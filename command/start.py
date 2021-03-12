import sys
import os
import subprocess
from twisted.internet import reactor, defer, utils
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.error import ReactorNotRunning
from protocol import TXProtocol

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
        cmd = f"ps -ef|grep -v grep|grep {exec}" + "|awk '{print $2}'|xargs kill -9"
        print(cmd)
        subprocess.check_output(cmd, shell=True, text=True)
    except Exception:
        pass


def quit(wlan):
    kill_wfb('wfb_tx')
    kill_wfb('wfb_rx')
    set_mode(wlan, managed_mode)
    show_info(wlan)
    kill_wfb('wfb_tx')
    kill_wfb('wfb_rx')
    # reactor.removeAll()
    # reactor.iterate()
    # reactor.stop()


def init_tx(wlan):
    cmd = "wfb_tx {}".format(wlan).split()
    df = TXProtocol(cmd, 'video tx').start()
    return df


def init(wlan):
    def _init_services(_):
        return defer.gatherResults([defer.maybeDeferred(init_tx, wlan)])\
                    .addErrback(lambda f: f.trap(defer.FirstError) and f.value.subFailure)
    return init_wlan(wlan).addCallback(_init_services)


def main():
    kill_wfb('wfb_tx')
    kill_wfb('wfb_rx')
    wlan = subprocess.check_output(get_wlans, shell=True, text=True)
    wlan = wlan.strip()
    log.startLogging(sys.stdout)
    reactor.callWhenRunning(lambda: defer.maybeDeferred(
        init, wlan).addErrback(abort_on_crash))
    reactor.addSystemEventTrigger('during', 'shutdown', quit, wlan)
    reactor.run()
    kill_wfb('wfb_tx')
    kill_wfb('wfb_rx')
    # rc = exit_status()
    # log.msg('Exiting with code %d' % rc)
    # sys.exit(rc)


def test_main():
    wlans = subprocess.check_output(get_wlans, shell=True, text=True)
    wlans = wlans.strip()
    print(wlans)

    set_mode(wlans, managed_mode)
    show_info(wlans)
    # set_mode(wlans, monitor_mode)


if __name__ == '__main__':
    main()
