#!/bin/bash

# Активуємо virtualenv
source /home/yoghurt/wifi-setup/venv/bin/activate

# Перевіряємо підключення Wi-Fi
nmcli -t -f WIFI g | grep enabled > /dev/null
nmcli -t -f STATE device show wlan0 | grep connected > /dev/null
if [ $? -eq 0 ]; then
    echo "Wi-Fi підключений, запускаємо Flask"
else
    echo "Wi-Fi не підключений, створюємо AP"
    nmcli device disconnect wlan0
    nmcli device wifi hotspot ifname wlan0 ssid orangepi-setup password orangepi123
fi

# Запускаємо Flask
/home/yoghurt/wifi-setup/venv/bin/python /home/yoghurt/wifi-setup/app.py
