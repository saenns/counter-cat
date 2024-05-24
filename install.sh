#!/bin/sh
mkdir -p ~/bin
python3 -m venv ~/counter-cat/venv
source ~/counter-cat/venv/bin/activate
cp src/counter-cat/*.py ~/bin/
chmod +x ~/bin/*.py
pip3 install RPi.GPIO
pip3 install discord.py
# pip3 install PyBluez
sudo cp ~/counter-cat/etc/systemd/system/countercat.service /etc/systemd/system/countercat.service
