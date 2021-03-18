
ps -ef|grep -v grep|grep wfb|awk '{print $2}'|xargs kill -9

sudo wfb tx -w wlan1 --nogst