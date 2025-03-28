import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import random
import sqlite3
import re
from datetime import datetime, timedelta
from database import init_db, add_user, get_user, update_user_misses
from openai import ChatCompletion

TOKEN = 'YOUR_TOKEN'
bot = Bot(token="7010016225:AAEeqUSlgc1-EBUTxO6_d7Mm2GnEMp0G9Jk")
dp = Dispatcher()

# Временное хранилище данных пользователей и групп
users = {}
groups = {}

# Инициализация базы данных
init_db()

# Список групп с диапазонами времени
GROUPS = [
    {"id": -1001234567890, "range": (0, 30)},  # ID группы 0-30 секунд
    {"id": -1001234567891, "range": (30, 60)},  # ID группы 30-60 секунд
    {"id": -1001234567892, "range": (60, 90)},  # ID группы 60-90 секунд
    {"id": -1001234567893, "range": (90, 120)},  # ID группы 90-120 секунд
    {"id": -1001234567894, "range": (120, 150)},  # ID группы 120-150 секунд
    {"id": -1001234567895, "range": (150, 180)},  # ID группы 150-180 секунд
    {"id": -1001234567896, "range": (180, 210)},  # ID группы 180-210 секунд
    {"id": -1001234567897, "range": (210, 240)},  # ID группы 210-240 секунд
    {"id": -1001234567898, "range": (240, 270)},  # ID группы 240-270 секунд
    {"id": -1001234567899, "range": (270, 300)},  # ID группы 270-300 секунд
]

# Функция для выбора группы
def get_group_for_time(plank_time):
    for group in GROUPS:
        if group["range"][0] <= plank_time < group["range"][1]:
            return group["id"]
    return None

@dp.message(Command('start'))
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    if not get_user(user_id):  # Проверяем, есть ли пользователь в базе
        add_user(user_id, username, 0)  # Добавляем пользователя с нулевым временем
    await message.answer(
        "Я помогаю людям ежедневно стоять в планке. И увеличивать время в планке на 1% в день.\n\n"
        "1. Встаньте в планку.\n"
        "2. Засеките время, сколько вы простояли.\n"
        "3. Пришлите мне это время в формате: '30 секунд' или '1 минута'."
    )

# Парсинг времени
def parse_time(input_text):
    input_text = input_text.lower().strip()
    # Обновляем регулярное выражение для обработки минут и секунд
    match = re.match(r'(?:(\d+)\s*(минут[а-я]*|мин))?\s*(?:и\s*)?(?:(\d+)\s*(секунд[а-я]*|сек))?', input_text)
    if not match:
        return None
    minutes, _, seconds, _ = match.groups()
    total_seconds = 0
    if minutes:
        total_seconds += int(minutes) * 60
    if seconds:
        total_seconds += int(seconds)
    if total_seconds < 1:  # Минимальное время 1 секунда
        return None
    return total_seconds

# Получение времени от пользователя и добавление в группу
@dp.message(F.text)
async def handle_time(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    user = get_user(user_id)  # Получаем данные пользователя из базы
    if not user:
        await message.answer("Для начала работы отправьте команду /start.")
        return

    plank_time = parse_time(message.text)
    if plank_time:
        # Обновляем данные пользователя в базе
        add_user(user_id, username, plank_time)
        await message.answer(f"Отлично! Вы добавлены с временем {plank_time} секунд.")
        
        # Выбор группы для добавления
        group_id = get_group_for_time(plank_time)
        if group_id:
            await bot.send_message(group_id, f"Пользователь @{username} добавлен в группу с временем {plank_time} секунд.")
        else:
            await message.answer("Не удалось найти подходящую группу.")
    else:
        await message.answer("Для начала работы постойте в планке и пришли мне время, сколько простояли.")

@dp.message(F.text)
async def handle_chat_message(message: types.Message):
    if "планка" in message.text.lower():
        response = ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Это сообщение из чата, где участники выполняют упражнение Планка. Если сообщение содержит вопрос о выполнении упражнения Планка, кратко ответь на него (не более 150 символов). Ответ должен быть безопасным и мотивирующим. Если сообщение не содержит вопроса или не касается упражнения планка ответь <IGNORE>."},
                {"role": "user", "content": message.text}
            ]
        )
        reply = response.choices[0].message["content"]
        if reply != "<IGNORE>":
            await message.reply(reply)

# Регулярная отправка напоминаний, статистики и исключение
async def reminder_task():
    while True:
        conn = sqlite3.connect("plankibot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, misses FROM users")
        users = cursor.fetchall()
        for user_id, misses in users:
            if misses == 2:
                await bot.send_message(user_id, f"@{user_id}, как у вас дела? Вы два дня не писали о ваших результатах.")
            elif misses >= 3:
                await bot.send_message(user_id, "Вы были исключены за неактивность.")
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            else:
                update_user_misses(user_id, misses + 1)
        conn.commit()
        conn.close()
        await asyncio.sleep(86400)  # каждый день

async def monthly_statistics_task():
    while True:
        conn = sqlite3.connect("plankibot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, initial_time, current_time, days, misses FROM users")
        users = cursor.fetchall()
        for user_id, initial_time, current_time, days, misses in users:
            months = days // 30
            await bot.send_message(
                user_id,
                f"@{user_id}, вы делаете планку {months} месяцев. "
                f"Увеличили время с {initial_time} секунд до {current_time} секунд. "
                f"Пропусков за прошедший месяц: {misses}."
            )
        conn.close()
        await asyncio.sleep(2592000)  # 30 дней

@dp.chat_member()
async def on_chat_member_update(chat_member: types.ChatMemberUpdated):
    if chat_member.new_chat_member.user.id == bot.id and chat_member.new_chat_member.status in ('administrator', 'member'):
        chat_id = chat_member.chat.id
        members = await bot.get_chat_administrators(chat_id)
        stats = []
        for member in members:
            if member.user.is_bot:
                continue
            user_data = get_user(member.user.id)
            if user_data:
                stats.append(
                    f"@{member.user.username or member.user.id}: "
                    f"Дата вступления: {user_data[7]}, "
                    f"Начальное время: {user_data[3]} секунд, "
                    f"Текущее время: {user_data[4]} секунд, "
                    f"Дней участия: {user_data[5]}, "
                    f"Пропусков: {user_data[6]}"
                )
        if stats:
            await bot.send_message(chat_id, "\n".join(stats))

async def main():
    asyncio.create_task(reminder_task())
    asyncio.create_task(monthly_statistics_task())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
