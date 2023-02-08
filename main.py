import logging
import json

import db
from db import *
from aiogram import Bot, Dispatcher, executor, types
with open('config.json', 'r', encoding='utf8') as file:
    data = json.load(file)
API_TOKEN = data['token']
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message : types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Русский язык', callback_data='language_ru'))
    kb.add(types.InlineKeyboardButton(text='English language', callback_data='language_en'))
    await message.answer(data['start_message'], reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data.startswith('language_'))
async def language_set(callback_query: types.CallbackQuery):
    await callback_query.answer()
    db.set_language(callback_query.message.chat.id, callback_query.data.split('_')[-1])
async def check_subscribe(message : types.Message):
    lang = db.get_language(message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text = data[f'i_subscribed_{lang}'], callback_data='check_subscribe'))
    await message.answer(data[f'offer_subscribe_{lang}'], reply_markup=kb)

@dp.callback_query_handler(lambda query: query.data == 'check_subscribe')
async def check(message : types.Message):
    channel = data['channel']
    member = await bot.get_chat_member(chat_id=channel,user_id=message.chat.id)
    if isinstance(member,types.ChatMemberLeft):
        return False
    else:
        return True

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)