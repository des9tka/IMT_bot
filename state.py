from aiogram.filters.state import StatesGroup


class BotState(StatesGroup):
    state = {
        'session_name': None,
        'message_id': None
    }
