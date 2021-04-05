ifconfig wlan1 down
iw dev wlan1 set monitor otherbss fcsfail
ifconfig wlan1 up
iwconfig wlan1 channel 13


ifconfig wlan2 down
iw dev wlan2 set monitor otherbss fcsfail
ifconfig wlan2 up
iwconfig wlan2 channel 13