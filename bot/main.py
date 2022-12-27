import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject, Text
from aiogram.types import FSInputFile, KeyboardButton, Message, ReplyKeyboardMarkup
from sqlalchemy.orm import sessionmaker

import config
from db import (get_async_engine, get_current_user_file, get_session_maker,
                get_tg_user, get_user, get_unmarked_file,
                login_user, logout_user, register_user, set_current_user_file,
                set_file_processed)
from middelwares import NewUser
from utils import random_word


bot = Bot(config.BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher()
dp.message.middleware(NewUser())

# keyboards
kb_authorized = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='My Tasks'),
                                               KeyboardButton(text='Exit')]],
                                    resize_keyboard=True)
kb_unauthorized = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Registration'),
                                                 KeyboardButton(text='Login')]],
                                      resize_keyboard=True)

# handlers
@dp.message(Command(commands=['start']))
async def command_start_handler(message: Message, session_maker: sessionmaker) -> None:
    _, authorized_as = await get_tg_user(message.from_user.id, session_maker)
    keyboard = kb_authorized if authorized_as else kb_unauthorized
    await message.answer(f'Hello, <b>{message.from_user.full_name}!</b>',
                         reply_markup=keyboard)


@dp.message(Command(commands=['login']))
async def command_login_handler(message: Message, command: CommandObject,
                                session_maker: sessionmaker) -> None:
    if args := command.args:
        try:
            login, password = args.split()
        except ValueError:
            await message.reply('Failed to parse login/password')
            return
        _, saved_password = await get_user(login, session_maker)
        if password == saved_password:
            await login_user(message.from_user.id, login, session_maker)
            await message.answer(f'You are logged in as <b>{login}</b> now',
                                 reply_markup=kb_authorized)


@dp.message(Text(text='Registration'))
async def registration_handler(message: Message, session_maker: sessionmaker) -> None:
    _, authorized_as = await get_tg_user(message.from_user.id, session_maker)
    if not authorized_as:
        login = random_word(5, 'qwertyuiopasdfghjklzxcvbnm')
        password = random_word(5, '1234567890')
        await register_user(login, password, session_maker)
        await login_user(message.from_user.id, login, session_maker)
        await message.answer('You have succesfully registered\n'
                             f'Your login is <b>{login}</b>\n'
                             f'Your password is <b>{password}</b>',
                             reply_markup=kb_authorized)
    else:
        await message.answer('You need to log out before registeration\n',
                             reply_markup=kb_authorized)


@dp.message(Text(text='Login'))
async def login_handler(message: Message, session_maker: sessionmaker) -> None:
    _, authorized_as = await get_tg_user(message.from_user.id, session_maker)
    if authorized_as:
        await message.answer(f'You are logged in as {authorized_as} now',
                             reply_markup=kb_authorized)
    else:
        await message.answer('Send "/login your_login your_password"',
                             reply_markup=kb_unauthorized)


@dp.message(Text(text='Exit'))
async def exit_handler(message: Message, session_maker: sessionmaker) -> None:
    _, authorized_as = await get_tg_user(message.from_user.id, session_maker)
    if not authorized_as:
        await message.answer('You are not logged in',
                             reply_markup=kb_unauthorized)
    else:
        await logout_user(message.from_user.id, session_maker)
        await message.answer('Now you are logged out',
                             reply_markup=kb_unauthorized)


@dp.message(Text(text='My Tasks'))
async def task_handler(message: Message, session_maker: sessionmaker) -> None:
    _, authorized_as = await get_tg_user(message.from_user.id, session_maker)
    if not authorized_as:
        return
    file = await get_current_user_file(authorized_as, session_maker) or \
        await get_unmarked_file(session_maker)
    if file:
        buttons = []
        file_id, classes = file
        file_id = str(file_id)
        for el in classes.split(', '):
            buttons.append(KeyboardButton(text=el))
        keyboard = ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True)
        image = FSInputFile(os.path.join(config.UPLOAD_FOLDER, file_id))
        await bot.send_photo(chat_id=message.chat.id,
                             photo=image,
                             reply_markup=keyboard)
        await set_current_user_file(file_id, authorized_as, session_maker)
    else:
        await message.answer(f'There is no tasks for you',
                             reply_markup=kb_authorized)


@dp.message()
async def markup_file(message: Message, session_maker: sessionmaker) -> None:
    if not message.text:
        return
    _, authorized_as = await get_tg_user(message.from_user.id, session_maker)
    if not authorized_as:
        return
    file = await get_current_user_file(authorized_as, session_maker) or \
        await get_unmarked_file(session_maker)
    if file and message.text in file[1].split(', '):
        await set_file_processed(file[0], message.text, session_maker)
    await task_handler(message, session_maker)


# bot start
async def main(bot: Bot, dp: Dispatcher) -> None:
    logging.basicConfig(level=logging.INFO)
    async_engine = get_async_engine(config.POSTGRES_URL)
    session_maker = get_session_maker(async_engine)
    await dp.start_polling(bot, session_maker=session_maker)


if __name__ == '__main__':
    try:
        asyncio.run(main(bot, dp))
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
