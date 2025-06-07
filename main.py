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

def get_coordinates(city):
    try:
        url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={OPENCAGE_API_KEY}&language=ru"
        res = requests.get(url)
        data = res.json()
        lat = data['results'][0]['geometry']['lat']
        lng = data['results'][0]['geometry']['lng']
        return GeoPos(str(lat), str(lng))
    except:
        return None

def gpt_interpretation(planet, sign, house):
    prompt = f"Опиши влияние {planet} в знаке {sign} и {house} доме в натальной карте. Стиль: астропсихология, глубоко, но понятно."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты опытный астролог. Дай психологическую и эзотерическую трактовку."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def gpt_aspect_interpretation(aspect):
    prompt = f"Дай астропсихологическую интерпретацию аспекта {aspect}. Пиши красиво, как профессиональный астролог."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты астролог, профессионально интерпретируешь аспекты натальной карты."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def generate_pdf(user_id, interpretations):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Натальная карта: трактовка", ln=True, align='C')
    pdf.ln(10)
    for interp in interpretations:
        pdf.multi_cell(0, 10, interp)
        pdf.ln(2)
    file_path = f"/mnt/data/chart_{user_id}.pdf"
    pdf.output(file_path)
    return file_path

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в *Зеркало Судьбы* — бота, который раскроет твою натальную карту с помощью астрологии и GPT.

Нажми кнопку ниже, чтобы начать расчёт ✨",
        reply_markup=start_kb,
        parse_mode="Markdown"
    )

@dp.message_handler(lambda msg: msg.text == "🚀 Начать расчёт")
async def show_main_menu(message: types.Message):
    await message.answer("Готово! Выбирай, что хочешь получить 👇", reply_markup=main_kb)

@dp.message_handler(lambda msg: msg.text == "💰 Купить полный разбор")
async def handle_payment(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Оплатить 199₽", url="https://your-site.com/pay"))
    await message.answer(
        "Чтобы получить *расширенный PDF-анализ* натальной карты с трактовками планет и аспектов, перейди по кнопке ниже 👇",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message_handler(lambda msg: msg.text == "🔮 Получить натальную карту")
async def request_data(message: types.Message):
    await message.answer("Введите данные рождения:
ДД.ММ.ГГГГ, ЧЧ:ММ, Город")

@dp.message_handler(lambda msg: msg.text == "📄 Скачать PDF разбор")
async def send_pdf(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_cache and 'pdf_path' in user_cache[user_id]:
        with open(user_cache[user_id]['pdf_path'], 'rb') as doc:
            await message.answer_document(doc)
    else:
        await message.answer("Вы ещё не запрашивали натальную карту.")

@dp.message_handler()
async def natal_analysis(message: types.Message):
    try:
        user_id = message.from_user.id
        text = message.text.strip()
        date_str, time_str, city = [x.strip() for x in text.split(',')]
        pos = get_coordinates(city)

        if not pos:
            await message.answer("❗ Не удалось определить координаты города.")
            return

        date_parts = date_str.split('.')
        dt = Datetime(f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}", time_str, '+03:00')
        chart = Chart(dt, pos)

        planets = ['SUN', 'MOON', 'ASC', 'MERCURY', 'VENUS', 'MARS']
        interpretations = []
        short_summary = []

        for obj in planets:
            item = chart.get(obj)
            line = f"{item} — {item.sign} в {item.house} доме"
            short_summary.append(line)
            interp = gpt_interpretation(item, item.sign, item.house)
            interpretations.append(f"{line}\n{interp}\n")

        aspects = getAspects(chart.objects, orb=6)
        interpretations.append("🌌 Аспекты:")
        for asp in aspects:
            description = f"{asp.obj1} {asp.type} {asp.obj2}"
            interpretation = gpt_aspect_interpretation(description)
            interpretations.append(f"{description}\n{interpretation}\n")

        summary = "\n".join(short_summary)
        await message.answer(f"🔭 Краткий обзор:\n\n{summary}\n\n📄 Генерация PDF с полной трактовкой...")

        pdf_path = generate_pdf(user_id, interpretations)
        user_cache[user_id] = {"pdf_path": pdf_path}

        with open(pdf_path, 'rb') as doc:
            await message.answer_document(doc)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {e}\nПроверь формат: ДД.ММ.ГГГГ, ЧЧ:ММ, Город")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
