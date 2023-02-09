import logging
import json

import db
from aiogram import Bot, Dispatcher, executor, types
from config import data
API_TOKEN = data['token']
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message : types.Message):
    db.create_user(message.chat.id)
    if len(message.text.split()) > 1:
        try:
            ref_id = int(message.text.split()[1])
            db.add_ref(ref_id)
        except ValueError:
            pass
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text='Русский язык', callback_data='language_ru'))
    kb.add(types.InlineKeyboardButton(text='English language', callback_data='language_en'))
    await message.answer(data['start_message'], reply_markup=kb)
@dp.message_handler(commands=['menu'])
async def menu(message : types.Message):
    lang= db.get_language(message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text=data[f'balance_{lang}'], callback_data='balance'))
    kb.add(types.InlineKeyboardButton(text=data[f'referal_{lang}'] , callback_data='referal'))
    kb.add(types.InlineKeyboardButton(text=data[f'settings_{lang}'] , callback_data='settings'))
    kb.add(types.InlineKeyboardButton(text=data[f'FAQ_{lang}'] , callback_data='FAQ'))
    kb.add(types.InlineKeyboardButton(text=data[f'donate_{lang}'] , callback_data='donate'))
    await message.answer(data[f'menu_{lang}'], reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data == 'menu')
async def back_to_menu(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text=data[ f'balance_{lang}' ] , callback_data='balance'))
    kb.add(types.InlineKeyboardButton(text=data[ f'referal_{lang}' ] , callback_data='referal'))
    kb.add(types.InlineKeyboardButton(text=data[ f'settings_{lang}' ] , callback_data='settings'))
    kb.add(types.InlineKeyboardButton(text=data[ f'FAQ_{lang}' ] , callback_data='FAQ'))
    kb.add(types.InlineKeyboardButton(text=data[ f'donate_{lang}' ] , callback_data='donate'))
    text = data[f'menu_{lang}']
    await callback_query.message.edit_text(text=text, reply_markup=kb)

@dp.callback_query_handler(lambda query: query.data == 'balance')
async def show_balance(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text=data[f'back_button_{lang}'], callback_data='menu'))
    balance = db.get_balance(callback_query.message.chat.id)
    daily_balance = db.get_daily_balance(callback_query.message.chat.id)
    refs = db.get_refs(callback_query.message.chat.id)
    text = data[f'balance_1row_{lang}'] + str(balance) + '\n' + data[f'balance_2row_{lang}'] + str(daily_balance) + '\n' + data[f'balance_3row_{lang}'] + str(refs*100) + '\n'+ data[f'balance_4row_{lang}']
    await callback_query.message.edit_text(text=text, reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data == 'referal')
async def show_referals(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text=data[f'back_button_{lang}'], callback_data='menu'))
    id = callback_query.message.chat.id
    refs = db.get_refs(callback_query.message.chat.id)
    link = data['bot_start_link'] + str(id)
    text = data[f'referal_1row_{lang}'] + '\n' + data[f'referal_2row_{lang}'] + str(id) + '\n' + data[f'referal_3row_{lang}'] + str(refs) + '\n' + data[f'referal_4row_{lang}'] + link
    await callback_query.message.edit_text(text=text, reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data == 'FAQ')
async def show_FAQ(callback_query : types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text=data[f'back_button_{lang}'] , callback_data='menu'))
    text = data[f'FAQ_show_{lang}']
    await callback_query.message.edit_text(text=text , reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data == 'settings')
async def show_settings(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    image_size = db.get_image_size(callback_query.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text = f'{image_size}x{image_size}', callback_data=f'change_image_size_{image_size}'))
    kb.add(types.InlineKeyboardButton(text = data[lang], callback_data='change_language'))
    kb.add(types.InlineKeyboardButton(text=data[f'back_button_{lang}'] , callback_data='menu'))
    await callback_query.message.edit_text(text = data[f'settings_show_{lang}'], reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data.startswith(f'change_image_size_'))
async def change_image_size(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    call_data = callback_query.data.split('_')[-1]
    if call_data == '256':
        image_size = '512'
    elif call_data == '512':
        image_size = '1024'
    elif call_data == '1024':
        image_size = '256'
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(text=f'{image_size}x{image_size}' , callback_data=f'change_image_size_{image_size}'))
    kb.add(types.InlineKeyboardButton(text=data[ lang ] , callback_data='change_language'))
    kb.add(types.InlineKeyboardButton(text=data[f'back_button_{lang}'] , callback_data='menu'))
    db.change_image_size(callback_query.message.chat.id, int(image_size))
    await callback_query.message.edit_text(text = data[f'settings_show_{lang}'], reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data == 'change_language')
async def change_language(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    if lang == 'en':
        lang = 'ru'
    elif lang == 'ru':
        lang = 'en'
    db.set_language(callback_query.message.chat.id, lang)
    image_size = db.get_image_size(callback_query.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(text=f'{image_size}x{image_size}' , callback_data=f'change_image_size_{image_size}'))
    kb.add(types.InlineKeyboardButton(text=data[ lang ] , callback_data='change_language'))
    kb.add(types.InlineKeyboardButton(text=data[ f'back_button_{lang}' ] , callback_data='menu'))
    await callback_query.message.edit_text(text=data[ f'settings_show_{lang}' ] , reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data.startswith('language_'))
async def language_set(callback_query: types.CallbackQuery):
    await callback_query.answer()
    db.set_language(callback_query.message.chat.id, callback_query.data.split('_')[-1])
    if not (await check(callback_query.message)):
        await check_subscribe(callback_query.message)
async def check_subscribe(message : types.Message):
    lang = db.get_language(message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text = data[f'i_subscribed_{lang}'], callback_data='check_subscribe'))
    await message.answer(data[f'offer_subscribe_{lang}'], reply_markup=kb)

@dp.callback_query_handler(lambda query: query.data == 'check_subscribe')
async def check(message : types.Message):
    lang = db.get_language(message.chat.id)
    channel = data['channel']
    member = await bot.get_chat_member(chat_id=channel,user_id=message.chat.id)
    if isinstance(member,types.ChatMemberLeft):
        await message.answer('You are not subscribed to the channel')
        return False
    else:
        await message.edit_text(text=data[f'thanks_for_subscribe_{lang}'], reply_markup=None)
        return True

if __name__ == '__main__':
    db.start()
    executor.start_polling(dp, skip_updates=True)