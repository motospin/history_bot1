import logging
import os
import signal
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import ErrorEvent
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import Database
from keyboards import (
    get_epoch_keyboard, 
    get_difficulty_keyboard, 
    get_schedule_keyboard,
    get_main_menu_keyboard,
    get_settings_keyboard,
    get_back_button,
    get_themes_keyboard
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и базы данных
BOT_TOKEN = '7079040743:AAF89lKBLucf0_yoSFrS1F3UEpZ9kXbOoyU'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()
scheduler = AsyncIOScheduler()

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await db.add_user(message.from_user.id)
    await message.answer(
        "Привет! Я бот для изучения истории России. Я помогу вам узнать интересные факты о разных исторических эпохах.\n\n"
        "Для начала выберите интересующую вас эпоху:",
        reply_markup=get_epoch_keyboard()
    )

@dp.message(Command("help"))
async def send_help(message: Message):
    help_text = (
        "🤖 *Бот для изучения истории России* 🤖\n\n"
        "Этот бот поможет вам изучать историю России по эпохам и с разной степенью детализации.\n\n"
        "*Основные команды:*\n"
        "• /start - Начать использование бота\n"
        "• /fact - Получить исторический факт\n"
        "• /settings - Изменить настройки\n"
        "• /progress - Просмотреть свой прогресс\n"
        "• /help - Получить справку\n\n"
        "*Как пользоваться:*\n"
        "1. Выберите историческую эпоху\n"
        "2. Выберите уровень сложности\n"
        "3. Решите, получать ли факты по расписанию\n"
        "4. Изучайте историю России!\n\n"
        "В любой момент вы можете изменить настройки через меню или команду /settings"
    )
    
    await message.answer(help_text, reply_markup=get_main_menu_keyboard())

@dp.message(F.text == "Получить факт")
@dp.message(Command("fact"))
async def send_fact_command(message: Message):
    user_id = message.from_user.id
    user_data = await db.get_user_progress(user_id)
    
    if not user_data or not user_data['selected_epoch']:
        await message.answer(
            "Похоже, вы еще не настроили свои предпочтения. Давайте сделаем это сейчас!",
            reply_markup=get_epoch_keyboard()
        )
        return
    
    await send_history_fact(user_id)
    # Увеличиваем счетчик просмотренных фактов
    await db.increment_fact_counter(user_id)
    
    # Проверяем, пора ли предложить тест
    facts_count = user_data['facts_viewed'] + 1  # +1 потому что мы только что увеличили счетчик
    if facts_count % 5 == 0:  # Каждые 5 фактов предлагаем тест
        await message.answer(
            "Вы изучили 5 новых фактов! Хотите проверить свои знания?",
            reply_markup=get_test_keyboard()
        )

@dp.message(F.text == "Мой прогресс")
@dp.message(Command("progress"))
async def show_progress(message: Message):
    user_id = message.from_user.id
    user_data = await db.get_user_progress(user_id)
    
    if not user_data or not user_data['selected_epoch']:
        await message.answer(
            "У вас еще нет прогресса. Начните изучение истории!",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Определяем эпоху в текстовом виде
    epoch_text = {
        "ri": "Российская Империя (1721-1917)",
        "ussr": "СССР (1922-1991)",
        "rf": "Россия (1991-наст.вр.)"
    }.get(user_data['selected_epoch'], "Неизвестная эпоха")
    
    # Определяем уровень сложности в текстовом виде
    difficulty_text = {
        "basic": "Поверхностный",
        "medium": "Средний",
        "advanced": "Углубленный"
    }.get(user_data['difficulty_level'], "Не выбран")
    
    # Вычисляем прогресс в процентах для выбранной эпохи
    progress_percent = 0
    total_years = 0
    
    if user_data['selected_epoch'] == "ri":
        total_years = 1917 - 1721
        progress_years = user_data['current_year'] - 1721
    elif user_data['selected_epoch'] == "ussr":
        total_years = 1991 - 1922
        progress_years = user_data['current_year'] - 1922
    elif user_data['selected_epoch'] == "rf":
        total_years = datetime.now().year - 1991
        progress_years = user_data['current_year'] - 1991
    
    if total_years > 0:
        progress_percent = min(100, max(0, (progress_years * 100) // total_years))
    
    # Формируем строку прогресса в виде [■■■■□□□□□□] XX%
    progress_bar_length = 10
    filled_blocks = progress_percent // 10
    progress_bar = '[' + '■' * filled_blocks + '□' * (progress_bar_length - filled_blocks) + ']'
    
    # Формируем сообщение о прогрессе
    progress_message = (
        f"📊 *Ваш прогресс в изучении истории* 📊\n\n"
        f"🔷 *Эпоха:* {epoch_text}\n"
        f"🔷 *Уровень сложности:* {difficulty_text}\n"
        f"🔷 *Текущий год изучения:* {user_data['current_year']}\n"
        f"🔷 *Изучено фактов:* {user_data['facts_viewed']}\n\n"
        f"*Прогресс по эпохе:* {progress_bar} {progress_percent}%\n\n"
        f"Продолжайте изучение истории! Каждый новый факт приближает вас к полному пониманию эпохи."
    )
    
    await message.answer(progress_message, reply_markup=get_main_menu_keyboard())

@dp.message(F.text == "Настройки")
@dp.message(Command("settings"))
async def show_settings(message: Message):
    user_id = message.from_user.id
    user_data = await db.get_user_progress(user_id)
    
    if not user_data:
        await db.add_user(user_id)
        user_data = await db.get_user_progress(user_id)
    
    # Формируем текст с текущими настройками
    epoch_text = "Не выбрана"
    if user_data['selected_epoch'] == "ri":
        epoch_text = "Российская Империя (1721-1917)"
    elif user_data['selected_epoch'] == "ussr":
        epoch_text = "СССР (1922-1991)"
    elif user_data['selected_epoch'] == "rf":
        epoch_text = "Россия (1991-наст.вр.)"
    
    difficulty_text = "Не выбран"
    if user_data['difficulty_level'] == "basic":
        difficulty_text = "Поверхностный"
    elif user_data['difficulty_level'] == "medium":
        difficulty_text = "Средний"
    elif user_data['difficulty_level'] == "advanced":
        difficulty_text = "Углубленный"
    
    schedule_text = "Не настроено"
    if user_data['subscription_active']:
        schedule_text = "По расписанию (3 раза в день)"
    else:
        schedule_text = "По запросу"
    
    settings_text = (
        f"⚙️ *Текущие настройки* ⚙️\n\n"
        f"🔹 *Эпоха:* {epoch_text}\n"
        f"🔹 *Уровень сложности:* {difficulty_text}\n"
        f"🔹 *Получение фактов:* {schedule_text}\n\n"
        f"Выберите, что вы хотите изменить:"
    )
    
    await message.answer(settings_text, reply_markup=get_settings_keyboard())

@dp.callback_query(F.data == "settings_epoch")
async def change_epoch(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите интересующую вас эпоху:",
        reply_markup=get_epoch_keyboard(with_back=True)
    )
    await callback.answer()

@dp.callback_query(F.data == "settings_difficulty")
async def change_difficulty(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите уровень сложности изучения:",
        reply_markup=get_difficulty_keyboard(with_back=True)
    )
    await callback.answer()

@dp.callback_query(F.data == "settings_schedule")
async def change_schedule(callback: CallbackQuery):
    await callback.message.edit_text(
        "Хотите получать уведомления по расписанию?",
        reply_markup=get_schedule_keyboard(with_back=True)
    )
    await callback.answer()

@dp.callback_query(F.data == "settings_themes")
async def change_themes(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите интересующие вас темы истории:",
        reply_markup=get_themes_keyboard(with_back=True)
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery):
    await show_settings(callback.message)
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

# Обработка выбора эпохи
@dp.callback_query(F.data.startswith("epoch_"))
async def process_epoch_choice(callback: CallbackQuery):
    epoch = callback.data.split("_")[1]
    start_year = {"ri": 1721, "ussr": 1922, "rf": 1991}[epoch]
    
    # Проверяем, новый ли пользователь
    user_data = await db.get_user_progress(callback.from_user.id)
    is_new_user = not user_data or not user_data['difficulty_level']
    
    # Обновляем данные пользователя
    if is_new_user:
        await db.update_user_preferences(callback.from_user.id, epoch, None, start_year)
        await callback.answer()
        await callback.message.edit_text(
            "Выберите уровень сложности изучения:",
            reply_markup=get_difficulty_keyboard()
        )
    else:
        # Если пользователь уже настроен, просто обновляем эпоху
        await db.update_epoch(callback.from_user.id, epoch, start_year)
        await callback.answer("Эпоха успешно изменена!")
        await show_settings(callback.message)

# Обработка выбора сложности
@dp.callback_query(F.data.startswith("diff_"))
async def process_difficulty_choice(callback: CallbackQuery):
    difficulty = callback.data.split("_")[1]
    user_data = await db.get_user_progress(callback.from_user.id)
    
    # Проверяем, новый ли пользователь
    is_new_user = not user_data or not user_data['selected_epoch'] or 'subscription_active' not in user_data or not user_data['subscription_active']
    
    if is_new_user:
        await db.update_user_preferences(
            callback.from_user.id, 
            user_data['selected_epoch'], 
            difficulty, 
            user_data['start_year']
        )
        await callback.answer()
        await callback.message.edit_text(
            "Хотите получать уведомления по расписанию?",
            reply_markup=get_schedule_keyboard()
        )
    else:
        # Если пользователь уже настроен, просто обновляем сложность
        await db.update_difficulty(callback.from_user.id, difficulty)
        await callback.answer("Уровень сложности успешно изменен!")
        await show_settings(callback.message)

# Обработка выбора расписания
@dp.callback_query(F.data.startswith("schedule_"))
async def process_schedule_choice(callback: CallbackQuery):
    choice = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    # Проверяем, настроены ли базовые параметры
    user_data = await db.get_user_progress(user_id)
    if not user_data or not user_data['selected_epoch'] or not user_data['difficulty_level']:
        text = "Сначала необходимо выбрать эпоху и уровень сложности. Пожалуйста, настройте эти параметры."
        await callback.message.edit_text(text, reply_markup=get_settings_keyboard())
        return

    subscription_active = choice == "yes"
    await db.update_subscription(user_id, subscription_active)
    
    if subscription_active:
        # Настройка расписания для пользователя
        job_id = f"fact_schedule_{user_id}"
        # Удаляем старое расписание, если оно существует
        scheduler.remove_job(job_id, ignore_if_not_exists=True)
        # Добавляем новое расписание
        scheduler.add_job(
            send_history_fact,
            'cron',
            hour='9,14,19',
            args=[user_id],
            id=job_id,
            replace_existing=True
        )
        text = "Отлично! Вы будете получать исторические факты три раза в день: в 9:00, 14:00 и 19:00."
    else:
        # Удаляем существующее расписание
        scheduler.remove_job(f"fact_schedule_{user_id}", ignore_if_not_exists=True)
        text = "Хорошо! Вы можете использовать кнопку 'Получить факт' для получения исторического факта в любое время."
    
    # Проверяем, это первоначальная настройка или изменение настроек
    user_data = await db.get_user_progress(callback.from_user.id)
    if not user_data.get('setup_completed', False):
        # Первоначальная настройка завершена
        await db.mark_setup_completed(callback.from_user.id)
        text += "\n\nНастройка завершена! Теперь вы можете начать изучение истории России."
        
    await callback.answer()
    # Создаем inline клавиатуру для сообщения
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🏠 Главное меню", callback_data="back_to_main")
    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    
    # Отправляем основное меню отдельным сообщением
    await bot.send_message(
        callback.from_user.id,
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )

@dp.callback_query(F.data.startswith("theme_"))
async def process_theme_choice(callback: CallbackQuery):
    theme = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    # Обновляем выбранные темы пользователя
    await db.toggle_theme(user_id, theme)
    
    # Получаем обновленный список тем
    selected_themes = await db.get_user_themes(user_id)
    
    await callback.answer(f"Тема {'добавлена' if theme in selected_themes else 'удалена'}")
    await callback.message.edit_text(
        "Выберите интересующие вас темы истории (можно выбрать несколько):",
        reply_markup=get_themes_keyboard(with_back=True, selected_themes=selected_themes)
    )

# Функция для отправки исторического факта
from yandex_gpt import YandexGPT

gpt = YandexGPT()

async def send_history_fact(user_id: int):
    user_data = await db.get_user_progress(user_id)
    if not user_data:
        return
    
    # Получаем выбранные темы пользователя (если они есть)
    selected_themes = await db.get_user_themes(user_id)
    
    fact = await gpt.generate_history_fact(
        epoch=user_data['selected_epoch'],
        year=user_data['current_year'],
        difficulty=user_data['difficulty_level'],
        themes=selected_themes  # Передаем темы в генератор фактов
    )
    
    # Создаем клавиатуру с контекстными кнопками для сообщения с фактом
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    fact_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Следующий факт", callback_data="next_fact")],
        [InlineKeyboardButton(text="⚙️ Изменить настройки", callback_data="open_settings")]
    ])
    
    await bot.send_message(
        user_id,
        f"📚 *Исторический факт ({user_data['current_year']} год):*\n\n{fact}",
        reply_markup=fact_keyboard
    )
    
    # Обновляем текущий год для следующего факта
    if user_data['current_year']:
        new_year = user_data['current_year'] + 1
        
        # Проверяем, не вышли ли мы за пределы эпохи
        if (user_data['selected_epoch'] == "ri" and new_year > 1917) or \
           (user_data['selected_epoch'] == "ussr" and new_year > 1991) or \
           (user_data['selected_epoch'] == "rf" and new_year > datetime.now().year):
            # Если вышли за пределы, предложим сменить эпоху
            await bot.send_message(
                user_id,
                f"Поздравляем! Вы изучили всю эпоху {user_data['selected_epoch']}. "
                f"Хотите перейти к изучению другой эпохи?",
                reply_markup=get_epoch_keyboard()
            )
        else:
            await db.update_current_year(user_id, new_year)

@dp.callback_query(F.data == "next_fact")
async def send_next_fact(callback: CallbackQuery):
    await callback.answer("Получаем следующий факт...")
    await send_fact_command(callback.message)

@dp.callback_query(F.data == "open_settings")
async def open_settings(callback: CallbackQuery):
    await callback.answer()
    await show_settings(callback.message)

def get_test_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Пройти тест", callback_data="start_test")],
        [InlineKeyboardButton(text="❌ Не сейчас", callback_data="skip_test")]
    ])

