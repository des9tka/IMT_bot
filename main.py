import asyncio
import logging
import sys

from config import dp, bot
from handlers import router_message_handler, router_callback_query_handler, router_sticker_handler, router_voice_handler, router_video_handler, router_audio_handler, router_photo_handler


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.include_routers(router_message_handler, router_callback_query_handler, router_sticker_handler, router_voice_handler, router_video_handler, router_audio_handler, router_photo_handler)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
