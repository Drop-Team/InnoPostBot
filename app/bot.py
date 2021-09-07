from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor, exceptions

from app.logger import logger
from app.users import users, UserStates, save_file
from app.metrics import Metrics

import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)


async def process_fetched_message(message_text, message_link):
    lower_msg_text = message_text.lower()
    for user_id, user in users.items():
        if not (user.state == UserStates.confirmed and user.subscribed and
                (user.last_name_ru.lower() in lower_msg_text or user.last_name_en.lower() in lower_msg_text)):
            continue
        try:
            html_link = f"<a href='{message_link}'>сообщения</a>"
            await bot.send_message(user_id, f"Кажется, тебе что-то пришло. Вот копия {html_link}:",
                                   parse_mode="HTML")
            await bot.send_message(user_id, message_text)
            await bot.send_message(user_id, "Почтовое отделение 420500:\n"
                                            "ПН - ПТ: 9.00 - 17.00\n"
                                            "СБ - ВС: Выходной\n"
                                            "Университетская ул., 7, Иннополис, Россия\n"
                                            "Для того, чтобы забрать почтовое отправление нужно "
                                            "иметь с собой паспорт или электронную подпись.")
            Metrics.sending_notification.labels("success").inc()
        except exceptions.BotBlocked:
            logger.info(f"Bot blocked by user {user_id}")
            Metrics.sending_notification.labels("blocked").inc()


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    logger.info(f"User {message.from_user.username} ({message.from_user.id}) started bot")
    Metrics.start_command.labels("success").inc()
    user = users[message.from_user.id]
    if user.state == UserStates.confirmed:
        return await message.answer(f"Я тебя помню как {user.last_name_ru} ({user.last_name_en})\n"
                                    "Если захочешь сменить фамилию, напиши /name\n"
                                    "Чтобы сменить режим уведомлений, напиши /mode")
    await message.answer("Привет, это @innopostbot\n"
                         "Отправь мне свою фамилию, чтобы я отслеживал её в канале Почты России")


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    logger.info(f"User {message.from_user.username} ({message.from_user.id}) used help command")
    Metrics.help_command.labels("success").inc()
    user = users[message.from_user.id]
    if user.state == UserStates.confirmed:
        user_mode = "Включены" if user.subscribed else "Отключены"
        await message.answer(f"Я тебя помню как *{user.last_name_ru}* (*{user.last_name_en}*)\n"
                             f"/name - сменить фамилию\n\n"
                             f"Уведомления: *{user_mode}*\n"
                             f"/mode -  переключить режим",
                             parse_mode="Markdown")
    await message.answer("Поддержка: @blinikar и @KeepError\n"
                         "GitHub: https://github.com/blinikar/innopostbot",
                         parse_mode="Markdown", disable_web_page_preview=True, )


@dp.message_handler(lambda message: users[message.from_user.id].state == UserStates.init)
async def process_last_name_ru(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"User {user_id} enters last name on Russian")
    if not message.text.isalpha():
        return await message.answer("Тебе нужно отправить только фамилию (например, *Иванов*).",
                                    parse_mode="Markdown")
    users[user_id].last_name_ru = message.text
    users[user_id].state = UserStates.saved_last_name_ru
    await message.answer("Отлично! Теперь напиши свою фамилию на английском.")
    save_file()


@dp.message_handler(lambda message: users[message.from_user.id].state == UserStates.saved_last_name_ru)
async def process_last_name_en(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"User {user_id} enters last name on English")
    if not message.text.isalpha():
        return await message.answer("Тебе нужно отправить только фамилию (например, *Ivanov*).",
                                    parse_mode="Markdown")
    users[user_id].last_name_en = message.text
    users[user_id].state = UserStates.confirmed
    await message.answer(f"Отлично! Я запомнил тебя как {users[user_id].last_name_ru} ({users[user_id].last_name_en})\n"
                         f"Теперь я уведомлю, когда увижу тебя в списках получателей.\n"
                         f"Если захочешь сменить фамилию, напиши /name\n"
                         f"Чтобы отписаться от уведомлений, напиши /mode")
    Metrics.registration.labels("success").inc()
    save_file()


@dp.message_handler(lambda message: users[message.from_user.id].state == UserStates.confirmed, commands=["name"])
async def process_last_name_command(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"User {user_id} requested last name changing")
    users[user_id].state = UserStates.init
    await message.answer("Отлично! Теперь напиши свою фамилию.")
    save_file()


@dp.message_handler(lambda message: users[message.from_user.id].state == UserStates.confirmed, commands=["mode"])
async def process_change_mode_command(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"User {user_id} requested changing mode")
    user = users[user_id]
    if user.subscribed:
        await message.answer("Больше не буду тебя беспокоить. Для отмены напиши /mode снова.")
    else:
        await message.answer("Отлично, уведомления снова включены!")
    user.subscribed = not user.subscribed
    save_file()


def start():
    print("Bot starting...")
    executor.start_polling(dp)