@dp.callback_query(F.data == "start_test")
async def start_test(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = await db.get_user_progress(user_id)
    
    # Здесь будет логика для генерации теста на основе эпохи и года
    # В базовой версии просто отправляем простой вопрос
    
    epoch_text = {
        "ri": "Российской Империи",
        "ussr": "СССР",
        "rf": "России"
    }.get(user_data['selected_epoch'], "")
    
    # Простой тестовый вопрос с вариантами ответов
    year = user_data['current_year']
    
    test_question = f"Вопрос о событиях {epoch_text} примерно {year} года:\n\n"
    
    # Имитация вопроса (в реальном боте здесь должна быть генерация вопроса на основе фактов)
    if user_data['selected_epoch'] == "ri":
        test_question += "Кто был императором России в начале XIX века?"
        options = [
            ["Александр I", "correct_alexander1"],
            ["Николай I", "wrong_nicholas1"],
            ["Павел I", "wrong_paul1"],
            ["Петр III", "wrong_peter3"]
        ]
    elif user_data['selected_epoch'] == "ussr":
        test_question += "Какое событие произошло в СССР в 1961 году?"
        options = [
            ["Первый полет человека в космос", "correct_space"],
            ["Карибский кризис", "wrong_caribbean"],
            ["Начало Великой Отечественной войны", "wrong_ww2"],
            ["Запуск первого спутника", "wrong_sputnik"]
        ]
    else:  # rf
        test_question += "В каком году была принята действующая Конституция Российской Федерации?"
        options = [
            ["1993", "correct_1993"],
            ["1991", "wrong_1991"],
            ["2000", "wrong_2000"],
            ["1998", "wrong_1998"]
        ]
    
    # Создаем клавиатуру с вариантами ответов
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    test_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=option[0], callback_data=option[1])] for option in options
    ])
    
    await callback.message.edit_text(
        f"📝 *Тест по истории* 📝\n\n{test_question}",
        reply_markup=test_keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("correct_"))
