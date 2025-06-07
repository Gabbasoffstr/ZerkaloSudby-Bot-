from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import logging
import os
import requests
import openai
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
from flatlib.aspects import getAspects
from fpdf import FPDF

API_TOKEN = os.getenv("API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("🚀 Начать расчёт"))

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(
    KeyboardButton("🔮 Получить натальную карту"),
    KeyboardButton("📄 Скачать PDF разбор"),
    KeyboardButton("💰 Купить полный разбор")
)

user_cache = {}

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в *Зеркало Судьбы* — бота, который раскроет твою натальную карту с помощью астрологии и GPT.

Нажми кнопку ниже, чтобы начать расчёт ✨",
        reply_markup=start_kb,
        parse_mode="Markdown"
    )

# Остальные хендлеры могут быть добавлены здесь

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
