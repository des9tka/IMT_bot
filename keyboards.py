from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

language_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Ru', callback_data='Ru_language')],
        [InlineKeyboardButton(text='En', callback_data='En_language')],
        [InlineKeyboardButton(text='Ua', callback_data='Ua_language')],
    ]
)

image_size_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='256x256', callback_data='image_size_kb 1')],
        [InlineKeyboardButton(text='512x512', callback_data='image_size_kb 2')],
        [InlineKeyboardButton(text='1024x1024', callback_data='image_size_kb 3')],
    ]
)

image_numbers_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='1', callback_data='image_numbers_kb 1')],
        [InlineKeyboardButton(text='2', callback_data='image_numbers_kb 2')],
        [InlineKeyboardButton(text='3', callback_data='image_numbers_kb 3')],
        [InlineKeyboardButton(text='4', callback_data='image_numbers_kb 4')],
    ]
)

image_request_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Request', callback_data='image_request_response')],
    ]
)

voice_assistant_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='On', callback_data='voice_assistant_on')],
        [InlineKeyboardButton(text='Off', callback_data='voice_assistant_off')],
    ]
)

close_sure = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Yes', callback_data='close_sure_yes')],
        [InlineKeyboardButton(text='No', callback_data='close_sure_no')],
    ]
)
