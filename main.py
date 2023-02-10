import logging

import chat_gpt
from PyEasyQiwi import QiwiConnection
import db
from aiogram import Bot, Dispatcher, executor, types
from config import data
from apscheduler.schedulers.asyncio import AsyncIOScheduler
API_TOKEN = data['token']
QIWI_token = data['qiwi_token']
conn = QiwiConnection(QIWI_token)
logging.basicConfig(level=logging.INFO)
job_defaults = {
    'coalesce': False,
    'max_instances': 30
}
scheduler = AsyncIOScheduler(job_defaults=job_defaults)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message : types.Message):

    if len(message.text.split()) > 1:
        try:
            ref_id = int(message.text.split()[1])
            db.create_user(message.chat.id, ref_id)
        except ValueError:
            pass
    else:
        db.create_user(message.chat.id , 0)
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
@dp.message_handler(commands=['image'])
async def image(message : types.Message):
    lang =db.get_language(message.chat.id)
    prompt = message.text[6:]
    size = db.get_image_size(message.chat.id)
    if db.check_subscription(message.chat.id):
        response = await chat_gpt.create_image(prompt, size)
    elif db.get_balance(message.chat.id) >= data[f'{size}image']:
        response = await chat_gpt.create_image(prompt , size)
        db.spend_balance(message.chat.id , data[ f'{size}image' ])
    else:
        await message.answer(data[f'not_enough_money_{lang}'])
        return

    await message.answer_photo(photo=response)
@dp.message_handler()
async def messages(message:types.Message):
    lang = db.get_language(message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text = data[f'break_dialog_{lang}'], callback_data='break_dialog'))
    prompt = message.text
    if db.get_context_status(message.chat.id):
        text = db.get_prompt(message.chat.id) + '\n' + prompt
        if db.check_subscription(message.chat.id):
            response = await chat_gpt.text(text)
            await message.answer(response)
            db.add_to_prompt(message.chat.id,prompt)
            return
        else:
            price = len(text.split()) * data['1token_price']
            if db.get_balance(message.chat.id) >= price:
                response = await chat_gpt.text(text)
                await message.answer(response)
                db.add_to_prompt(message.chat.id, prompt)
                db.spend_balance(message.chat.id, price)
            else:
                await message.answer(data[f'not_enough_money_{lang}'])
    else:
        if db.check_subscription(message.chat.id):
            response = await chat_gpt.text(prompt)
            await message.answer(response)
        else:
            price = len(prompt.split()) * data['1token_price']
            if db.get_balance(message.chat.id) >= price:
                response = await chat_gpt.text(prompt)
                await message.answer(response)
                db.spend_balance(message.chat.id, price)
            else:
                await message.answer(data[f'not_enough_money_{lang}'])



@dp.callback_query_handler(lambda query: query.data== 'break_dialog')
async def break_dialog(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    db.break_prompt(callback_query.message.chat.id)
    await callback_query.message.answer(data[f'dialog_restarted_{lang}'])
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
@dp.callback_query_handler(lambda query: query.data == 'donate')
async def donation(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    if db.check_subscription(callback_query.message.chat.id):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text=data[ f'back_button_{lang}' ] , callback_data='menu'))
        await callback_query.message.edit_text(text = data[f'already_subscribed_{lang}'], reply_markup=kb)
        return
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text= 'Qiwi', callback_data='payment_qiwi'))
    kb.add(types.InlineKeyboardButton(text=data[f'back_button_{lang}'], callback_data='menu'))
    await callback_query.message.edit_text(text=data[f'offer_donation_{lang}'], reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data.startswith('payment_'))
async def offer_payment(callback_query: types.CallbackQuery):
    payment = callback_query.data.split('_')[-1]
    lang = db.get_language(callback_query.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text=data[ f'back_button_{lang}' ] , callback_data='donate'))
    kb.add(types.InlineKeyboardButton(text=f'{data["price"]} RUB', callback_data= f'create_payment_{payment}'))
    await callback_query.message.edit_text(text=data[f'offer_to_pay_{lang}'], reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data.startswith('create_payment_'))
async def create_payment(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    payment = callback_query.data.split('_')[-1]
    if payment == 'qiwi':
        if db.check_existing_payments(callback_query.message.chat.id):
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(text = data[f'restart_payment_{lang}'], callback_data=f'restart_payment_{payment}'))
            await callback_query.message.answer(data[f'payment_exists_{lang}'],reply_markup=kb)
            return
        pay_url, bill_id, response=conn.create_bill(value=data['price'], description=str(callback_query.message.chat.id))
        db.create_payment(callback_query.message.chat.id, bill_id)
        text = data[f'go_payment_{lang}']
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='QIWI', url=pay_url))
        kb.add(types.InlineKeyboardButton(text=data[f'check_payment_{lang}'], callback_data=f'check_payment_{bill_id}'))
        await callback_query.message.answer(text,reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data.startswith('check_payment'))
