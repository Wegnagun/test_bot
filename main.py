import os
import sys
from datetime import datetime
from typing import BinaryIO
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv
from aiogram.types import (
    ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, callback_query
)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')
BOTS_COMMAND = [
    '/start', '/help', 'Загрузить своё фото'
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class UploadPhotoForm(StatesGroup):
    photo = State()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Отменено.', reply_markup=types.ReplyKeyboardRemove())


def check_tokens() -> bool:
    """ Проверяем доступность переменных окружения. """
    return all([BOT_TOKEN])


def add_text_to_image(file_name: str, text: str) -> BinaryIO:
    image = Image.open(file_name)
    font = ImageFont.truetype('Lobster-Regular.ttf', size=45)
    draw = ImageDraw.Draw(image)
    width_image, height_image = image.size
    width_text, height_text = draw.textsize(text, font=font)
    draw.text(
        ((width_image - width_text) / 2 + 1, ((height_image / 10) * 9) + 1),
        text,
        fill='#fffcfe',
        font=font,
        stroke_width=2,
        stroke_fill='#030203'
    )
    image.save(file_name)
    photo = open(file_name, 'rb')
    return photo


def get_random_text() -> str:
    pass


async def save_user_start_foto(user_id: int, text: str) -> None:
    filename = datetime.now().strftime(f"%m-%d-%Y_%H-%M")
    user_profile_photo = await dp.bot.get_user_profile_photos(user_id)
    file_name = f"./media/{filename}_{user_id}.jpg"
    os.makedirs(os.path.dirname('./media/'), exist_ok=True)
    if user_profile_photo.total_count != 0:
        await user_profile_photo.photos[0][-1].download(
            destination_file=file_name
        )
    photo = add_text_to_image(file_name, text)
    await bot.send_photo(chat_id=user_id, photo=photo)


async def save_user_foto(user_id: int, text: str, photo) -> None:
    await photo.download(
        destination_file='C:/Antony/py_projects/qr_code_bot/photos/ggg.jpg')
    filename = datetime.now().strftime(f"%m-%d-%Y_%H-%M")
    file_name = f"./media/{filename}_{user_id}.jpg"
    os.makedirs(os.path.dirname('./media/'), exist_ok=True)
    photo = add_text_to_image(file_name, text)
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
    text = 'Хоба шо могу! =)'
    bot_keyboard = InlineKeyboardMarkup(
        row_width=1,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    upload_button = InlineKeyboardButton(
        text="Загрузить своё фото",
        callback_data='upload_image'
    )
    bot_keyboard.add(upload_button)
    me = await bot.get_me()
    await save_user_start_foto(user_id, text)
    await message.reply(
        f'\U0001F916 Привет, {message.from_user.full_name}, '
        f'меня зовут {me.full_name}!\n'
        f'Я делаю подписи к фото =)', reply_markup=bot_keyboard,
    )


@dp.callback_query_handler(lambda c: c.data == 'upload_image')
async def process_photo(callback_query: types.CallbackQuery):
    # photo = message.photo[-1]
    # await save_user_foto(callback_query.from_user.id, 'hubabuba', photo)
    await bot.send_message(
        callback_query.from_user.id, "Жду Ваше изображение!"
    )
    await UploadPhotoForm.photo.set()


@dp.message_handler(lambda message: message.photo is None, state=UploadPhotoForm.photo)
async def process_photo_invalid(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await bot.send_message(callback_query.from_user.id, "Фотография не найдена в сообщении!")


@dp.message_handler(lambda message: message.photo is not None, state=UploadPhotoForm.photo)
async def process_photo(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await bot.send_message(callback_query.from_user.id, "Фотография успешно загружена!")


if __name__ == '__main__':
    if not check_tokens():
        sys.exit('Ошибка, проверьте токены в config.py')
    executor.start_polling(dp, skip_updates=True)
