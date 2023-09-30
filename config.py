import dotenv
import os
from aiogram import Bot, Dispatcher

dotenv.load_dotenv()

TG_TOKEN = os.environ.get('TG_TOKEN')
BARD_TOKEN = os.environ.get('BARD_TOKEN')

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(Bot=bot)
