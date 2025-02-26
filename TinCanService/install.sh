#!/bin/sh
sudo cp ./tinCan.service /etc/systemd/system
sudo systemctl daemon-reload
sudo cp ./tinCan.rules /etc/udev/rules.d/
sudo cp ./tinSocketCan.sh /opt
sudo udevadm control --reload-rules
