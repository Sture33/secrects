from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

chooses = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отправить анонимный вопрос', callback_data='q_type1')],
    [InlineKeyboardButton(text='Анонимно ответить на вопрос', callback_data='q_type2')]
])

to_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='cb_menu')],
])

cancel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')],
])