import logging

from telethon import TelegramClient, utils, events

import bot
from config import API_HASH, API_ID

client = TelegramClient('anon', API_ID, API_HASH)

@client.on(events.NewMessage())
async def handler(event):
    sender = await event.get_sender()
    name = utils.get_display_name(sender)
    print(name, 'said', event.text, '!')

with client:
    bot.bot_start()
    client.run_until_disconnected()
    