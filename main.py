import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os

# Загрузка переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    logging.error("BOT_TOKEN не найден. Проверьте Secrets в Replit.")
    exit()

# Инициализация бота
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Клавиатура для выбора эпохи
def get_epoch_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Российская Империя", callback_data="epoch_ri")
    builder.button(text="СССР", callback_data="epoch_sssr")
    builder.button(text="Россия", callback_data="epoch_russia")
    builder.adjust(2)  # Количество кнопок в ряду
    return builder.as_markup()


# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Привет! Выбери эпоху для изучения:",
                         reply_markup=get_epoch_keyboard())


# Обработка выбора эпохи
@dp.callback_query(F.data.startswith("epoch_"))
async def process_epoch(callback: CallbackQuery):
    epoch = callback.data.split("_")[1]
    await callback.answer()
    await callback.message.answer(
        f"Вы выбрали эпоху: {epoch.upper()}. Теперь выберите уровень сложности:"
    )


# Запуск бота
if __name__ == '__main__':
    import asyncio
    asyncio.run(dp.start_polling(bot))
