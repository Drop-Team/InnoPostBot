from telethon import TelegramClient, events

from app import bot
from app.logger import logger
from app.metrics import Metrics
import config

client = TelegramClient("innopost", config.API_ID, config.API_HASH)


@client.on(events.NewMessage())
async def handler(event):
    if event.chat_id != config.CHAT_ID:
        return

    Metrics.receiving_message.inc()

    message_text = event.message.raw_text
    message_link = f"https://t.me/c/{event.message.chat.id}/{event.message.id}"
    logger.info(f"New message from {event.chat_id} ({message_link})")

    await bot.process_fetched_message(message_text, message_link)


def start():
    print("Fetch client starting...")
    client.start()
