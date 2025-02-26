#!/bin/sh
sudo pip3 install inputs python-can
sudo cp ./controller.service /etc/systemd/system
sudo systemctl daemon-reload
sudo cp ./controller.rules /etc/udev/rules.d/
sudo cp ./controller.py ./controller.sh /opt
sudo udevadm control --reload-rules
