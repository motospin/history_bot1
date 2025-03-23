
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_epoch_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Российская Империя (1721-1917)", callback_data="epoch_ri")
    builder.button(text="СССР (1922-1991)", callback_data="epoch_ussr")
    builder.button(text="Россия (1991-наст.вр.)", callback_data="epoch_rf")
    builder.adjust(1)
    return builder.as_markup()

def get_difficulty_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Поверхностный", callback_data="diff_basic")
    builder.button(text="Средний", callback_data="diff_medium")
    builder.button(text="Углубленный", callback_data="diff_advanced")
    builder.adjust(1)
    return builder.as_markup()

def get_schedule_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да, 3 раза в день", callback_data="schedule_yes")
    builder.button(text="Нет, читать когда удобно", callback_data="schedule_no")
    builder.adjust(1)
    return builder.as_markup()
