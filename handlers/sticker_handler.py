from aiogram import Router, types, F

from filters import AdminFilter

router_sticker_handler = Router()


@router_sticker_handler.message(AdminFilter(), F.sticker)
async def sticker_id(message: types.Message):
    await message.answer(f'Here is your`s sticker id: {message.sticker.file_id}')
