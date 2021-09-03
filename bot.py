import logging
from typing import Text

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentTypes, user
from telethon.events import register

from config import BOT_TOKEN

users = dict()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

class UserStates:
    init = 0
    registered = 1
    active = 2


def state_filter(message, state):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"state": UserStates.init}
        users[user_id]["state"] = UserStates.init
        users[user_id]["last_name"] = "unregistered"
    return users[user_id]["state"] == state


def get_user_state(user_id):
    if user_id not in users:
        users[user_id] = {"state": UserStates.init}
        users[user_id]["state"] = UserStates.init
        users[user_id]["last_name"] = "unregistered"
    return users[user_id]["state"]


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    #logger.info(f"User {message.from_user.username} ({message.from_user.id}) started bot")
    user_id = message.from_user.id
    if (get_user_state(user_id) == UserStates.active 
        or get_user_state(user_id) == UserStates.registered):
        return await message.answer("Я тебя помню\n"
                                    "Если захочешь сменить фамилию, напиши /name\n"
                                    "Чтобы отписаться от уведомлений напиши /mode")
    await message.answer("Привет, это @innopostbot\n"
                         "Отправь мне свою фамилию, чтобы я отслеживал её в канале Почты России")


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    #logger.info(f"User {message.from_user.username} ({message.from_user.id}) used help command")
    await message.answer("To print just send your file to me\n"
                         "Please *don't shut down* the printer. It causes connection problems. "
                         "Printer will suspend automatically!\n\n"
                         "Support: @blinikar and @KeepError\n"
                         "GitHub: https://github.com/blinikar/innoprintbot",
                         parse_mode="Markdown")


@dp.message_handler(lambda message: state_filter(message, UserStates.init))
async def process_name(message: types.Message):
    user_id = message.from_user.id
    if not message.text or " " in message.text:
        return await message.answer("Отправь мне только свою фамилию")    
    users[user_id]["last_name"] = message.text
    users[user_id]["state"] = UserStates.active
    await message.answer("Отлично! Я начал следить и напишу тебе, когда что-то увижу\n"
                        "Если захочешь сменить фамилию, напиши /name\n"
                        "Чтобы отписаться от уведомлений напиши /mode")


@dp.message_handler(lambda message: state_filter(message, UserStates.registered) 
                                    or state_filter(message, UserStates.active), commands=["name"])
async def process_name_command(message: types.Message):
    user_id = message.from_user.id
    if state_filter(message, UserStates.init):
        return await message.answer("Просто напиши свою фамилию")
    users[user_id]["state"] = UserStates.init
    users[user_id]["last_name"] = "unregistered"
    await message.answer("Отлично, теперь напиши свою фамилию")


@dp.message_handler(lambda message: state_filter(message, UserStates.registered) 
                                    or state_filter(message, UserStates.active), commands=["mode"])
async def process_change_mode_command(message: types.Message):
    user_id = message.from_user.id
    if get_user_state(user_id) == UserStates.active:
        users[user_id]["state"] = UserStates.registered
        return await message.answer("Больше не буду тебя беспокоить, "
                                    "если захотите вернуться напиши /mode снова")
    users[user_id]["state"] = UserStates.active
    await message.answer("Отлично! Я снова слежу за сообщениями")


async def send_message_about_mention(user_id, message_text):
    await bot.send_message(user_id, "Кажется тебе что-то пришло. Вот копия сообщения")
    await bot.send_message(user_id, message_text)
    return


def bot_start():
    executor.start_polling(dp)