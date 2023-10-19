from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from config import bot
from filters import AdminFilter

router_video_handler = Router()


@router_video_handler.message(AdminFilter(), F.video)
async def cpt_video(message: types.Message, state: FSMContext):
    size = message.video.file_size / 1024 / 1024
    if size > 100:
        await message.answer('Video should be less then 100 mb. ')
    else:
        try:
            file_id = message.video.file_id
            file = await bot.get_file(file_id)

            await bot.download_file(file.file_path, "work_video.mp4")
            await state.update_data(subject=file_id)
            await state.update_data(command_name='/video_ai')
            await message.answer('Select command for your image: \n- /video_caption\n- /video_resize + "width"x"high"\n- /video_mp3\n- /video_id')

        except (Exception,):
            await message.answer('Something went wrong. Check your input video and try again...')
