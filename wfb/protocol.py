from twisted.internet.protocol import ProcessProtocol, Protocol, Factory
from twisted.python import log
from twisted.internet import reactor, defer
import json
from itertools import groupby
from twisted.protocols.basic import LineReceiver


class WFBFlags(object):
    LINK_LOST = 1
    LINK_JAMMED = 2


class StatisticsProtocol(Protocol):
    def connectionMade(self):
        self.factory.sessions.append(self)

    def dataReceived(self, data):
        pass

    def connectionLost(self, reason):
        self.factory.sessions.remove(self)

    def send_stats(self, data):
        self.transport.write(json.dumps(data).encode('utf-8') + b'\n')


class AntennaFactory(Factory):
    noisy = False
    protocol = StatisticsProtocol

    def __init__(self, p_in, p_tx_l):
        self.p_in = p_in
        self.p_tx_l = p_tx_l
        self.tx_sel = 0
        self.tx_sel_delta = 0  # settings.common.tx_sel_delta

        # Select antenna #0 by default
        if p_in is not None and p_tx_l is not None:
            p_in.peer = p_tx_l[0]

        # tcp sockets for UI
        self.sessions = []

    def select_tx_antenna(self, ant_rssi):
        wlan_rssi = {}
        for k, grp in groupby(sorted(((int(ant_id, 16) >> 8) & 0xff, rssi_avg)
                                     for ant_id, (pkt_s, rssi_min, rssi_avg, rssi_max) in ant_rssi.items()),
                              lambda x: x[0]):
            # Select max average rssi from all wlan's antennas
            wlan_rssi[k] = max(rssi for _, rssi in grp)

        tx_max = None
        for k, v in wlan_rssi.items():
            if tx_max is None or k != tx_max and v > wlan_rssi[tx_max]:
                tx_max = k

        if tx_max is None or wlan_rssi[tx_max] <= wlan_rssi.get(self.tx_sel, -200) + self.tx_sel_delta:
            return

        log.msg('Swith TX antenna from %d to %d' % (self.tx_sel, tx_max))
        self.tx_sel = tx_max
        self.p_in.peer = self.p_tx_l[tx_max]

    def update_stats(self, rx_id, packet_stats, ant_rssi):
        mav_rssi = []
        flags = 0

        for i, (k, v) in enumerate(sorted(ant_rssi.items())):
            pkt_s, rssi_min, rssi_avg, rssi_max = v
            mav_rssi.append(rssi_avg)

        rssi = (max(mav_rssi) if mav_rssi else -128) % 256

        if not mav_rssi:
            flags |= WFBFlags.LINK_LOST
        elif packet_stats['dec_ok'] == 0:
            flags |= WFBFlags.LINK_JAMMED

        if self.p_in:
            if ant_rssi:
                self.select_tx_antenna(ant_rssi)
            # Send mavlink packet with radio rssi
            rx_errors = min(
                packet_stats['dec_err'][0] + packet_stats['bad'][0] + packet_stats['lost'][0], 65535)
            rx_fec = min(packet_stats['fec_rec'][0], 65535)
            self.p_in.send_rssi(rssi, rx_errors, rx_fec, flags)

        # if settings.common.debug:
        #     log.msg('%s rssi %s tx#%d %s %s' % (rx_id, max(mav_rssi) if mav_rssi else 'N/A', self.tx_sel, packet_stats, ant_rssi))

        for s in self.sessions:
            s.send_stats(dict(id=rx_id, tx_ant=self.tx_sel,
                              packets=packet_stats, rssi=ant_rssi))


class BadTelemetry(Exception):
    pass


