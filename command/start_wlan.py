import sys
import subprocess

get_wlans = " iw dev | awk '$1==\"Interface\"{print $2}'"
down_wlan = 'ip link set {} down'
up_wlan = 'ip link set {} up'
set_wlan = 'iw dev {} set {}'
power_wlan = 'iw {} set txpower fixed {}'
info_wlan = 'iw {} info'
channel_wlan = 'iwconfig {} channel {}'

monitor_mode = 'monitor otherbss fcsfail'
managed_mode = 'type managed'


def switch_channel(wlan, channel):
    subprocess.check_output(channel_wlan.format(wlan, channel), shell=True, text=True)

def show_info(wlan):
    info = subprocess.check_output(info_wlan.format(wlan), shell=True, text=True)
    print(info)
    return info

def set_mode(wlan, mode):
    subprocess.check_output(down_wlan.format(wlan), shell=True, text=True)
    subprocess.check_output(set_wlan.format(wlan, mode), shell=True, text=True)
    subprocess.check_output(up_wlan.format(wlan), shell=True, text=True)
    try:
        if mode == managed_mode:
            subprocess.check_output(power_wlan.format(wlan, '2000'), shell=True, text=True)
        else:
            subprocess.check_output(power_wlan.format(wlan, '3000'), shell=True, text=True)
    except Exception as e:
        print(e)
        

def main():
    wlans = subprocess.check_output(get_wlans, shell=True, text=True)
    wlans = wlans.strip()
    print(wlans)

    set_mode(wlans, managed_mode)
    show_info(wlans)
    # set_mode(wlans, monitor_mode)


main()