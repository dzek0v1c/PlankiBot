import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import random
import re
from datetime import datetime, timedelta

TOKEN = 'YOUR_TOKEN'
bot = Bot(token="7010016225:AAEeqUSlgc1-EBUTxO6_d7Mm2GnEMp0G9Jk")
dp = Dispatcher()

# Временное хранилище данных пользователей и групп
users = {}
groups = {}

# Команда старта
@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer("Я помогаю людям ежедневно стоять в планке. Встаньте в планку, засеките сколько смогли простоять и пришлите результат мне")
    users[message.from_user.id] = {"status": "waiting_for_time"}

# Парсинг времени
def parse_time(input_text):
    input_text = input_text.lower().strip()
    match = re.match(r'(\d+)\s*(секунд[а-я]*|сек|минут[а-я]*|мин)?', input_text)
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    if unit in ('минута', 'минут', 'мин', 'минуты'):
        return value * 60
    elif unit in ('секунда', 'секунд', 'сек', None):
        return value
    return None

# Получение времени от пользователя и добавление в группу
@dp.message(F.text)
async def handle_time(message: types.Message):
    user = users.get(message.from_user.id)
    if user and user["status"] == "waiting_for_time":
        plank_time = parse_time(message.text)
        if plank_time:
            user.update({
                "status": "active",
                "initial_time": plank_time,
                "current_time": plank_time,
                "days": 0,
                "misses": 0,
                "join_date": datetime.now()
            })
            # Выбор группы с менее 10 участников
            target_groups = [gid for gid, gdata in groups.items() if len(gdata["members"]) < 10]
            if not target_groups:
                group = await bot.create_chat(title=f"Планка-группа {len(groups)+1}")
                await bot.set_chat_administrator_custom_title(group.id, bot.id, "Админ")
                groups[group.id] = {"members": [], "history_loaded": True}
                target_groups = [group.id]
            group_id = random.choice(target_groups)
            groups[group_id]["members"].append(message.from_user.id)
            await bot.send_message(group_id, f"Новый участник @{message.from_user.username} встал в планку на {plank_time} секунд")
            await message.answer("Отлично! Я добавил тебя в группу.")
        else:
            await message.answer("Для начала работы постойте в планке и пришли мне время, сколько простояли")
    else:
        await message.answer("Для начала работы постойте в планке и пришли мне время, сколько простояли")

# Регулярная отправка напоминаний, статистики и исключение
async def reminder_task():
    while True:
        for gid, gdata in groups.items():
            for uid in list(gdata["members"]):
                user = users.get(uid)
                if user:
                    last_active = datetime.now() - timedelta(days=user["misses"])
                    if user["misses"] == 2:
                        await bot.send_message(gid, f"@{uid}, как у вас дела? Вы два дня не писали о ваших результатах")
                    elif user["misses"] >= 3:
                        gdata["members"].remove(uid)
                        await bot.send_message(gid, f"@{uid} был исключён за неактивность.")
                    elif (datetime.now() - user["join_date"]).days % 30 == 0:
                        months = (datetime.now() - user["join_date"]).days // 30
                        await bot.send_message(gid, f"@{uid}, вы делаете планку {months} месяцев. Увеличили время с {user['initial_time']} секунд до {user['current_time']} секунд. Пропусков за прошедший месяц: {user['misses']}")
        await asyncio.sleep(86400)  # каждый день

async def main():
    asyncio.create_task(reminder_task())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
