from typing import Text
import json
import logging

from aiogram import Bot, types
import aiogram
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentTypes, user
from telethon.events import register

from config import BOT_TOKEN
from metrics import Metrics, save_users_count


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
    filename='bot.log'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

users = dict() #[id] <last_name_en><last_name>
users_locked = False

@dp.errors_handler()
async def exception(update, error):
    Metrics.errors.inc()


class UserStates:
    init = 0
    registration = 1
    registered = 2
    active = 3


def read_file():
    try:
        with open("users.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    
    data = {int(key): value for key, value in data.items()}
    save_users_count(data)
    return data


def save_file():
    with open("users.json", "w") as f:
        json.dump(users, f)
    save_users_count(users)


def state_filter(message, state):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"state": UserStates.init}
        users[user_id]["last_name_en"] = "unregistered"
        users[user_id]["last_name"] = "unregistered"
    return users[user_id]["state"] == state


def get_user_state(user_id):
    if user_id not in users:
        users[user_id] = {"state": UserStates.init}
        users[user_id]["last_name_en"] = "unregistered"
        users[user_id]["last_name"] = "unregistered"
    return users[user_id]["state"]


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    logger.info(f"User {message.from_user.username} ({message.from_user.id}) started bot")
    user_id = message.from_user.id
    if (get_user_state(user_id) == UserStates.active 
        or get_user_state(user_id) == UserStates.registered):
        user_last_name = users[user_id]["last_name"]
        user_last_name_en = users[user_id]["last_name_en"]
        return await message.answer(f"Я тебя помню. Тебя зовут {user_last_name} ({user_last_name_en})\n"
                                    "Если захочешь сменить имя и фамилию, напиши /name\n"
                                    "Чтобы сменить режим уведомлений, напиши /mode")
    await message.answer("Привет, это @innopostbot\n"
                         "Отправь мне свою фамилию, чтобы я отслеживал её в канале Почты России")
    Metrics.start_command.labels("success").inc()


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    logger.info(f"User {message.from_user.username} ({message.from_user.id}) used help command")
    user_id = message.from_user.id
    if (get_user_state(user_id) == UserStates.registered or 
        get_user_state(user_id) == UserStates.active):
        user_last_name = users[user_id]["last_name"]
        user_last_name_en = users[user_id]["last_name_en"]
        user_state_string = "Включены" if get_user_state(user_id) == UserStates.active else "Отключены"
        await message.answer(f"Я тебя помню. Твоя фамилия - {user_last_name} ({user_last_name_en})\n"
                            f"Уведомления: {user_state_string}",
                            parse_mode="Markdown")    
    await message.answer("Поддержка: @blinikar and @KeepError\n"
                         "GitHub: https://github.com/blinikar/innopostbot",
                         parse_mode="Markdown", disable_web_page_preview=True, )
    Metrics.help_command.labels("success").inc()


@dp.message_handler(lambda message: state_filter(message, UserStates.init))
async def process_last_name(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"User {user_id} enters last name on russian")
    if not message.text or " " in message.text or len(message.text) <= 1:
        return await message.answer("Это некорректная фамилия. Тебе нужно отправить только одно слово")
    if users_locked == True:
        return await message.answer("Сейчас мы обрабатываем входящее собщение, поэтому эта опция "
                                    "недоступна")    
    users[user_id]["last_name"] = message.text
    users[user_id]["state"] = UserStates.registration
    await message.answer("Отлично! Теперь напиши свою фамилию на английском")


@dp.message_handler(lambda message: state_filter(message, UserStates.registration))
async def process_last_name_en(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"User {user_id} enters last name on English")
    if not message.text or " " in message.text or len(message.text) <= 1:
        return await message.answer("Это некорректная фамилия. Тебе нужно отправить только одно слово")
    if users_locked == True:
        return await message.answer("Сейчас я обрабатываю входящее собщение, поэтому эта опция "
                                    "пока недоступна. Повторите через несколько минут")    
    users[user_id]["last_name_en"] = message.text
    users[user_id]["state"] = UserStates.active
    user_last_name = users[user_id]["last_name"]
    user_last_name_en = users[user_id]["last_name_en"]
    await message.answer("Отлично! Я начал следить и напишу тебе, когда что-то увижу\n"
                        "Если захочешь сменить имя и фамилию, напиши /name\n"
                        "Чтобы отписаться от уведомлений, напиши /mode")
    await message.answer(f"Я запомнил тебя как {user_last_name} ({user_last_name_en})")
    Metrics.registartion.labels("success").inc()
    save_file()


@dp.message_handler(lambda message: state_filter(message, UserStates.registered) 
                                    or state_filter(message, UserStates.active), commands=["name"])
async def process_name_command(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"User {user_id} changing name")
    if state_filter(message, UserStates.init):
        return await message.answer("Отправь мне только свою фамилию")
    if users_locked == True:
        return await message.answer("Сейчас мы обрабатываем входящее собщение, поэтому эта опция "
                                    "недоступна")
    users[user_id]["state"] = UserStates.init
    users[user_id]["last_name"] = "unregistered"
    users[user_id]["last_name_en"] = "unregistered"
    await message.answer("Отлично, теперь напиши свою фамилию")


@dp.message_handler(lambda message: state_filter(message, UserStates.registered) 
                                    or state_filter(message, UserStates.active), commands=["mode"])
async def process_change_mode_command(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"User {user_id} changing mode")
    if get_user_state(user_id) == UserStates.active:
        users[user_id]["state"] = UserStates.registered
        await message.answer("Больше не буду тебя беспокоить, "
                            "если захочешь вернуться напиши /mode снова")
        Metrics.changing_mode.labels("to_registered").inc()
    else:
        users[user_id]["state"] = UserStates.active
        await message.answer("Отлично! Я снова слежу за сообщениями")
        Metrics.changing_mode.labels("to_active").inc()
    save_file()
    


async def send_message_about_mention(user_id, message_text, message_link):
    logger.info(f"Sending notification to {user_id}")
    try:
        await bot.send_message(user_id, f"Кажется тебе что-то пришло. Вот копия сообщения "
                                        f"{message_link}")
        await bot.send_message(user_id, message_text)
        await bot.send_message(user_id, "Почтовое отделение 420500:\n"
                                        "ПН - ПТ: 9.00 - 17.00\n"
                                        "СБ - ВС: Выходной\n"
                                        "Университетская ул., 7, Иннополис, Россия\n"
                                        "Для того, чтобы забрать почтовое отправление нужно "
                                        "иметь с собой паспорт или электронную подпись")
        Metrics.sending_message.labels("success").inc()
    except aiogram.utils.exceptions.BotBlocked:
        logger.info(f"Bot blocked by user {user_id}")
        Metrics.sending_message.labels("blocked").inc()
    return


users = read_file()

def bot_start():
    logger.info(f"Initing aiogram...")
    executor.start_polling(dp)