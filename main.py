import sys
import asyncio
import logging
from config import dp, bot

from handlers import router_handler


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.include_routers(router_handler)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
