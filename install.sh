#!/bin/sh
mkdir -p ~/bin
python3 -m venv ~/countercat/venv
source ~/countercat/venv/bin/activate
cp src/countercat/*.py ~/bin/
chmod +x ~/bin/*.py
pip3 install RPi.GPIO
pip3 install discord.py
# pip3 install PyBluez
cp ~/countercat/etc/systemd/system/countercat.service /etc/systemd/system/countercat.service
