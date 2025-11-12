from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.callbacks import BackCallback, CloseCallback


def back_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data=BackCallback())
    return builder.as_markup()

def close_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Закрыть", callback_data=CloseCallback())
    return builder.as_markup()