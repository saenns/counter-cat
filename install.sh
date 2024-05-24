#!/bin/sh
mkdir -p ~/bin
cp src/countercat/*.py ~/bin/
chmod +x ~/bin/*.py
pip3 install RPi.GPIO
pip3 install discord.py
pip3 install PyBluez
