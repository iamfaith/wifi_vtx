import sys
import os
import subprocess
from twisted.internet import reactor, defer, utils
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.error import ReactorNotRunning
from wfb.protocol import TXProtocol, RXProtocol, AntennaFactory
from typing import List
from wfb import register, cmd
import argparse
from wfb import GstCmd, Monitor

get_wlans = " iw dev | awk '$1==\"Interface\"{print $2}'"
down_wlan = 'ip link set {} down'
up_wlan = 'ip link set {} up'
set_wlan = 'iw dev {} set {}'
power_wlan = 'iw dev {} set txpower fixed {}'
info_wlan = 'iw {} info'
channel_wlan = 'iwconfig {} channel {}'
channel_wlan = 'iw dev {} set channel {}'

kill_cmd = "ps -ef|grep -v grep|grep {}|awk '{print $2}'|xargs kill -9"

monitor_mode = 'monitor otherbss fcsfail'
managed_mode = 'type managed'


def switch_channel(wlan, channel):
    subprocess.check_output(channel_wlan.format(
        wlan, channel), shell=True, text=True)


def show_info(wlan):
    info = subprocess.check_output(
        info_wlan.format(wlan), shell=True, text=True)
    print(info)
    return info


def set_mode(wlan, mode):
    subprocess.check_output(down_wlan.format(wlan), shell=True, text=True)
    subprocess.check_output(set_wlan.format(wlan, mode), shell=True, text=True)
    subprocess.check_output(up_wlan.format(wlan), shell=True, text=True)
    try:
        if mode == managed_mode:
            subprocess.check_output(power_wlan.format(
                wlan, '2000'), shell=True, text=True)
        else:
            subprocess.check_output(power_wlan.format(
                wlan, '3000'), shell=True, text=True)
    except Exception as e:
        print(e)


ht_mode = 'HT20'


class ExecError(Exception):
    pass


def call_and_check_rc(cmd, *args):
    def _check_rc(_args):
        (stdout, stderr, rc) = _args
        if rc != 0:
            err = ExecError('RC %d: %s %s' % (rc, cmd, ' '.join(args)))
            err.stdout = stdout.strip()
            err.stderr = stderr.strip()
            raise err

        log.msg('# %s' % (' '.join((cmd,) + args),))
        if stdout:
            log.msg(stdout)

    def _got_signal(f):
        f.trap(tuple)
        stdout, stderr, signum = f.value
        err = ExecError('Got signal %d: %s %s' % (signum, cmd, ' '.join(args)))
        err.stdout = stdout.strip()
        err.stderr = stderr.strip()
        raise err

    return utils.getProcessOutputAndValue(cmd, args, env=os.environ).addCallbacks(_check_rc, _got_signal)


@defer.inlineCallbacks
def init_wlan(wlan):
    yield call_and_check_rc('ifconfig', wlan, 'down')
    yield call_and_check_rc('iw', 'dev', wlan, 'set', 'monitor', 'otherbss', 'fcsfail')
    yield call_and_check_rc('ifconfig', wlan, 'up')
    yield call_and_check_rc('iw', 'dev', wlan, 'set', 'channel', '13', ht_mode)
    # yield call_and_check_rc('iwconfig', wlan, 'channel', '13')


def abort_on_crash(f):

    log.err(f, 'receive an error on reactor')
    # try:
    #     reactor.removeAll()
    #     reactor.iterate()
    #     reactor.stop()
    # except ReactorNotRunning:
    #     pass


def kill_wfb(exec):
    try:
        kill_cmd = f"ps -ef|grep -v grep|grep {exec}" + \
            "|awk '{print $2}'|xargs kill -9"
        check_cmd = f"ps -ef|grep -v grep|grep {exec}" + \
            "|awk '{print $2}'"
        pids = subprocess.check_output(check_cmd, shell=True, text=True)
        if pids.strip() != '':
            subprocess.check_output(kill_cmd, shell=True, text=True, stderr=None)
    except Exception:
        pass


