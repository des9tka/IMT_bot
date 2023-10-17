from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

audio_session = None


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

close_sure_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Yes', callback_data='close_sure_yes')],
        [InlineKeyboardButton(text='No', callback_data='close_sure_no')],
    ]
)

volume_master_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='⬆️', callback_data='volume_master_up')],
        [InlineKeyboardButton(text='⬇️', callback_data='volume_master_down')],
        [InlineKeyboardButton(text='Mute/Unmute', callback_data='volume_master_mute_unmute')],
        [InlineKeyboardButton(text='Max/Min volume', callback_data='volume_master_max_min')],
    ]
)

volume_app_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='⬆️', callback_data=f'app_session_up')],
        [InlineKeyboardButton(text='⬇️', callback_data=f'app_session_down')],
        [InlineKeyboardButton(text='Mute/Unmute', callback_data=f'app_session_mute_unmute')],
        [InlineKeyboardButton(text='Max/Min volume', callback_data=f'app_session_max_min')],
    ]
)

volume_choice_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Master volume', callback_data='volume_choice_master')],
        [InlineKeyboardButton(text='App volume', callback_data='volume_choice_app')],
    ]
)

exit_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text='EXIT')]], one_time_keyboard=True, selective=True)
