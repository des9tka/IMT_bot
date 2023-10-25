"""Screenshot by pyautogui v2"""
# pyautogui.press('win')
        # time.sleep(2)
        # keyboard.write('Snipping Tool')
        # time.sleep(2)
        # keyboard.press('enter')
        # time.sleep(2)
        #
        # try:
        #     locate = pyautogui.locateCenterOnScreen('commands_images/full_mode_image.png')
        #     if not locate:
        #         raise Exception('No full screenshot mode.')
        #
        # except (Exception,):
        #     await message.answer('No full screenshot mode in snipping tool. Active it for proper working.')
        #
        # locate = pyautogui.locateCenterOnScreen('commands_images/add_screenshot.png')
        # pyautogui.moveTo(locate)
        # time.sleep(1)
        # pyautogui.click()
        # time.sleep(2)
        #
        # buffer_img = PIL.ImageGrab.grabclipboard()
        # np_img = np.array(buffer_img)
        #
        # img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
        # cv2.imwrite('screenshot.png', img)
        #
        # screenshot = types.FSInputFile('screenshot.png')
        #
        # if len(list(filter(is_not_empty, query))) == 0 or list(filter(is_not_empty, query))[0] == '1':
        #     await bot.send_photo(chat_id=message.chat.id, photo=screenshot)
        # elif list(filter(is_not_empty, query))[0] == '2':
        #     await bot.send_document(chat_id=message.chat.id, document=screenshot)
        #
        # os.remove('screenshot.png')
        # await message.answer(f'*Additional: {close_app("Snipping Tool")}')


"""Callback close asking"""
# elif 'close_sure_yes' in callback.data:
    # app = callback.message.text.split(' ')[1]
    # await callback.message.answer(close_app(app))
    #
    # elif 'close_sure_no' in callback.data:
    # await callback.message.answer('Application closure rejected.')


"""Open app v2"""
# processes = psutil.process_iter()
    # for process in processes:
    #     if app.lower() in process.name():
    #         windows = win32gui.EnumWindows()
    #         for window in windows:
    #             if app.lower() in win32gui.GetWindowText(window):
    #                 win32gui.ShowWindow(window, win32con.SW_MAXIMIZE)
    #                 break
    #         return f'{app.capitalize()} was successfully open.'
    #
    # for process in processes:
    #     if app.lower() not in process.name():
    #         pyautogui.hotkey("win")
    #         time.sleep(1)
    #         pyautogui.write(app)
    #         time.sleep(1)
    #         pyautogui.press("enter")
    #         time.sleep(5)
    #
    #         return f'{app.capitalize()} was successfully open.'
    # return f'{app.capitalize()} wasnt find, not global available, or has wrong name input (You can use /task_manager for listing all tasks).'


"""Format answer"""
# def format_answer(answer):
#     answer = answer.replace('\n', ' ')
#     answer = answer.replace('*', '')
#     return answer


"""Generate images"""
# def generate_image(prompt, num_image=1, size='512x512', output_format='url'):
#     """
#     params:
#         prompt (str):
#         num_image (int):
#         size (str):
#         output_format (str):
#     """
#     try:
#         images = []
#         response = openai.Image.create(
#             prompt=prompt,
#             n=num_image,
#             size=size,
#             response_format=output_format
#         )
#         if output_format == 'url':
#             for image in response['data']:
#                 images.append(image.url)
#         elif output_format == 'b64_json':
#             for image in response['data']:
#                 images.append(image.b64_json)
#         return {'created': datetime.datetime.fromtimestamp(response['created']), 'images': images}
#     except InvalidRequestError as e:
#         print(e)


"""Callback generate image"""
# elif 'image_size_kb' in callback.data:
    #     if '1' in callback.data:
    #         image['size'] = '256x256'
    #     elif '2' in callback.data:
    #         image['size'] = '512x512'
    #     elif '3' in callback.data:
    #         image['size'] = '1024x1024'
    #     await callback.message.answer('Let`s choose a number of images:', reply_markup=kb.image_numbers_kb)
    #
    # elif 'image_numbers_kb' in callback.data:
    #     if '1' in callback.data:
    #         image['number'] = 1
    #     elif '2' in callback.data:
    #         image['number'] = 2
    #     elif '3' in callback.data:
    #         image['number'] = 3
    #     elif '4' in callback.data:
    #         image['number'] = 4
    #     await callback.message.answer('Do request to AI', reply_markup=kb.image_request_kb)
    #
    # elif 'image_request_response' in callback.data:
    #     await callback.message.answer(f'Request: {image["prompt"], image["size"], image["number"]}')
    #     await callback.message.answer('Request in development...')
