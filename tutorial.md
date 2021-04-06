pip install stem stdeb3 setuptools future

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
gst-launch-1.0  filesrc location=a.mp4 ! decodebin ! videorate ! video/x-raw,framerate=30/1 ! videoscale ! video/x-raw,width=1920,height=1080 ! omxh264enc ! video/x-h264,framerate=60/1,profile=high,target-bitrate=40000000 ! rtph264pay ! udpsink host=192.168.31.176 port=5600

gst-launch-1.0  filesrc location=a.mp4 ! decodebin ! x264enc ! video/x-h264,framerate=60/1,profile=high,target-bitrate=40000000 ! rtph264pay ! udpsink host=192.168.31.176 port=5600

## camera

raspivid -n  -ex fixedfps -w 960 -h 540 -b 1000000 -fps 40 -vf -hf -t 0 -o - | \
               gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600

### pf baseline  qp 23
raspivid -n -pf baseline -ex fixedfps -w 640 -h 480 -qp 23 -fps 60 -vf -hf -t 0 -o - | \
               gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=192.168.31.226 port=5600

### 480P@60FPS
raspivid -n  -pf baseline -ex fixedfps -w 640 -h 480 -b 1000000 -fps 60 -vf -hf -t 0 -o - | \
               gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=192.168.31.226 port=5600


### 1296@qp30
raspivid -n  -ex fixedfps -w 1296 -h 730 -b 0 -qp 30 -fps 49 -vf -hf -t 0 -o - |                gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=192.168.31.226 port=5600

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

./wfb_tx  -p 3 -u 5600 -K drone.key  wlan1

# mac
```
 gst-launch-1.0 udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' \
               ! rtph264depay ! avdec_h264 ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false

 gst-launch-1.0 udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' \
               ! rtph264depay ! omxh264dec ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false



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







https://picamera.readthedocs.io/en/release-1.13/fov.html

#	Resolution	Aspect Ratio	Framerates	Video	Image	FoV	Binning
1	1920x1080	16:9	1 < fps <= 30	x	 	Partial	None
2	2592x1944	4:3	1 < fps <= 15	x	x	Full	None
3	2592x1944	4:3	1/6 <= fps <= 1	x	x	Full	None
4	1296x972	4:3	1 < fps <= 42	x	 	Full	2x2
5	1296x730	16:9	1 < fps <= 49	x	 	Full	2x2
6	640x480	4:3	42 < fps <= 60	x	 	Full	4x4
7	640x480	4:3	60 < fps <= 90	x	 	Full	4x4
On the V2 module, these are:

#	Resolution	Aspect Ratio	Framerates	Video	Image	FoV	Binning
1	1920x1080	16:9	1/10 <= fps <= 30	x	 	Partial	None
2	3280x2464	4:3	1/10 <= fps <= 15	x	x	Full	None
3	3280x2464	4:3	1/10 <= fps <= 15	x	x	Full	None
4	1640x1232	4:3	1/10 <= fps <= 40	x	 	Full	2x2
5	1640x922	16:9	1/10 <= fps <= 40	x	 	Full	2x2
6	1280x720	16:9	40 < fps <= 90	x	 	Partial	2x2
7	640x480	4:3	40 < fps <= 90	x	 	Partial	2x2




 gst-launch-1.0 udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' \
               ! rtph264depay ! avdec_h264_mmal ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false


gst-launch-1.0 udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' \
               ! rtph264depay ! avdec_h264 ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false



gst-launch-1.0 videotestsrc ! autovideosink

gst-launch-1.0 videotestsrc ! omxh264enc ! "video/x-h264,profile=high" ! h264parse ! matroskamux ! filesink location=output.avi