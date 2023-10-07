from aiogram import types
from aiogram.filters import Filter

from config import ADMIN_ID


class AdminFilter(Filter):
    async def __call__(self, message: types.Message):
        return message.from_user.id in [int(ADMIN_ID)]
