#!/usr/bin/python3
# https://raspberrytips.com/make-a-discord-bot-on-pi/
"""
Simple BLE forever-scan example, that prints all the detected
LE advertisement packets, and prints a colored diff of data on data changes.
"""
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

class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_task = self.loop.create_task(self.ble_loop())
        self.ch_ft = asyncio.Future()

    async def on_ready(self):
        self.ch =client.get_channel(929738879563612244)
        self.ch_ft.set_result(self.ch)

    async def close(self):
        await self.ch.send('proximity sensor disconnecting')
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
            await self.ch.send('monitoring proximity')
            cooldown_seconds = 50
            time_of_last_honk = time.time()-cooldown_seconds

            dev_id = 0  # the bluetooth device is hci0
            toggle_device(dev_id, True)
            self.sock = bluez.hci_open_dev(dev_id)
            enable_le_scan(self.sock, filter_duplicates=False)
            parse_le_advertising_events_init(self.sock)
            dq = deque()
            while not self.is_closed():
                tpl =  parse_le_advertising_events_once(self.sock)
                if (tpl):
                    mac_addr_str, adv_type, rssi = tpl
                if mac_addr_str == '01:B6:EC:C6:44:9B':
                    dq.appendleft(rssi)
                    lookback_window = 2
                    if len(dq) > lookback_window:
                      dq.pop()
                    avg_rssi = sum(dq) / len(dq)
                    seconds_since_last_honk = time.time() - time_of_last_honk
                    logging.info('rssi: %d sslh %d' % (avg_rssi, seconds_since_last_honk))
                    if len(dq) == lookback_window and avg_rssi >= -40 and seconds_since_last_honk > cooldown_seconds:
                        logging.info('honking the horn')
                        await self.ch.send('rssi: %d' % avg_rssi)
                        time_of_last_honk = time.time()
                        await self.ch.send('h4')
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            logging.info("closing the BLE loop")
            return
        except:
            logging.exception("BLE loop failed")
            raise


client = MyClient()
client.run('OTQ4NzQxNDcxMTAyNzEzODg2.YiAOWQ.bUx-lXD5efKNq_9E_9MSCVNqx4g')