def quit(wlan, cb=None):
    kill_wfb('wfb_tx')
    kill_wfb('wfb_rx')
    set_mode(wlan, managed_mode)
    show_info(wlan)
    kill_wfb('wfb_tx')
    kill_wfb('wfb_rx')
    if cb is not None:
        cb()
    # reactor.removeAll()
    # reactor.iterate()
    # reactor.stop()


def init_tx(wlan):
    cmd = "wfb_tx {}".format(wlan).split()
    df = TXProtocol(cmd, 'video tx').start()
    return df


def init_rx(wlan):
    ant_f = AntennaFactory(None, None)
        # if cfg.stats_port:
        #     reactor.listenTCP(cfg.stats_port, ant_f
    cmd = "wfb_rx {}".format(wlan).split()
    df = RXProtocol(ant_f, cmd, 'video rx').start()
    return df


def init_tx_service(wlan):
    def _init_services(_):
        return defer.gatherResults([defer.maybeDeferred(init_tx, wlan)])\
                    .addErrback(lambda f: f.trap(defer.FirstError) and f.value.subFailure)
    return init_wlan(wlan).addCallback(_init_services)


def init_rx_service(wlan):
    def _init_services(_):
        return defer.gatherResults([defer.maybeDeferred(init_rx, wlan)])\
                    .addErrback(lambda f: f.trap(defer.FirstError) and f.value.subFailure)
    return init_wlan(wlan).addCallback(_init_services)


class Base:

    def init_parameter(self, argv: List, gst_cmd=GstCmd.P480):
        self.args = self.parser.parse_args(argv)
        if self.args.nogst == False:
            self.monitor = Monitor(gst_cmd)
            # def cb():
            #     self.monitor.kill_monitor()
            self.monitor.setDaemon(True)
            self.monitor.start()
        else:
            self.monitor = None

        if self.args.wlan is None or self.args.wlan == "":
            self.wlan = subprocess.check_output(
                get_wlans, shell=True, text=True)
            self.wlan = self.wlan.strip()

        else:
            self.wlan = self.args.wlan
        print(f'wlan:{self.wlan}')
        if self.args.verbose:
            log.startLogging(sys.stdout)

    def after_execute(self):
        if self.monitor is not None:
            self.monitor.kill_monitor()


@register(name='{}.tx'.format(cmd), description='start tx')
class TX(Base):

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description=self.__class__.__doc__, prog='{} tx'.format(cmd), usage='%(prog)s', add_help=True)
        self.parser.add_argument('--wlan', '-w', required=False, help='wlans')
        self.parser.add_argument('--verbose', '-v', required=False,
                                 action="store_true", default=False, help='verbose mode, print output')
        self.parser.add_argument('--nogst', required=False,
                                 action="store_true", default=False, help='do not start gst')
        

    def execute(self, argv: List) -> bool:
        self.init_parameter(argv, GstCmd.P480)
        kill_wfb('wfb_tx')
        reactor.callWhenRunning(lambda: defer.maybeDeferred(
            init_tx_service, self.wlan).addErrback(abort_on_crash))
        reactor.addSystemEventTrigger('during', 'shutdown', quit, self.wlan)
        reactor.run()
        kill_wfb('wfb_tx')
        self.after_execute()


@register(name='{}.rx'.format(cmd), description='start rx')
class RX(Base):
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description=self.__class__.__doc__, prog='{} rx'.format(cmd), usage='%(prog)s', add_help=True)
        self.parser.add_argument('--wlan', '-w', required=False, help='wlans')
        self.parser.add_argument('--verbose', '-v', required=False,
                                 action="store_true", default=False, help='verbose mode, print output')
        self.parser.add_argument('--nogst', required=False,
                                 action="store_true", default=False, help='do not start gst')

    def execute(self, argv: List) -> bool:
        self.init_parameter(argv, GstCmd.GROUND_GST)
        
        kill_wfb('wfb_rx')
        reactor.callWhenRunning(lambda: defer.maybeDeferred(
            init_rx_service, self.wlan).addErrback(abort_on_crash))
        reactor.addSystemEventTrigger(
            'during', 'shutdown', quit, self.wlan)
        reactor.run()
        kill_wfb('wfb_rx')
        self.after_execute() 
