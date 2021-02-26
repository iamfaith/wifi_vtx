# stopwatch

https://naozhong.net.cn/miaobiao/


# wlan

ifconfig wlan1 down
iw dev wlan1 set monitor otherbss fcsfail
ifconfig wlan1 up

iwconfig wlan1 channel 13

# RX

./wfb_rx    -c 10.0.2.2 -p 3 -u 5600 -K gs.key  wlan0mon

./wfb_rx    -c 127.0.0.1 -p 3 -u 5600 -K gs.key  $rx

# TX

## test video
gst-launch-1.0  filesrc location=a.mp4 ! decodebin ! videorate ! video/x-raw,framerate=30/1 ! videoscale ! video/x-raw,width=960,height=540 ! omxh264enc ! video/x-h264,framerate=30/1,profile=high,target-bitrate=10000000 ! rtph264pay ! udpsink host=127.0.0.1 port=5600

## camera

raspivid -n  -ex fixedfps -w 960 -h 540 -b 1000000 -fps 40 -vf -hf -t 0 -o - | \
               gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600

# 480 P
raspivid -n  -ex fixedfps -w 720 -h 480 -b 2000000 -fps 50 -vf -hf -t 0 -o - | \
               gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600

# not good
raspivid -n  -ex fixedfps -w 640 -h 480 -b 1000000 -fps 60 -vf -hf -t 0 -o - | \
               gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600

# dynamic bitrate not good
raspivid -n  -ex fixedfps -w 720 -h 480 -b 0 -qp 40 -fps 50 -vf -hf -t 0 -o - |                gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600


// ./wfb_tx  -p 3 -u 5600 -K drone.key -S 1 -L 1 -B 20 wlan1mon

./wfb_tx  -p 3 -u 5600 -K drone.key -S 1 -L 1 -B 20 wlan1

> -e for encryption


# mac
```
 gst-launch-1.0 udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' \
               ! rtph264depay ! avdec_h264 ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false

export LIBVA_DRIVER_NAME=i965

 gst-launch-1.0 udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' \
               ! rtph264depay ! vaapih264dec ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false
```
# ffmpeg

ffmpeg  -i a.mp4 -vcodec libx264 -tune zerolatency -b 900k -f h264 udp://35.241.102.213:5600
ffplay -f h264 udp://35.241.102.213:5600


## with frp
[common]
server_addr = vless.faithio.cn
server_port = 7000

[ssh]
type = udp
local_ip = 127.0.0.1
local_port = 5600
remote_port = 5600

ffmpeg  -i a.mp4 -vcodec libx264 -tune zerolatency -b 900k -f h264 udp://127.0.0.1:5600
ffplay -f h264 udp://127.0.0.1:5600