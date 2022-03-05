#!/usr/bin/python3
# https://raspberrytips.com/make-a-discord-bot-on-pi/
import discord
import RPi.GPIO as GPIO
import time

pin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)

def blow_horn(secs):
    GPIO.output(pin, 1)
    time.sleep(secs)
    GPIO.output(pin, 0)

class MyClient(discord.Client):
    async def on_ready(self):
        ch = client.get_channel(929738879563612244)
        await ch.send('honk when you\'re ready')

    async def on_message(self, message):
        ch = message.channel
        # don't respond to ourselves
        if message.author == self.user:
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

client = MyClient()
client.run('OTQ2OTYyNTU4NjUxMzU5MzIy.YhmVmw.ifr8FNKD_wWz5BlBpINniZF1A8s')