async def process_correct_answer(callback: CallbackQuery):
    await callback.answer("Правильно! 🎉", show_alert=True)
    
    # Увеличиваем счетчик правильных ответов пользователя
    await db.increment_correct_answers(callback.from_user.id)
    
    await callback.message.edit_text(
        f"✅ Правильно! Вы хорошо знаете историю!\n\n"
        f"Хотите продолжить изучение?",
        reply_markup=get_main_menu_keyboard()
    )

@dp.callback_query(F.data.startswith("wrong_"))
async def process_wrong_answer(callback: CallbackQuery):
    await callback.answer("Неправильно! Попробуйте еще раз.", show_alert=True)
    
    # Отмечаем неправильный ответ в статистике
    await db.increment_wrong_answers(callback.from_user.id)
    
    # Определяем правильный ответ на основе callback.data
    correct_answer = ""
    if "alexander1" in callback.data:
        correct_answer = "Александр I"
    elif "space" in callback.data:
        correct_answer = "Первый полет человека в космос"
    elif "1993" in callback.data:
        correct_answer = "1993"
    
    await callback.message.edit_text(
        f"❌ Неправильно!\n\n"
        f"Правильный ответ: *{correct_answer}*\n\n"
        f"Продолжайте изучать историю, чтобы улучшить свои знания!",
        reply_markup=get_main_menu_keyboard()
    )

@dp.callback_query(F.data == "skip_test")
async def skip_test(callback: CallbackQuery):
    await callback.answer("Тест пропущен")
    await callback.message.edit_text(
        "Вы решили пропустить тест. Продолжайте изучение истории!",
        reply_markup=get_main_menu_keyboard()
    )

# Функция для корректного завершения работы бота
def signal_handler(sig, frame):
    print("Получен сигнал завершения. Закрываю соединение с Telegram...")
    asyncio.run(bot.session.close())
    sys.exit(0)

# Регистрируем обработчик сигналов
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Запуск бота
@dp.error()
async def error_handler(event: ErrorEvent):
    """Глобальный обработчик ошибок"""
    logging.error(f"Update {event.update} caused error {event.exception}")
    try:
        # Если это ошибка Telegram API
        if isinstance(event.exception, TelegramAPIError):
            if hasattr(event.update, 'message'):
                await event.update.message.answer(
                    "Произошла ошибка при обработке запроса. Попробуйте позже."
                )
    except Exception as e:
        logging.error(f"Error in error handler: {e}")

async def main():
    await db.init()
    
    # Настройка для корректной обработки завершения
    await bot.delete_webhook(drop_pending_updates=True)
    
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен!")