class AntennaProtocol(LineReceiver):
    delimiter = b'\n'

    def __init__(self, antenna_f, rx_id):
        self.antenna_f = antenna_f
        self.rx_id = rx_id
        self.ant = {}
        self.count_all = None

    def lineReceived(self, line):
        cols = line.decode('utf-8').strip().split('\t')
        try:
            if len(cols) < 2:
                raise BadTelemetry()

            #ts = int(cols[0])
            cmd = cols[1]

            if cmd == 'ANT':
                if len(cols) != 4:
                    raise BadTelemetry()
                self.ant[cols[2]] = tuple(int(i) for i in cols[3].split(':'))
            elif cmd == 'PKT':
                if len(cols) != 3:
                    raise BadTelemetry()

                p_all, p_dec_err, p_dec_ok, p_fec_rec, p_lost, p_bad = list(
                    int(i) for i in cols[2].split(':'))

                if not self.count_all:
                    self.count_all = (p_all, p_dec_ok, p_fec_rec,
                                      p_lost, p_dec_err, p_bad)
                else:
                    self.count_all = tuple(
                        (a + b) for a, b in zip((p_all, p_dec_ok, p_fec_rec, p_lost, p_dec_err, p_bad), self.count_all))

                stats = dict(zip(('all', 'dec_ok', 'fec_rec', 'lost', 'dec_err', 'bad'),
                                 zip((p_all, p_dec_ok, p_fec_rec, p_lost, p_dec_err, p_bad),
                                     self.count_all)))

                self.antenna_f.update_stats(self.rx_id, stats, dict(self.ant))
                self.ant.clear()
            else:
                raise BadTelemetry()
        except BadTelemetry:
            log.msg('Bad telemetry [%s]: %s' % (self.rx_id, line), isError=1)


class DbgProtocol(LineReceiver):
    delimiter = b'\n'

    def __init__(self, rx_id):
        self.rx_id = rx_id

    def lineReceived(self, line):
        log.msg('%s: %s' % (self.rx_id, line.decode('utf-8')))


class RXProtocol(ProcessProtocol):
    def __init__(self, antenna_stat, cmd, rx_id):
        self.cmd = cmd
        self.rx_id = rx_id
        self.ant = AntennaProtocol(antenna_stat, rx_id)
        self.dbg = DbgProtocol(rx_id)
        self.df = defer.Deferred()

    def connectionMade(self):
        log.msg('Started %s' % (self.rx_id,))

    def outReceived(self, data):
        self.ant.dataReceived(data)

    def errReceived(self, data):
        self.dbg.dataReceived(data)

    def processEnded(self, status):
        rc = status.value.exitCode
        log.msg('Stopped RX %s with code %s' % (self.rx_id, rc))

        # if rc == 0:
        #     self.df.callback(str(status.value))
        # else:
        #     self.df.errback(status)

    def processExited(self, reason):
        print("process exited!")
        defer.maybeDeferred(reactor.spawnProcess, self, self.cmd[0], self.cmd, env=None,
                                 childFDs={0: "w", 1: "r", 2: "r"})

    def start(self):
        df = defer.maybeDeferred(reactor.spawnProcess, self, self.cmd[0], self.cmd, env=None, childFDs={
                                 0: "w", 1: "r", 2: "r"})
        return df.addCallback(lambda _: self.df)


class TXProtocol(ProcessProtocol):
    def __init__(self, cmd, tx_id):
        self.cmd = cmd
        self.tx_id = tx_id
        self.dbg = DbgProtocol(tx_id)
        self.df = defer.Deferred()

    def connectionMade(self):
        log.msg('Started %s' % (self.tx_id,))

    def outReceived(self, data):
        self.dbg.dataReceived(data)

    def errReceived(self, data):
        self.dbg.dataReceived(data)

    def processExited(self, reason):
        print("process exited!")
        defer.maybeDeferred(reactor.spawnProcess, self, self.cmd[0], self.cmd, env=None,
                                 childFDs={0: "w", 1: "r", 2: "r"})


    def processEnded(self, status):
        rc = status.value.exitCode
        log.msg('Stopped TX %s with code %s' % (self.tx_id, rc))

        # if rc == 0:
        #     self.df.callback(str(status.value))
        # else:
        #     self.df.errback(status)

    def start(self):
        df = defer.maybeDeferred(reactor.spawnProcess, self, self.cmd[0], self.cmd, env=None,
                                 childFDs={0: "w", 1: "r", 2: "r"})
        return df.addCallback(lambda _: self.df)
