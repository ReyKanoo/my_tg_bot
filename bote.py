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
API_TOKEN = ''

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
    await message.answer("Пивте, это бот منئ ؤتجابغفلائ رفرب ؤتي لا لاج لاتؤرتىاب", reply_markup=role_kb)
    await state.set_state(Form.role)

@dp.callback_query(lambda c: c.data in ["Я смотрю мемы", "Я хочу закинуть мемы"])
async def role_choose(callback: CallbackQuery, state):
    print(callback)
    await state.update_data(role=callback)
    await callback.answer()
    await callback.message.answer("Напиши свой ник")
    await state.set_state(Form.name)


async def choose_meme (message: Message, state):
    await state.update_data(name = message.text)
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

@dp.message(F.text == "/mem")
async def list_meme(message: Message):
    cursor.execute("SELECT name, breed FROM Dogs")
    rows = cursor.fetchall()

    if not rows:
        await message.answer("В базе пока нет ни одного мема.")
        return

async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Окей, всё сбросил. Напиши /start, чтобы начать заново.", reply_markup=ReplyKeyboardRemove())

async def main():
    dp.message.register(cmd_start, F.text == "/start")
    dp.message.register(cancel_handler, F.text == "/cancel")
    dp.message.register(role_choose, Form.role)
    dp.message.register(choose_meme, Form.name) 
    dp.message.register(photo_chose, Form.meme)
    dp.message.register(list_meme)
    dp.message.register(cancel_handler)
    await dp.start_polling(bot)
    #     role = State()
    # name = State()
    # meme = State()

if __name__ == "__main__":
    asyncio.run(main())