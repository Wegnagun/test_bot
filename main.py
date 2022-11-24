import os
import sys
from datetime import datetime

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

COLON = '\U0000A789'
BOT_TOKEN = os.getenv('TOKEN')
BOTS_COMMAND = [
    '/start', '/help',
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


def check_tokens() -> bool:
    """ Проверяем доступность переменных окружения. """
    return all([BOT_TOKEN])


async def save_user_foto(user_id):
    filename = datetime.now().strftime(f"%m-%d-%Y_%H-%M")   #  верни бля двоеточие во времени!!!!
    user_profile_photo = await dp.bot.get_user_profile_photos(user_id)
    file_name = f"./media/{filename}_{user_id}.jpg"
    os.makedirs(os.path.dirname('./media/'), exist_ok=True)
    if user_profile_photo.total_count != 0:
        await user_profile_photo.photos[0][-1].download(
            destination_file=file_name
        )
    await add_text_to_image(file_name, user_id)


async def add_text_to_image(file_name, user_id):
    default_image = Image.open(file_name)
    font = ImageFont.truetype('Lobster-Regular.ttf', size=45)
    final_image = ImageDraw.Draw(default_image)
    final_image.text(
        (60, 550),
        'Фоточка, а ней красоточка!',
        fill='#fffcfe',
        font=font,
        stroke_width=2,
        stroke_fill='#030203'
    )
    default_image.save(file_name)
    photo = open(file_name, 'rb')
    await bot.send_photo(chat_id=user_id, photo=photo)


@dp.message_handler(lambda message: message.text not in BOTS_COMMAND)
async def unknown_command(message: types.Message):
    await message.reply('Я не знаю такую команду(\n'
                        'напиши /help чтобы узнать, что я умею =)')


@dp.message_handler(commands='help')
async def give_help(message: types.Message):
    """Функция реакции на команду /help."""
    await message.reply(f'Значится так, я умею в следующие команды:\n'
                        f'/follow - подписаться на уведомления\n'
                        f'/help - узнать доступные команды\n')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    """Функция реакции на команду /start."""
    user_id = message.from_user.id
    await save_user_foto(user_id)
    me = await bot.get_me()
    await message.reply(f'\U0001F916 Привет, {message.from_user.full_name}, '
                        f'меня зовут {me.full_name}!\n'
                        f'Я делаю подписи к фото =)')


if __name__ == '__main__':
    if not check_tokens():
        sys.exit('Ошибка, проверьте токены в config.py')
    executor.start_polling(dp, skip_updates=True)
