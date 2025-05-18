import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, KeyboardButton,CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
# from dotenv import load_dotenv
# load_dotenv()
API_TOKEN = '7228651021:AAF2mFoe0bC0BL5bngUtqvwggkOL2iPNeGM'

conn = sqlite3.connect('bot_meme.db')
cursor = conn.cursor()

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

class Form(StatesGroup):
    role = State()
    name = State()
    meme = State()

role_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Я смотрю мемы", callback_data="Я смотрю мемы"),
        InlineKeyboardButton(text="Я хочу закинуть мемы", callback_data="Я хочу закинуть мемы")
    ]
])

async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Пивте, это бот منئ ؤتجابغفلائ رفربؤتي لا لاج لاتؤرتىاب", reply_markup=role_kb)
    await state.set_state(Form.role)

@dp.callback_query(lambda c: c.data in ["Я смотрю мемы", "Я хочу закинуть мемы"])
async def handle_yes(callback: CallbackQuery, state):
    print(callback)
    await state.update_data(role=callback)
    await callback.answer()
    await callback.message.answer("Напиши свой ник/псевдоним")
    await state.set_state(Form.name)

@dp.message(F.text == "/imeme")
async def find_command_handler(message: Message, state):
    await message.answer("Ну что же, теперь отправляй мем.")
    await state.set_state(Form.meme)

async def photo_chose(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    photo_data = await bot.download_file(file.file_path)
    photo_bytes = photo_data.read()
    data = await state.get_data()
    name = data["meme"]
    cursor.execute("INSERT INTO Memes (name, breed, photo) VALUES (?, ?, ?)", (name, photo_bytes))
    conn.commit()
    await message.answer(f"Мем {name} добавлен!")
    await state.clear()


