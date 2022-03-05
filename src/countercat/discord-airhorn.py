#!/usr/bin/python3
# https://raspberrytips.com/make-a-discord-bot-on-pi/
"""
Simple BLE forever-scan example, that prints all the detected
LE advertisement packets, and prints a colored diff of data on data changes.
"""
import RPi.GPIO as GPIO
import asyncio
import discord
import sys
import time
import bluetooth._bluetooth as bluez
import logging

from collections import deque
from bluetooth_common import (toggle_device,
                             enable_le_scan, parse_le_advertising_events,parse_le_advertising_events_init,parse_le_advertising_events_once,
                             disable_le_scan, raw_packet_to_str)

logging.basicConfig(level='INFO')

pin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)

class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_task = self.loop.create_task(self.ble_loop())
        self.ch_ft = asyncio.Future()
        self.dq = deque()
        self.time_of_last_honk = time.time() - 50
        self.ch_ft = asyncio.Future()

    def blow_horn(self, secs):
        GPIO.output(pin, 1)
        time.sleep(secs)
        GPIO.output(pin, 0)
        self.time_of_last_honk = time.time()

    async def on_ready(self):
        self.ch = client.get_channel(929738879563612244)
        self.ch_ft.set_result(self.ch)
        await self.ch.send('honk when you\'re ready')

    async def on_message(self, message):
        ch = message.channel
        # don't respond to ourselves
        if message.author == self.user:
            return
        if message.bot:
            # lets double check to prevent false positives
            seconds_since_last_honk = time.time() - self.time_of_last_honk
            if len(self.dq) == lookback_window and self.avg_rssi >= -40 and seconds_since_last_honk > cooldown_seconds:
                logging.info('honking the horn')
                await self.ch.send('confirmed proximity rssi: %d' % self.avg_rssi)
            else:
                await self.ch.send('not close enough rssi: %d' % self.avg_rssi)
                return

        if message.content == 'ping':
            await ch.send('pong')
        if message.content == 'h1':
            blow_horn(0.1)
            await ch.send('0.1s')
        elif message.content == 'h2':
            blow_horn(0.25)
            await ch.send('0.25s')
        elif message.content == 'h3':
            blow_horn(0.5)
            await ch.send('0.5s')
        elif message.content == 'h4':
            blow_horn(1.0)
            await ch.send('1.0s')
        elif message.content == 'h5':
            blow_horn(2.0)
            await ch.send('2.0s')

    async def close(self):
        await self.ch.send('horn honker disconnecting')
        await super().close()

    async def on_disconnect(self):
        logging.info('cleaning up BLE')
        self.bg_task.cancel()
        try:
            await self.bg_task
        except asyncio.CancelledError:
            logging.exception('cancelled error')
        disable_le_scan(self.sock)

    async def ble_loop(self):
        try:
            await self.wait_until_ready()
            await self.ch_ft
            await self.ch.send('horn honker monitoring proximity')
            cooldown_seconds = 50

            dev_id = 0  # the bluetooth device is hci0
            toggle_device(dev_id, True)
            self.sock = bluez.hci_open_dev(dev_id)
            enable_le_scan(self.sock, filter_duplicates=False)
            parse_le_advertising_events_init(self.sock)
            while not self.is_closed():
                tpl =  parse_le_advertising_events_once(self.sock)
                if (tpl):
                    mac_addr_str, adv_type, rssi = tpl
                if mac_addr_str == '01:B6:EC:C6:44:9B':
                    self.dq.appendleft(rssi)
                    lookback_window = 2
                    if len(self.dq) > lookback_window:
                      self.dq.pop()
                    self.avg_rssi = sum(self.dq) / len(self.dq)
                    seconds_since_last_honk = time.time() - self.time_of_last_honk
                    logging.info('rssi: %d sslh %d' % (self.avg_rssi, seconds_since_last_honk))
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            logging.info("closing the BLE loop")
            return
        except:
            logging.exception("BLE loop failed")
            raise


client = MyClient()
client.run('OTQ2OTYyNTU4NjUxMzU5MzIy.YhmVmw.ifr8FNKD_wWz5BlBpINniZF1A8s')
