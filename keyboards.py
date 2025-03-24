from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, KeyboardButton
from typing import List, Optional

def get_epoch_keyboard(with_back: bool = False):
    """Клавиатура для выбора исторической эпохи."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Российская Империя (1721-1917)", callback_data="epoch_ri")
    builder.button(text="СССР (1922-1991)", callback_data="epoch_ussr")
    builder.button(text="Россия (1991-наст.вр.)", callback_data="epoch_rf")
    builder.adjust(1)
    
    # Если нужна кнопка "Назад"
    if with_back:
        builder.button(text="◀️ Назад", callback_data="back_to_settings")
        builder.button(text="🏠 Главное меню", callback_data="back_to_main")
        builder.adjust(1, 2)  # Первый ряд - 1 кнопка, второй ряд - 2 кнопки
    
    return builder.as_markup()

def get_difficulty_keyboard(with_back: bool = False):
    """Клавиатура для выбора уровня сложности."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Поверхностный", callback_data="diff_basic")
    builder.button(text="Средний", callback_data="diff_medium")
    builder.button(text="Углубленный", callback_data="diff_advanced")
    builder.adjust(1)
    
    # Если нужна кнопка "Назад"
    if with_back:
        builder.button(text="◀️ Назад", callback_data="back_to_settings")
        builder.button(text="🏠 Главное меню", callback_data="back_to_main")
        builder.adjust(1, 2)
    
    return builder.as_markup()

def get_schedule_keyboard(with_back: bool = False):
    """Клавиатура для выбора расписания получения фактов."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Да, 3 раза в день", callback_data="schedule_yes")
    builder.button(text="Нет, читать когда удобно", callback_data="schedule_no")
    builder.adjust(1)
    
    # Если нужна кнопка "Назад"
    if with_back:
        builder.button(text="◀️ Назад", callback_data="back_to_settings")
        builder.button(text="🏠 Главное меню", callback_data="back_to_main")
        builder.adjust(1, 2)
    
    return builder.as_markup()

def get_main_menu_keyboard():
    """Создает основную клавиатуру с кнопками для главного меню."""
    builder = ReplyKeyboardBuilder()
    builder.button(text="Получить факт")
    builder.button(text="Мой прогресс")
    builder.button(text="Настройки")
    builder.button(text="Помощь")
    builder.adjust(2)  # 2 кнопки в ряду
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

def get_settings_keyboard():
    """Клавиатура для раздела настроек."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Изменить эпоху", callback_data="settings_epoch")
    builder.button(text="Изменить сложность", callback_data="settings_difficulty")
    builder.button(text="Изменить расписание", callback_data="settings_schedule")
    builder.button(text="Выбрать темы", callback_data="settings_themes")
    builder.button(text="🏠 Вернуться в главное меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def get_back_button():
    """Создает кнопку 'Назад'."""
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад", callback_data="back_to_settings")
    return builder.as_markup()

def get_themes_keyboard(with_back: bool = False, selected_themes: Optional[List[str]] = None):
    """
    Клавиатура для выбора тематических категорий.
    
    Args:
        with_back: Если True, добавит кнопку "Назад"
        selected_themes: Список уже выбранных тем
    """
    if selected_themes is None:
        selected_themes = []
    
    # Определяем темы и их callback_data
    themes = [
        ("Военная история", "theme_military"),
        ("Культура и искусство", "theme_culture"),
        ("Политика", "theme_politics"),
        ("Экономика", "theme_economy"),
        ("Наука и изобретения", "theme_science"),
        ("Повседневная жизнь", "theme_daily_life")
    ]
    
    builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки с темами, отмечая выбранные
    for theme_name, theme_id in themes:
        # Если тема выбрана, добавляем ✅ в начало названия
        if theme_id.split('_')[1] in selected_themes:
            text = f"✅ {theme_name}"
        else:
            text = theme_name
        
        builder.button(text=text, callback_data=theme_id)
    
    # Если нужна кнопка "Назад"
    if with_back:
        builder.button(text="✅ Сохранить выбор", callback_data="back_to_settings")
        builder.button(text="🏠 Главное меню", callback_data="back_to_main")
    
    builder.adjust(1)  # Одна кнопка в ряду
    return builder.as_markup()