# RX

./wfb_rx    -c 10.0.2.2 -p 3 -u 5600 -K gs.key  wlan0mon


# TX

## test video
gst-launch-1.0  filesrc location=a.mp4 ! decodebin ! videorate ! video/x-raw,framerate=30/1 ! videoscale ! video/x-raw,width=960,height=540 ! omxh264enc ! video/x-h264,framerate=30/1,profile=high,target-bitrate=10000000 ! rtph264pay ! udpsink host=127.0.0.1 port=5600

## camera

raspivid -n  -ex fixedfps -w 960 -h 540 -b 4000000 -fps 30 -vf -hf -t 0 -o - | \
               gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600



./wfb_tx  -p 3 -u 5600 -K drone.key -S 1 -L 1 -B 20 wlan1mon


> -e for encryption


# mac

 gst-launch-1.0 udpsrc port=5600 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' \
               ! rtph264depay ! avdec_h264 ! clockoverlay valignment=bottom ! autovideosink fps-update-interval=1000 sync=false