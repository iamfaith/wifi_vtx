####  wifi

gst-launch-1.0 uvch264src device=/dev/video0 initial-bitrate=6000000 average-bitrate=6000000 iframe-period=1000 name=src auto-start=true \
               src.vidsrc ! queue ! video/x-h264,width=1920,height=1080,framerate=30/1 ! h264parse ! rtph264pay ! udpsink host=localhost port=5600
To encode a Raspberry Pi Camera V2:

raspivid -n  -ex fixedfps -w 960 -h 540 -b 4000000 -fps 30 -vf -hf -t 0 -o - | \
               gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600
To decode:

 gst-launch-1.0 udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' \
               ! rtph264depay ! avdec_h264 ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false


# for PC  x264enc
gst-launch-1.0  filesrc location=a.mp4 ! decodebin ! videorate ! video/x-raw,framerate=30/1 ! videoscale ! video/x-raw,width=720,height=480 ! x264enc ! video/x-h264,framerate=30/1,profile=baseline ! rtph264pay ! udpsink host=127.0.0.1 port=5600



# for picar
# x264enc
gst-launch-1.0  filesrc location=a.mp4 ! decodebin ! videorate ! video/x-raw,framerate=30/1 ! videoscale ! video/x-raw,width=320,height=240 ! x264enc ! video/x-h264,framerate=30/1,profile=baseline ! rtph264pay ! udpsink host=192.168.31.226  port=5600

# omxh264enc
gst-launch-1.0  filesrc location=a.mp4 ! decodebin ! videorate ! video/x-raw,framerate=30/1 ! videoscale ! video/x-raw,width=720,height=480 ! omxh264enc ! video/x-h264,framerate=30/1,profile=high,target-bitrate=10000000  ! rtph264pay ! udpsink host=192.168.31.226  port=5600

# new.mp4
gst-launch-1.0  filesrc location=new.mp4 ! decodebin ! videorate ! video/x-raw,framerate=30/1 ! videoscale ! video/x-raw,width=320,height=240 ! omxh264enc ! video/x-h264,framerate=30/1,profile=baseline ! rtph264pay ! udpsink host=192.168.31.226  port=5600

# take photos
sudo raspistill -t 3000 -o 2.jpg


### h264
raspivid -n  -ex fixedfps -w 960 -h 540 -b 4000000 -fps 30 -vf -hf -t 0 -o - | \
               gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=192.168.31.226  port=5600


### h265
raspivid -n  -ex fixedfps -w 960 -h 540 -b 4000000 -fps 30 -vf -hf -t 0 -o - | \
               gst-launch-1.0 -v fdsrc ! h265parse ! rtph265pay config-interval=1 pt=35 ! udpsink sync=false host=192.168.31.226  port=5600


 gst-launch-1.0 udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H265' \
               ! rtph265depay ! avdec_h265 ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false


#### not used
gst-launch-1.0 v4l2src ! video/x-h264, width=960, height=540, framerate=30/1 ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=192.168.31.226  port=5600



TX: ./wfb_tx -p 3 -u 5600 -K drone.key -S 1 -L 1 -B 20 wlan0
RX: ./wfb_rx -c 192.168.31.226 -p 3 -u 5600 -K gs.key $rx




TX: ./wfb_tx -k 4 -n 8 -u 5600 -p 3 -M 4 -B 20 -K drone.key -f 2 wlan0mon
RX: ./wfb_rx -c 192.168.31.226 -p 3 -u 5600 -K gs.key -f 10 $rx



raspivid -n  -ex fixedfps -w 640 -h 320 -b 100000 -fps 30 -vf -hf -t 0 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600


raspivid -n  -ex fixedfps -w 640 -h 480 -b 100000 -fps 30 -vf -hf -t 0 -o - | gst-launch-1.0 -v fdsrc !  decodebin ! video/x-raw, width=640, height=480 ! progressreport name=progress ! omxh264enc target-bitrate=7500000 control-rate=variable ! video/x-h264, profile=baseline ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=192.168.31.226 port=5600




raspivid -n  -ex fixedfps -w 640 -h 480 -b 100000 -fps 30 -vf -hf -t 0 -o - | gst-launch-1.0 -v fdsrc !  decodebin ! omxh264enc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=192.168.31.226 port=5600



For test


gst-launch-1.0  filesrc location=a.mp4 ! decodebin ! videorate ! video/x-raw,framerate=30/1 ! videoscale ! video/x-raw,width=320,height=240 ! omxh264enc ! video/x-h264,framerate=30/1,profile=baseline ! rtph264pay ! udpsink host=127.0.0.1  port=5600




## vb
gst-launch-1.0  filesrc location=sora-293.mp4 ! decodebin ! videorate ! video/x-raw,framerate=30/1 ! videoscale ! video/x-raw,width=320,height=240 ! x264enc ! video/x-h264,framerate=30/1,profile=baseline ! rtph264pay ! udpsink host=0.0.0.0 port=5600


gst-launch-1.0  filesrc location=a.mp4 ! decodebin ! videorate ! video/x-raw,framerate=30/1 ! videoscale ! video/x-raw,width=960,height=540 ! omxh264enc ! video/x-h264,framerate=30/1,profile=high,target-bitrate=10000000 ! rtph264pay ! udpsink host=127.0.0.1 port=5600




    ffmpeg -hide_banner -nostats -i sora-293.mp4 -c:v mpeg2video -f mpegts - | mbuffer -q -c -m 20000k | ffmpeg -hide_banner -nostats -re -fflags +igndts -thread_queue_size 512 -i pipe:0 -fflags +genpts [proper codec setting] -f flv rtmp://0.0.0.0/live/stream




    gst-launch-1.0 host=35.241.102.213 port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' \
               ! rtph264depay ! avdec_h264 ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false





ffmpeg -f dshow -i video=a.mp4 -vcodec libx264 -tune zerolatency -b 900k -f mpegts udp://0.0.0.0:5600


ffmpeg  -i a.mp4 -vcodec libx264 -tune zerolatency -b 900k -f h264 udp://35.241.102.213:5600
ffplay -f h264 udp://35.241.102.213:5600

ffmpeg  -i a.mp4 -vcodec libx264 -tune zerolatency -b 900k -f h264 udp://127.0.0.1:5600
ffplay -f h264 udp://127.0.0.1:5600