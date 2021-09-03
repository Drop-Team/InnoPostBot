import logging

from telethon import TelegramClient, utils, events
from telethon.tl.types import Config

import bot
from config import API_HASH, API_ID, CHAT_ID

client = TelegramClient('anon', API_ID, API_HASH)


@client.on(events.NewMessage())
async def handler(event):
    if event.chat_id != CHAT_ID:
        return
    message_text = event.message.raw_text
    for user in bot.users:
        if (bot.users[user]["state"] == bot.UserStates.active 
             and bot.users[user]["last_name"].upper() in message_text.upper()):
            await bot.send_message_about_mention(user, message_text)


with client:
    bot.bot_start()
    client.run_until_disconnected()
    