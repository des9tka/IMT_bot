from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


language_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Ru', callback_data='Ru_language')],
        [InlineKeyboardButton(text='En', callback_data='En_language')],
    ]
)