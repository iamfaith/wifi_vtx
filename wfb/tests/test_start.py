# def main():
#     kill_wfb('wfb_tx')
#     kill_wfb('wfb_rx')
#     wlan = subprocess.check_output(get_wlans, shell=True, text=True)
#     wlan = wlan.strip()
#     log.startLogging(sys.stdout)
#     reactor.callWhenRunning(lambda: defer.maybeDeferred(
#         init, wlan).addErrback(abort_on_crash))
#     reactor.addSystemEventTrigger('during', 'shutdown', quit, wlan)
#     reactor.run()
#     kill_wfb('wfb_tx')
#     kill_wfb('wfb_rx')
    # rc = exit_status()
    # log.msg('Exiting with code %d' % rc)
    # sys.exit(rc)

# def test_main():
#     wlans = subprocess.check_output(get_wlans, shell=True, text=True)
#     wlans = wlans.strip()
#     print(wlans)

#     set_mode(wlans, managed_mode)
#     show_info(wlans)
    # set_mode(wlans, monitor_mode)


# if __name__ == '__main__':
#     main()