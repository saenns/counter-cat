#!/bin/sh
mkdir -p ~/bin
cp src/countercat/*.py ~/bin/
chmod +x ~/bin/*.py
sudo pip3 install RPi.GPIO
sudo pip3 install discord.py
sudo pip3 install PyBluez
