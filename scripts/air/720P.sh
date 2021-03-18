#! /bin/sh

ps -ef|grep -v grep|grep raspivid|awk '{print $2}'|xargs kill -9

raspivid -n  -pf baseline -ex sports -w 1280 -h 720 -b 4000000 -fps 60 -vf -hf -t 0 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=35 ! udpsink sync=false host=127.0.0.1 port=5600