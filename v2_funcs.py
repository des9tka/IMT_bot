"""Screenshot by pyautogui"""
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