async def check_payment(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    bill_id = callback_query.data.split('_')[-1]
    status, response =conn.check_bill(bill_id)
    if status == 'PAID':
        await callback_query.message.edit_text(text=data[f'successful_payment_{lang}'], reply_markup=None)
        db.change_payment_status(callback_query.message.chat.id,bill_id, 'paid')
        db.add_subscription(callback_query.message.chat.id)
    else:
        await callback_query.answer(data[f'unsuccessful_payment_{lang}'])

@dp.callback_query_handler(lambda query: query.data.startswith('restart_payment_'))
async def restart_payment(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    db.restart_payments(callback_query.message.chat.id)
    await create_payment(callback_query)
@dp.callback_query_handler(lambda query: query.data == 'balance')
async def show_balance(callback_query: types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text=data[f'back_button_{lang}'], callback_data='menu'))
    balance = db.get_balance(callback_query.message.chat.id)
    daily_balance = db.get_daily_balance(callback_query.message.chat.id)
    refs = db.get_refs(callback_query.message.chat.id)
    text = data[f'balance_1row_{lang}'] + str(balance) + '\n' + data[f'balance_2row_{lang}'] + str(daily_balance) + '\n' + data[f'balance_3row_{lang}'] + str(refs*100) + '\n'+ data[f'balance_4row_{lang}']
    if db.check_subscription(callback_query.message.chat.id):
        text = data[f'active_subscription_{lang}'] + text
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
    context_status = db.get_context_status(callback_query.message.chat.id)
    if context_status:
        text = '✅Context'
    else:
        text = '❌Context'
    kb.add(types.InlineKeyboardButton(text= text, callback_data= 'change_context'))
    kb.add(types.InlineKeyboardButton(text=data[f'back_button_{lang}'] , callback_data='menu'))
    await callback_query.message.edit_text(text = data[f'settings_show_{lang}'], reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data == 'change_context')
async def change_context(callback_query:types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    image_size = db.get_image_size(callback_query.message.chat.id)
    status = db.get_context_status(callback_query.message.chat.id)
    new_status = int(not status)
    db.change_context_status(callback_query.message.chat.id, new_status)
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(text=f'{image_size}x{image_size}' , callback_data=f'change_image_size_{image_size}'))
    kb.add(types.InlineKeyboardButton(text=data[ lang ] , callback_data='change_language'))
    context_status = db.get_context_status(callback_query.message.chat.id)
    if context_status:
        text = '✅Context'
    else:
        text = '❌Context'
    kb.add(types.InlineKeyboardButton(text=text , callback_data='change_context'))
    kb.add(types.InlineKeyboardButton(text=data[ f'back_button_{lang}' ] , callback_data='menu'))
    db.change_image_size(callback_query.message.chat.id , int(image_size))
    await callback_query.message.edit_text(text=data[ f'settings_show_{lang}' ] , reply_markup=kb)
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
    context_status = db.get_context_status(callback_query.message.chat.id)
    if context_status:
        text = '✅Context'
    else:
        text = '❌Context'
    kb.add(types.InlineKeyboardButton(text=text , callback_data='change_context'))
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
    context_status = db.get_context_status(callback_query.message.chat.id)
    if context_status:
        text = '✅Context'
    else:
        text = '❌Context'
    kb.add(types.InlineKeyboardButton(text=text , callback_data='change_context'))
    kb.add(types.InlineKeyboardButton(text=data[ f'back_button_{lang}' ] , callback_data='menu'))
    await callback_query.message.edit_text(text=data[ f'settings_show_{lang}' ] , reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data.startswith('language_'))
async def language_set(callback_query: types.CallbackQuery):
    await callback_query.answer()
    db.set_language(callback_query.message.chat.id, callback_query.data.split('_')[-1])
    await check_subscribe(callback_query.message)
async def check_subscribe(message : types.Message):
    lang = db.get_language(message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text = data[f'i_subscribed_{lang}'], callback_data='check_subscribe'))
    await message.answer(data[f'offer_subscribe_{lang}'], reply_markup=kb)

@dp.callback_query_handler(lambda query: query.data == 'check_subscribe')
async def check(callback_query : types.CallbackQuery):
    lang = db.get_language(callback_query.message.chat.id)
    channel = data['channel']
    member = await bot.get_chat_member(chat_id=channel,user_id=callback_query.message.chat.id)
    if isinstance(member,types.ChatMemberLeft):
        await callback_query.message.answer('You are not subscribed to the channel')
        return False
    else:
        await callback_query.message.edit_text(text=data[f'thanks_for_subscribe_{lang}'], reply_markup=None)
        return True

if __name__ == '__main__':
    db.start()
    scheduler.add_job(db.new_balance , 'cron' , hour=0)
    executor.start_polling(dp, skip_updates=True)