from aiogram import Router, types, F

from filters import AdminFilter

router_audio_handler = Router()


@router_audio_handler.message(AdminFilter(), F.audio)
async def get_audio_id(message: types.Message):
    await message.answer(message.audio.file_id)
