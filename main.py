import os
import sys

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


def check_tokens() -> bool:
    """ Проверяем доступность переменных окружения. """
    return all([BOT_TOKEN])

def main():
    pass


if __name__ == '__main__':
    if not check_tokens():
        sys.exit('Ошибка, проверьте токены в config.py')
    main()
    executor.start_polling(dp, skip_updates=True)
