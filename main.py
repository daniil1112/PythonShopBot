from aiogram import Bot, Dispatcher, executor, types
import logging
from dotenv import load_dotenv
from pathlib import Path
import os
import peewee
import datetime
from peewee import *
from playhouse.shortcuts import ReconnectMixin
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

API_TOKEN = os.getenv("API_TOKEN")
QIWI_TOKEN = os.getenv("QIWI_TOKEN")
QIWI_ACCOUNT = os.getenv("QIWI_ACCOUNT")
JoinLink = "https://t.me/joinchat/CjISZkSC99EwNTJi"


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    link = State()  # Will be represented in storage as 'Form:link'


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass


db = ReconnectMySQLDatabase("bot", host="localhost", port=3308, user="root", password="pswd")


class User(peewee.Model):
    userid = peewee.IntegerField(unique=True)
    balance = peewee.IntegerField(default=0)
    created_at = peewee.DateTimeField(default=datetime.datetime.now())
    chat = peewee.IntegerField(unique=True)

    class Meta:
        database = db
        db_table = "Users"


class Payment(peewee.Model):
    userid = peewee.IntegerField()
    amount = peewee.IntegerField()
    status = peewee.IntegerField(default=1)
    comment = peewee.TextField()
    created_at = peewee.DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db
        db_table = "Payments"


class Account(peewee.Model):
    gameid = peewee.IntegerField()
    email = peewee.TextField()
    password = peewee.TextField()
    created_at = peewee.DateTimeField(default=datetime.datetime.now())
    used_at = peewee.DateTimeField(default=datetime.datetime.now())
    canUse = peewee.IntegerField(default=1)
    used_by = peewee.BigIntegerField(default=0)

    class Meta:
        database = db
        db_table = "Account"


class Games(peewee.Model):
    name = peewee.TextField()
    coast = peewee.IntegerField()

    class Meta:
        database = db
        db_table = "Games"


class GameTags(peewee.Model):
    gameid = peewee.IntegerField()
    tag = peewee.TextField()

    class Meta:
        database = db
        db_table = "GameTags"


User.create_table()
Payment.create_table()
Account.create_table()
Games.create_table()
GameTags.create_table()

async def checkSubcribe(chatId, userId):
    try:
        chatMember = await bot.get_chat_member(chatId, userId)
        if chatMember.status == "left":
            return False
        return True
    except:
        return False
@dp.message_handler(commands=['start'])
async def startRoute(message: types.Message):
    try:
        User.create(userid=message.from_user.id, chat=message.chat.id)
        msg = """Привет 👋 
        🍏 Я Майлс, бот, который поможет тебе загрузить приложение из апстора совершено бесплатно 💴

        Для этого мне нужно понять, что бы ты хотел загрузить 📲
        ✍️ Отправь мне ссылку на это приложение из AppStore """

        await bot.send_message(message.from_user.id, msg)
        # Отправка файла с сервера телеги
        await bot.send_video(message.from_user.id, "BAACAgIAAxkBAAIDD2EBJ973FI_-tkVDS0wadkj8UnRlAAIrEQACIpgRSAJPM9ilgSeqIAQ")

        await bot.send_message(message.from_user.id, "Как это сделать, наглядный пример ❤️")
        await Form.link.set()
    except:
        pass


async def getLinkFromStartRoute(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, "Введите ссылку на игру")
        await Form.link.set()
    except:
        pass


@dp.message_handler(state=Form.link)
async def prepareLink(message: types.Message, state: FSMContext):
    link = message.text
    if len(link.split("/")) < 5:
        await bot.send_message(message.from_user.id, "Невозмозжно обработать ссылку, введите ее заново")
        await Form.link.set()
        return
    else:
        game = link.split("/")[-2].lower()
        if await checkSubcribe("-1001427565975", message.from_user.id):
            await bot.send_message(message.from_user.id, "Подписка есть")
            await bot.send_message(message.from_user.id, "Выдача игры "+game)
        else:
            keyboard = types.InlineKeyboardMarkup()
            key_join_chat = types.InlineKeyboardButton("Подписаться", url=JoinLink)
            key_check_subcribe = types.InlineKeyboardButton("Проверить подписку")
            keyboard.add(key_join_chat)
            keyboard.add(key_check_subcribe)
            await bot.send_message(message.from_user.id, """😜 Перед тем, как установить игру, необходимо будет подписать на наш телеграмм канал 👇

https://t.me/dfsgdfgDFSDFsdf

Мы работаем бескорыстно, поэтому будем рады, если вы останетесь с нами надолго 🥰""", reply_markup=keyboard)
        await getLinkFromStartRoute(message)







@dp.callback_query_handler(lambda c: True)
async def process_callback_button1(callback_query: types.callback_query):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Нажата первая кнопка!')


executor.start_polling(dp, skip_updates=True)


# https://t.me/dfsgdfgDFSDFsdf