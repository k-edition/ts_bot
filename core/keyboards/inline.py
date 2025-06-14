from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ready_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='ГОТОВО',
                             callback_data='ready1')
    ]
])
