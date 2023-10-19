import os

import cv2
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from config import bot
from filters import AdminFilter
from utils import is_not_empty
import keyboards as kb

router_photo_handler = Router()


@router_photo_handler.message(AdminFilter(), F.photo)
async def image_request(message: types.Message, state: FSMContext):
    sizes = None

    if message.caption and message.caption.startswith('/'):
        file = await bot.get_file(message.photo[-1].file_id)
        await message.bot.download_file(file.file_path, "work_image.jpg")

        if message.caption.startswith('/image_ai'):
            await message.answer('Image request to AI in development... ')
            os.remove('work_image.jpg')

        elif message.caption.startswith('/image_resize'):
            sizes = message.caption.replace('/image_resize', '').replace(' ', '')

        elif message.caption.startswith('/image_d'):
            await message.answer(f'Your image id: \n{file}')
            os.remove('work_image.jpg')

        if sizes:
            img = cv2.imread('work_image.jpg')
            sizes = list(filter(is_not_empty, sizes.split('x')))

            if len(sizes) > 2:
                await message.answer('Should be provided "width"x"high".')

            else:
                try:
                    resized_img = cv2.resize(img, (int(sizes[0]), int(sizes[1])))
                    cv2.imwrite('resized_image.jpg', resized_img)
                    await message.answer('Choose the quality of image:', reply_markup=kb.image_quality_kb)
                except (Exception,):
                    await message.answer('Something went wrong. Check your input size and try again...')

        else:
            await message.answer(f'Unknown command for image.')

    else:
        try:
            file = await bot.get_file(message.photo[-1].file_id)
            await message.bot.download_file(file.file_path, "work_image.jpg")
            await state.update_data(subject=message.photo[-1].file_id)

            await state.update_data(command_name='/photo')
            await message.answer('Select command for your image: \n- /image_ai + prompt\n- /image_resize + "width"x"high"\n- /image_id', reply_markup=kb.exit_keyboard)

        except (Exception,):
            await message.answer('Something gonna wrong, check your input image and try again.')
            try:
                await state.update_data(command_name=None)
                os.remove('work_image.jpg')
            except (Exception,):
                print('Details: All clear.')
