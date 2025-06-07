from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import logging
import os
import openai

API_TOKEN = os.getenv("API_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Кнопки меню
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(
    KeyboardButton("🔮 Рассчитать матрицу судьбы"),
    KeyboardButton("💰 Финансовая матрица")
)
main_kb.add(
    KeyboardButton("❤️ Совместимость"),
    KeyboardButton("🚀 Расширенный анализ (платно)")
)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer("Добро пожаловать в Матрицу Судьбы! Выберите, что хотите рассчитать:", reply_markup=main_kb)

@dp.message_handler(lambda msg: msg.text == "🔮 Рассчитать матрицу судьбы")
async def classic_matrix(message: types.Message):
    await message.answer("Введите вашу дату рождения в формате ДД.ММ.ГГГГ")

@dp.message_handler(lambda msg: msg.text == "💰 Финансовая матрица")
async def finance_matrix(message: types.Message):
    await message.answer("Введите вашу дату рождения для расчёта финансовой матрицы:")

@dp.message_handler(lambda msg: msg.text == "❤️ Совместимость")
async def compatibility(message: types.Message):
    await message.answer("Введите две даты рождения через запятую. Пример: 06.10.1985, 15.08.1990")

@dp.message_handler(lambda msg: msg.text == "🚀 Расширенный анализ (платно)")
async def premium_feature(message: types.Message):
    await message.answer("Для доступа к расширенному анализу приобретите доступ на сайте: https://вашсайт.рф")

@dp.message_handler(lambda msg: '.' in msg.text and len(msg.text) in (10, 21))
async def process_date_input(message: types.Message):
    try:
        dates = [d.strip() for d in message.text.split(',')]
        if len(dates) == 1:
            birth_date = datetime.strptime(dates[0], "%d.%m.%Y")
            day, month, year = birth_date.day, birth_date.month, birth_date.year
            c = sum(int(ch) for ch in str(year))
            d1 = day + month + c
            e = reduce_to_arcana(d1)
            gpt_text = get_gpt_interpretation(e)
            await message.answer(f"🎴 Аркан судьбы: {e}\n\n{gpt_text}")
        elif len(dates) == 2:
            await message.answer("🔗 Базовая совместимость рассчитана. Расширенная версия доступна после оплаты.")
        else:
            await message.answer("Проверьте формат ввода. Пример: 06.10.1985 или 06.10.1985, 15.08.1990")
    except Exception:
        await message.answer("Ошибка обработки даты. Убедитесь в правильном формате: ДД.ММ.ГГГГ")

def reduce_to_arcana(num):
    while num > 22:
        num = sum(int(d) for d in str(num))
    return num if num != 0 else 22

def get_gpt_interpretation(arkana_number):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты эзотерик и таролог. Дай понятную, вдохновляющую интерпретацию Аркана из матрицы судьбы. Объясни кратко суть, миссию, возможные уроки."},
                {"role": "user", "content": f"Расскажи про Аркан номер {arkana_number} из матрицы судьбы."}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Ошибка GPT: {e}"

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
