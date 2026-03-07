from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

chooses = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Только текст', callback_data='only_text')],
    [InlineKeyboardButton(text='Не только текст', callback_data='not_only_text')]
])

to_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='to_menu')],
])

cancel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')],
])