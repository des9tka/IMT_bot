import asyncio
import logging
import sys

from config import dp, bot
from handlers.message_handler import router_message_handler
from handlers.callbackquery_handler import router_callback_query_handler


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.include_routers(router_message_handler, router_callback_query_handler)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
