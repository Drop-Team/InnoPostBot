from telethon import TelegramClient, utils, events
from telethon.tl.types import Config
from prometheus_client import start_http_server

import bot
from config import API_HASH, API_ID, CHAT_ID
from metrics import Metrics

client = TelegramClient('anon', API_ID, API_HASH)


@client.on(events.NewMessage())
async def handler(event):
    #bot.users_locked = True
    if event.chat_id != CHAT_ID:
        return
    message_text = event.message.raw_text
    message_link = f"https://t.me/c/{event.message.chat.id}/{event.message.id}"
    bot.logger.info(f"New message from {event.chat_id} {message_link}")
    for user in bot.users:
        if (bot.users[user]["state"] == bot.UserStates.active 
             and (bot.users[user]["last_name"].upper() in message_text.upper() or 
                  bot.users[user]["last_name_en"].upper() in message_text.upper())):
            await bot.send_message_about_mention(user, message_text, message_link)
    #bot.users_locked = False


with client:
    start_http_server(8000)
    bot.bot_start()
    bot.logger.info(f"Initing client...")
    client.run_until_disconnected()
    