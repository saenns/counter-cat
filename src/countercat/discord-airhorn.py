#!/usr/bin/python3
# https://raspberrytips.com/make-a-discord-bot-on-pi/
"""
Simple BLE forever-scan example, that prints all the detected
LE advertisement packets, and prints a colored diff of data on data changes.
"""
import argparse
import RPi.GPIO as GPIO
import asyncio
import discord
import sys
import time
import logging

from collections import deque

logging.basicConfig(level='INFO')

pin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)


class MyClient(discord.Client):

    def __init__(self, role, intents):
        super().__init__(*[], **{})
        self.bg_task = self.loop.create_task(self.ble_loop())
        self.ch = None
        self.ch_ft = asyncio.Future()
        self.dq = deque()
        self.time_of_last_honk = time.time() - 50
        self.ch_ft = asyncio.Future()
        self.role = role
        if role not in ['honker']:
            raise RuntimeError('unknown role ' + role)
        self.lookback_window = 2
        self.cooldown_seconds = 50
        self.armed = False

    async def blow_horn(self, message, secs):
        if message.author.bot:
            seconds_since_last_honk = time.time() - self.time_of_last_honk

        if self.armed:
            GPIO.output(pin, 1)
            time.sleep(secs)
            GPIO.output(pin, 0)
            self.time_of_last_honk = time.time()
            await self.ch.send('honked for %d secs rssi: ' % (secs, avg_rssi))
        else:
            await self.ch.send('no honk because disarmed')
            logging.info('no honk because disarmed')

    async def on_ready(self):
        self.ch = client.get_channel(929738879563612244)
        self.ch_ft.set_result(self.ch)
        await self.ch.send('honk when you\'re ready')

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        await self.common_on_message(message)
        if (self.role == 'honker'):
            await self.honker_on_message(message)

    def avg_rssi(self):
        if self.dq:
            return sum(self.dq) / len(self.dq)
        return -100000

    async def common_on_message(self, message):
        ch = message.channel
        if message.content in ['ping', 'Ping']:
            await ch.send('role: ' + self.role + ' pong')
        if message.content in ['stats', 'Stats']:
            await ch.send('role: ' + self.role + ' armed: ' + str(self.armed) + ' rssis: ' + ','.join(map(str, self.dq)) + ' avg: ' + str(self.avg_rssi()))

    async def honker_on_message(self, message):
        ch = message.channel
        if message.content in ['arm', 'Arm']:
            self.armed = True
            await self.ch.send('honker armed')
        if message.content in ['disarm', 'Disarm']:
            self.armed = False
            await self.ch.send('honker disarmed')
        if message.content in ['h1', 'H1']:
            await self.blow_horn(message, 0.1)
        elif message.content in ['h2', 'H2']:
            await self.blow_horn(message, 0.25)
        elif message.content in ['h3', 'H3']:
            await self.blow_horn(message, 0.5)
        elif message.content in ['h4', 'H4']:
            await self.blow_horn(message, 1.0)
        elif message.content in ['h5', 'H5']:
            await self.blow_horn(message, 2.0)

    async def close(self):
        await self.ch.send('horn honker disconnecting')
        logging.info('cleaning up BLE')
        self.bg_task.cancel()
        try:
            await self.bg_task
        except asyncio.CancelledError:
            logging.exception('cancelled error')
        disable_le_scan(self.sock)
        await super().close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord chatbot to monitor proximity and operate the air horn remotely')
    parser.add_argument('--role', type=str, choices=['honker'], help='whether to act as remote proximity sensor or the horn operator')
    parser.add_argument('--token', type=str, required=True, help='Discord bot token')
    args = parser.parse_args()
    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(args.role, intents=intents)
    client.run(args.token)
