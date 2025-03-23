
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import Database
from keyboards import get_epoch_keyboard, get_difficulty_keyboard, get_schedule_keyboard

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и базы данных
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logging.error("BOT_TOKEN не найден. Проверьте Secrets в Replit.")
    exit()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()
scheduler = AsyncIOScheduler()

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await db.add_user(message.from_user.id)
    await message.answer(
        "Привет! Я бот для изучения истории. Выберите интересующую вас эпоху:",
        reply_markup=get_epoch_keyboard()
    )

# Обработка выбора эпохи
@dp.callback_query(F.data.startswith("epoch_"))
async def process_epoch_choice(callback: CallbackQuery):
    epoch = callback.data.split("_")[1]
    await callback.answer()
    await callback.message.answer(
        "Выберите уровень сложности изучения:",
        reply_markup=get_difficulty_keyboard()
    )

# Обработка выбора сложности
@dp.callback_query(F.data.startswith("diff_"))
async def process_difficulty_choice(callback: CallbackQuery):
    difficulty = callback.data.split("_")[1]
    await callback.answer()
    await callback.message.answer(
        "Хотите получать уведомления по расписанию?",
        reply_markup=get_schedule_keyboard()
    )

# Обработка выбора расписания
@dp.callback_query(F.data.startswith("schedule_"))
async def process_schedule_choice(callback: CallbackQuery):
    choice = callback.data.split("_")[1]
    await callback.answer()
    
    if choice == "yes":
        # Настройка расписания для пользователя
        scheduler.add_job(
            send_history_fact,
            'cron',
            hour='9,14,19',
            args=[callback.from_user.id]
        )
        await callback.message.answer(
            "Отлично! Вы будете получать исторические факты три раза в день: в 9:00, 14:00 и 19:00."
        )
    else:
        await callback.message.answer(
            "Хорошо! Вы можете использовать команду /fact для получения исторического факта в любое время."
        )

async def send_history_fact(user_id: int):
    # Здесь будет логика генерации исторического факта
    # В будущем добавим интеграцию с YandexGPT
    await bot.send_message(
        user_id,
        "Исторический факт дня: [Здесь будет сгенерированный факт]"
    )

# Запуск бота
async def main():
    await db.init()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
