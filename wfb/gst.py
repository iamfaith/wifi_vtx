import subprocess
import os
from enum import Enum
import threading
import time
# https://www.raspberrypi.org/documentation/hardware/camera/


class GstCmd(Enum):
    # 640 * 480
    P480 = ("raspivid -n  -pf baseline -ex sports -w 640 -h 480 -b 1000000 -fps 90 -vf -hf -t 0 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600", "raspivid")
    # 1280 * 720
    P720 = ("raspivid -n  -pf baseline -ex sports -w 1280 -h 720 -b 1000000 -fps 60 -vf -hf -t 0 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600", "raspivid")
    P1080 = ("raspivid -n  -pf baseline -ex sports -w 1920 -h 1080 -b 1000000 -fps 30 -vf -hf -t 0 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600", "raspivid")

    GROUND_GST = ("export LIBVA_DRIVER_NAME=i965 && gst-launch-1.0 udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' ! rtph264depay ! avdec_h264 ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false", "gst-launch-1.0")

    def cmd(self):
        return self.value[0]

    def monitor(self):
        return self.value[1]


# exposure fixedfps --> sports
# opt 1
# raspivid -n  -pf baseline -ex sports -w 960 -h 540 -b 1000000 -fps 90 -vf -hf -t 0 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600

# opt 2
# faster
# raspivid -n  -pf baseline -ex sports -w 640 -h 480 -b 1000000 -fps 90 -vf -hf -t 0 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600

def run_cmd(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid)


class Monitor(threading.Thread):

    def __init__(self, gst_cmd=GstCmd.GROUND_GST):
        super().__init__()
        self.cmd = gst_cmd.cmd()
        self.monitor_obj = gst_cmd.monitor()
        self.kill_cmd = "ps -ef|grep " + self.monitor_obj + \
            "|grep -v grep|awk '{print $2}'|xargs kill -9"
        self.check_cmd = "ps -ef|grep " + self.monitor_obj + \
            "|grep -v grep|awk '{print $2}'"

    def kill_monitor(self):
        run_cmd(self.kill_cmd)

    def run(self):
        self.kill_monitor()
        # start
        run_cmd(self.cmd)
        while True:
            try:
                pids = subprocess.check_output(
                    self.check_cmd, shell=True, text=True)
                if pids.strip() == '':
                    print('no pids, restart service')
                    run_cmd(self.cmd)
            except Exception as e:
                pass
            # else:
            #     print(pids)
            time.sleep(0.5)


if __name__ == "__main__":
    # print(GstCmd.GROUND_GST.cmd(), GstCmd.GROUND_GST.monitor())
    monitor = Monitor(gst_cmd=GstCmd.GROUND_GST)
    monitor.kill_monitor()
    # monitor.setDaemon(True)
    # monitor.start()
    # monitor.join()
