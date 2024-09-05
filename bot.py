from aiogram.types import Message, InlineKeyboardButton
from filterss.check_sub_channel import IsCheckSubChannels
from states.reklama import Adverts
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time 
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from data import config
import asyncio
import logging
import sys
from menucommands.set_bot_commands import set_default_commands
from baza.sqlite import Database
from filterss.admin import IsBotAdminFilter
from keyboard_buttons import admin_keyboard
from aiogram.fsm.context import FSMContext
from nomoz_vaqti import vaqti, mintaqalar
from aiogram.types import ReplyKeyboardRemove

# Konfiguratsiya ma'lumotlari
ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS

# Dispatcher yaratish
dp = Dispatcher()

# /start komandasi uchun handler
@dp.message(CommandStart())
async def start_command(message: Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        # Foydalanuvchini bazaga qo'shish
        db.add_user(full_name=full_name, telegram_id=telegram_id) 
        await message.answer(
            text="Assalomu alaykum, botimizga xush kelibsiz. Bu bot orqali siz namoz o'qishni o'rganishingiz mumkin.",
            reply_markup=admin_keyboard.start_buttonnew
        )
    except:
        await message.answer(
            text="Assalomu alaykum, botimizga xush kelibsiz. Bu bot orqali siz namoz o'qishni o'rganishingiz mumkin.",
            reply_markup=admin_keyboard.start_buttonnew
        )

# Kanalga obuna bo'lishni tekshirish
@dp.message(IsCheckSubChannels())
async def kanalga_obuna(message: Message):
    text = ""
    inline_channel = InlineKeyboardBuilder()
    for index, channel in enumerate(CHANNELS):
        ChatInviteLink = await bot.create_chat_invite_link(channel)
        inline_channel.add(InlineKeyboardButton(text=f"{index+1}-kanal", url=ChatInviteLink.invite_link))
    inline_channel.adjust(1, repeat=True)
    button = inline_channel.as_markup()
    await message.answer(f"{text} kanallarga a'zo bo'ling", reply_markup=button)

# Admin uchun menyu
@dp.message(Command("admin"), IsBotAdminFilter(ADMINS))
async def is_admin(message: Message):
    await message.answer(text="Admin menu", reply_markup=admin_keyboard.admin_button)

# Foydalanuvchilar sonini ko'rsatish
@dp.message(F.text == "Foydalanuvchilar soni", IsBotAdminFilter(ADMINS))
async def users_count(message: Message):
    counts = db.count_users()
    text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
    await message.answer(text=text)

# Reklama yuborish uchun holatni o'rnatish
@dp.message(F.text == "Reklama yuborish", IsBotAdminFilter(ADMINS))
async def advert_dp(message: Message, state: FSMContext):
    await state.set_state(Adverts.adverts)
    await message.answer(text="Reklama yuborishingiz mumkin!")

# Reklamani foydalanuvchilarga yuborish
@dp.message(Adverts.adverts)
async def send_advert(message: Message, state: FSMContext):
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = db.all_users_id()
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0], from_chat_id=from_chat_id, message_id=message_id)
            count += 1
        except:
            pass
        time.sleep(0.01)
    
    await message.answer(f"Reklama {count}ta foydalanuvchiga yuborildi")
    await state.clear()

# Namoz vaqtlarini ko'rsatish
mintaqalar = {
    "Toshkent": 27,
    "Andijon": 1,
    "Buxoro": 4,
    "Guliston": 5,
    "Samarqand": 18,
    "Namangan": 15,
    "Navoiy": 14,
    "Jizzax": 9,
    "Nukus": 16,
    "Qarshi": 25,
    "Qo'qon": 26,
    "Xiva": 21,
    "Marg'ilon": 13
}

@dp.message(F.text.in_(mintaqalar.keys()))
async def ism_func(message: Message):
    await message.delete()
    try:
        vaqtlar = vaqti(mintaqalar.get(message.text))
        text = (
            f"""{vaqtlar[1]} - {vaqtlar[-1]} | {vaqtlar[2]} \n
🌅Bomdod: {vaqtlar[3]}\n
🌄Quyosh chiqishi : {vaqtlar[4]}\n
☀️Peshin vaqti : {vaqtlar[5]}\n
☀️Asr vaqti: {vaqtlar[6]}\n
🌜Shom vaqti {vaqtlar[7]}\n
🌕Xufton vaqti: {vaqtlar[8]}"""
        )
        await message.answer(text=text, reply_markup=admin_keyboard.Admin)
    except:
        await message.answer(text="Xatolik yuz berdi")

# Namoz vaqtlarini tanlash
@dp.message(F.text == "⌛️NAMOZ VAQTLARI⌛️")
async def namoz_vaqti(message: Message):
    await message.delete()
    await message.answer(text="Hududingizni tanlang", reply_markup=admin_keyboard.hudud)
    await message.delete()

# Bosh menyu
@dp.message(F.text == "🏠 Bosh Menyu")
async def orqa(message: Message):
    await message.answer(text="Menyulardan birini tanlang", reply_markup=admin_keyboard.start_buttonnew)
    await message.delete()

from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
ITEMS_PER_PAGE = 20

def get_paginated_keyboard(page=0):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    surah_page = admin_keyboard.SURAH_NAMES[start:end]

    keyboard_builder = InlineKeyboardBuilder()
    
    for name, callback_data in surah_page:
        keyboard_builder.button(text=name, callback_data=callback_data)
    
    keyboard_builder.adjust(2)  # Adjust buttons in rows of 2

    # Add Previous and Next buttons in a new row
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(("⬅️ Oldinga", f"page_{page-1}"))
    if end < len(admin_keyboard.SURAH_NAMES):
        pagination_buttons.append(("➡️ Keyingi", f"page_{page+1}"))
    
    # If there are pagination buttons, add them in a new row
    if pagination_buttons:
        for text, callback_data in pagination_buttons:
            keyboard_builder.button(text=text, callback_data=callback_data)
        keyboard_builder.adjust(2)  # Ensure pagination buttons are in a new row

    return keyboard_builder.as_markup()

@dp.message(F.text == "QURON")
async def show_surah_list(message: Message):
    keyboard = get_paginated_keyboard(page=0)
    await message.answer("Tanlang:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("page_"))
async def paginate_callback(query: CallbackQuery):
    page = int(query.data.split("_")[1])
    keyboard = get_paginated_keyboard(page)
    await query.message.edit_reply_markup(reply_markup=keyboard)

@dp.callback_query(F.data == "orqaga_qaytamiz")
async def qaytar_handler(callback: CallbackQuery):
    await callback.message.answer(text="Menyulardan birini tanlang", reply_markup=get_paginated_keyboard(page=0))
    await callback.message.delete()

#fotiha surasi
@dp.callback_query(F.data == "fotiha_quron")
async def fotiha(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Makkiy, 7 oyatdan iborat
<a href='https://t.me/mukammal_namoz/3'>Bizning kanal📢</a> """,
   reply_markup=admin_keyboard.orqaga_qayt,
        parse_mode="HTML"
    )
    
#baqara
@dp.callback_query(F.data == "baqara")
async def baqar(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=""" 
 Makkiy, 286 oyatdan iborat                                  
<a href='https://t.me/namoz_uqishni_urganish_Kanal/77'>Bizning kanal📢</a>  """,
 parse_mode="html", 
reply_markup=admin_keyboard.orqaga_qayt
) 

#Oli Imron 
@dp.callback_query(F.data == "oli_imron")
async def oli_imron(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
 Makkiy, 200 oyatdan iborat 
    <a href='https://t.me/namoz_uqishni_urganish_Kanal/78'>Bizning kanal📢</a>  """,
 parse_mode="html",  # To'g'ri joylash
reply_markup=admin_keyboard.orqaga_qayt
) 

#niso
@dp.callback_query(F.data == "niso")
async def niso(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 200 oyatdan iborat 
<a href='https://t.me/namoz_uqishni_urganish_Kanal/79'>Bizning kanal📢</a> """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "moida")
async def peshin(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=""" 
Makkiy, 120 oyatdan iborat 
    <a href='https://t.me/namoz_uqishni_urganish_Kanal/83'>Bizning kanal📢</a> """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "anom")
async def moida(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 165 oyatdan iborat
    <a href='https://t.me/namoz_uqishni_urganish_Kanal/84'>Bizning kanal📢</a> """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "arof")
async def arof(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 206 oyatdan iborat
    <a href='https://t.me/namoz_uqishni_urganish_Kanal/85'>Bizning kanal📢</a> """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "anfol")
async def anfol(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 75 oyatdan iborat
            <a href='https://t.me/namoz_uqishni_urganish_Kanal/86'>Bizning kanal📢</a> """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "tavba")
async def tavba(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 129 oyatdan iborat
    <a href='https://t.me/namoz_uqishni_urganish_Kanal/95'>Bizning kanal📢</a> """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "yunus")
async def yunus(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 109 oyatdan iborat
        <a href='https://t.me/namoz_uqishni_urganish_Kanal/87'>Bizning kanal📢</a> """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "hud")
async def hud(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 123 oyatdan iborat
    <a href='https://t.me/namoz_uqishni_urganish_Kanal/87'>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "yusuf")
async def hud(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 111 oyatdan iborat
    <a href='https://t.me/namoz_uqishni_urganish_Kanal/89'>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

#rod
@dp.callback_query(F.data == "rod")
async def hud(callback: CallbackQuery):
    await callback.message.delete()
    parse_mode= "html"
    await callback.message.answer(text="""    
Makkiy, 43 oyatdan iborat
    <a href='https://t.me/namoz_uqishni_urganish_Kanal/90'>Bizning kanal📢</a>
        """,
        reply_markup=admin_keyboard.orqaga_qayt
    )
#ibrohim   
@dp.callback_query(F.data == "ibrohim")
async def ibrohim(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 52 oyatdan iborat
        <a href='https://t.me/namoz_uqishni_urganish_Kanal/90'>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "hijr")
async def hijr(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 99 oyatdan iborat                                  
    <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "nahl")
async def nahl(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 128 oyatdan iborat
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "isro")
async def isro(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 111 oyatdan iborat
    <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "kahf")
async def kahf(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 110 oyatdan iborat
    <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "maryam")
async def maryam(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 98 oyatdan iborat
        <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "toha")
async def taho(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 135 oyatdan iborat
 <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "anbiyo")
async def anbiyo(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 112 oyatdan iborat
     <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "haj")
async def haj(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 78 oyatdan iborat
     <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "muminum")
async def muminum(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 118 oyatdan iborat
     <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "Nur")
async def Nur(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 64 oyatdan iborat
 <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "furqon")
async def furqon(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 77 oyatdan iborat
    <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "shuaro")
async def shuaro(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 227 oyatdan iborat
        <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "naml")
async def naml(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 93 oyatdan iborat
      <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "qosos")
async def qosos(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 88 oyatdan iborat
        <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "ankobut")
async def ankobut(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 69 oyatdan iborat
 <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "rum")
async def rum(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 60 oyatdan iborat
        <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "luqmon")
async def luqmon(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 34 oyatdan iborat     
           <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "sajda")
async def sajda(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 30 oyatdan iborat
    <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "ahzob")
async def ahzob(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 73 oyatdan iborat
          <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "saba")
async def saba(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 54 oyatdan iborat
 <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "fotir")
async def fotir(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 45 oyatdan iborat         
 <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "yaasiyn")
async def yaasiyn(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 83 oyatdan iborat             
 <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "soffaat")
async def soffaat(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 182 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 



@dp.callback_query(F.data == "sod")
async def sod(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 88 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "zumar")
async def zumar(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 75 oyatdan iborat
      <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "gofir")
async def gofir(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 85 oyatdan iborat
      <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "fusilat")
async def fusilat(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 54 oyatdan iborat
      <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "shuuro")
async def shuuro(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 53 oyatdan iborat
             <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "zuxrof")
async def zuxrof(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 89 oyatdan iborat       
 <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "duxon")
async def duxon(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 59 oyatdan iborat
        <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "josiya")
async def josiya(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 37 oyatdan iborat    
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "ahqof")
async def ahqof(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 35 oyatdan iborat                                  
     <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "Muhammad")
async def Muhammad(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 38 oyatdan iborat     
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 
    
@dp.callback_query(F.data == "fatx")
async def fatx(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 29 oyatdan iborat        
 <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "hujurot")
async def hujurot(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 18 oyatdan iborat         
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "qof")
async def qof(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 45 oyatdan iborat
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "zoriyat")
async def zoriyat(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 60 oyatdan iborat
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "tur")
async def tur(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 49 oyatdan iborat
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "najm")
async def najm(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 62 oyatdan iborat
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "qamar")
async def qamar(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 55 oyatdan iborat
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 



@dp.callback_query(F.data == "Ar_Rohman")
async def Ar_Rohman(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 78 oyatdan iborat
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "voqi'a")
async def voqia(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 96 oyatdan iborat
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "hadid")
async def hadid(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 29 oyatdan iborat
<a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "mujodala")
async def mujodala(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 22 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "hashr")
async def hashr(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 24 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "mumtahana")
async def mumtahana(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 13 oyatdan iborat
   <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "soof")
async def soof(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 73 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "juma_quron")    
async def juma_quron(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 11 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "munofiqun")    
async def munofiqun(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 11 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "tagabun")    
async def tagabun(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 18 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "taloq")    
async def taloq(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 12 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "tahrim")    
async def tahrim(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 12 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "mulk")    
async def mulk(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 30 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "qalam")    
async def qalam(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 52 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "haaqqo")    
async def haaqqo(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 52 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "maorij")    
async def maorij(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 44 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "nuh")    
async def nuh(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 28 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "jin")    
async def jin(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 28 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "muzzammil")    
async def muzzammil(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 20 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "muddassir")    
async def muddassir(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 56 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "qiyaama")    
async def qiyaama(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 40 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "inson")    
async def inson(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 31 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "mursalaat")    
async def mursalaat(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 50 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "Naba")    
async def Naba(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 40 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "naziaat")    
async def naziaat(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 46 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "abasa")    
async def abasa(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 42 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "takvir")    
async def takvir(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 29 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "infitor")    
async def infitor(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 19 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "mutoffiful")    
async def mutoffiful(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 36 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "inshiqoq")    
async def inshiqoq(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 25 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "buruj")    
async def buruj(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 22 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 
    
@dp.callback_query(F.data == "toriq")    
async def toriq(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 17 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "alaa")    
async def alaa(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 19 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "goshiya")    
async def goshiya(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 26 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "fajr")    
async def fajr(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 30 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "balad")    
async def balad(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 20 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "shams")    
async def shams(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 15 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "layl")    
async def layl(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 21 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "zuho")    
async def zuho(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 11 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "sharh")    
async def sharh(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 8 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "tiyn")    
async def tiyn(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 8 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "alaq")    
async def alaq(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 19 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "qadr")    
async def qadr(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 5 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "bayyina")    
async def bayyina(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 8 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "zalzala")    
async def zalzala(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 8 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "adiyat")    
async def adiyat(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 11 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "qoria")    
async def qoria(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 11 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "takaasur")    
async def takaasur(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 8 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "asr_quron")    
async def asr_quron(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 3 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "humaza")    
async def humaza(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 9 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "fiyl")    
async def fiyl(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 5 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "quraysh")    
async def quraysh(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 4 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "maauun")    
async def maauun(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 7 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "kavsar")    
async def kavsar(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 3 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "kaafirun")    
async def kaafirun(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 6 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 


@dp.callback_query(F.data == "nasr")    
async def nasr(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 3 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "masad")    
async def masad(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 3 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "ixlos")    
async def ixlos(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 4 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "falaq ")    
async def falaq(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 5 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

@dp.callback_query(F.data == "nos_quron")    
async def nos_quron(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Makkiy, 6 oyatdan iborat
  <a href=''>Bizning kanal📢</a>
 """,reply_markup=admin_keyboard.orqaga_qayt) 

#------------------------------
@dp.message(F.text == "DIQQATNI JAMLASH")
async def namoz_vaqti(message: Message):
    await message.delete()
    
    await message.answer(
        text="""
Diqqatni pul deya qabul qiling.
Tasavvur qiling, diqqatingiz bu – pul. Bu valyuta sizda cheklangan miqdorda. 
Kun davomida uni “qimmat” va “qimmat bo‘lmagan” vazifalar uchun sarflashingiz mumkin. 
Jiddiy ish, mutolaa, siz uchun ahamiyatli vazifalar ko‘proq diqqat birligini talab etadi, biroq arzon turadi. 
Kam ahamiyatli masalan, ijtimoiy tarmoqlarni varaqlash kamroq diqqatni talab qiladi. 
Biroq u qimmat turadi. Diqqatning qarama-qarshi jihati ham shundan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/62'>Bizning kanal</a>  
""",reply_markup=admin_keyboard.qayt)
    
#shahodat----------------------


# Bosh menyu
@dp.message(F.text == "SHAHODAT")
async def orqa(message: Message):
    await message.delete()
    await message.answer(text="""   
Ashhadu alla ilaha illohu va ashhadu anna Muhammadan 'abduhu va rasuluh

Guvohlik beramanki, Allohdan o'zga iloh yo'q va yana guvohlik beramanki, Muhammad (s.a.v) Uning bandasi va elchisidir.                           
""")

# 99 ta ism ------====================
allah_names = [
    "1) Ar-Rohim: Latif ne'matlar beruvchi (qiyomat kuni faqat mo'minlarga)",
    "2) Al-Malik: Barcha narsaning egasi",
    "3) Al-Quddus: Barcha ayblardan xoli",
    "4) As-Salom: Barcha nuqsonlardan salomat va tinchlik omonlik va rohat beruvchi",
    "5) Al-Mu'min: Iymon va omonlik beruvchi",
    "6) Al-Muhaymin: Hamma narsani qamrab oluvchi",
    "7) Al-Aziz: Barchaning ustidan g'olib",
    "8) Al-Jabbar: Oliy qadar, ulug' zot",
    "9) Al-Mutakabbir: Kibriyosi va ulug'ligi behad",
    "10) Al-Xoliq: Asli va o'xshashi yo'q narsalarning o'lchovini mos qilib yaratuvchi",
    "11) Al-Bari': Yo'qdan paydo qiluvchi, vujudga keltiruvchi",
    "12) Al-Musavvir: Mahluqotlarning suratini shakillantiruvchi",
    "13) Al-G'affor: Ko'plab mag'firat qiluvchi",
    "14) Al-Qahhor: Barcha maxluqotlarni qabzida tutib, ularni o'z hukmiga yuritib va qudrati ila bo'ysundirib turuvchi",
    "15) Al-Vahhab: Ne'matlarni behisob beruvchi",
    "16) Ar-Razzaq: Ko'plab rizq beruvchi",
    "17) Al-Fattah: Ko'plab narsani ochuvchi",
    "18) Al-'Alim: Har bir narsani biluvchi",
    "19) Al-Qabid: Ruhlarni qabz qiluvchi",
    "20) Al-Basit: Ruhlarni kenglikka qo'yib yuboruvchi",
    "21) Al-Khafid: Pasaytiruvchi",
    "22) Ar-Rafi': Ko'taruvchi",
    "23) Al-Mu'izz: Aziz qiluvchi",
    "24) Al-Mudhill: Xor qiluvchi",
    "25) As-Sami': Har bir narsani eshituvchi",
    "26) Al-Basir: Har bir narsani ko'ruvchi",
    "27) Al-Hakam: Mukkamal hukm egasi",
    "28) Al-'Adl: Mutlaq adolat qiluvchi",
    "29) Al-Latif: Barcha nozik narsalarni ham biluvchi, o'ta lutf ko'rsatuvchi",
    "30) Al-Khabir: Hamma narsadan o'ta xabardor",
    "31) Al-Halim: G'azabi qo'zmaydigan va iqob qilishga shoshilmaydigan",
    "32) Al-'Azim: Aql tasavvur qila olmaydigan darajada azamatli va ulug'",
    "33) Al-Ghafur: Ko'plab mag'firat qiluvchi",
    "34) Ash-Shakur: Oz amal uchun ham ko'p savob beruvchi",
    "35) Al-'Aliy: Martabasi oliylikda benihoya",
    "36) Al-Kabir: Har bir narsadan katta",
    "37) Al-Hafiz: Har bir narsani Komil muhofaza qiluvchi",
    "38) Al-Muqit: Barcha moddiy va ruhiy rizqlarni yaratuvchi",
    "39) Al-Hasib: Kifoya qiluvchi va Qiyomatda bandalarini hisob qiluvchi",
    "40) Al-Jalil: Sifatlarda ulug'likka ega",
    "41) Al-Karim: Birov so'ramasa ham, hech bir evaz olmasdan ham, narsalarni ko'plab ato etuvchi",
    "42) Ar-Raqib: Hech bir zarrani ham qo'ymay tekshirib turuvchi",
    "43) Al-Mujib: Duolarni ijobat qiluvchi",
    "44) Al-Wasi': Keng-hamma narsani keng ilmi ila ihota qilgan, Barcha i keng rahmati ila qamrab oluvchi",
    "45) Al-Hakim: Har bir narsani hikmat ila qiluvchi",
    "46) Al-Wadud: Barcha yaxshilikni ravo ko'ruvchi",
    "47) Al-Majid: Shon-Sharafi va qadri behad yuksak",
    "48) Al-Ba'ith: Xalqlarga payg'ambarlarni yuboruvchi",
    "49) Ash-Shahid: Har bir narsaga hoziru nozir",
    "50) Al-Haqq: O'zgarmas,sobit Zot",
    "51) Al-Wakil: Barchaning ishni topshirilgan zot",
    "52) Al-Qawiyy: O'ta kuchli va quvvatli zot",
    "53) Al-Matin: Quvvatida mustahkam va matonatli",
    "54) Al-Waliyy: Muhabbat qiluvchi, nusrat beruvchi va xalqining ishini yurituvchi",
    "55) Al-Hamid: Barcha maqtovlar ila maqtalgan zot",
    "56) Al-Muhsi: Barcha narsaning hisobini oluvchi zot",
    "57) Al-Mubdi': Barcha narsalarni avvalboshidan bor qilgan Zot",
    "58) Al-Mu'id: Yo'q bo'lgan narsalarni yana qaytadan bor qiluvchi",
    "59) Al-Muhyi: Tiriltiruvchi",
    "60) Al-Mumit: O'ldiruvchi",
    "61) Al-Hayy: Tirik",
    "62) Al-Qayyum: O'zi qoim bo'lgan va boshqalarni qoim qilgan",
    "63) Al-Wajid: Topuvchi",
    "64) Al-Majid: Ulug'lik va sharaf sohibi",
    "65) Al-Wahid: Yagona,bitta.",
    "66) As-Samad: Hech kimga hojati tushmaydi, Barchaning hojati unga tushadi",
    "67) Al-Qadir: Cheksiz qudrat sohibi",
    "68) Al-Muqtadir: Juda ham qudratli",
    "69) Al-Muqaddim: Oldinga suruvchi",
    "70) Al-Mu'akhkhir: Orqaga suruvchi",
    "71) Al-Awwal: U hamma narsadan avval",
    "72) Al-Akhir: Hamma narsa yo'q bo'lib ketganda ham, Uning O'zi qoladi",
    "73) Az-Zahir: Uning mavjudligi oshkor, ochiq-oydindir",
    "74) Al-Batin: U ko'zga ko'rinmaydi",
    "75) Al-Wali: Har narsaga voliy ega bo'lgan Zot",
    "76) Al-Muta'ali: Nuqsonlardan yuqori turuvchi zot",
    "77) Al-Barr: Ulug' yaxshilik qiluvchi",
    "78) At-Tawwab: Bandalarni tavbaga yo'llovchi va ularning tavbasini ko'plab qabul qiluvchi Zot",
    "79) Al-Muntaqim: Zolim va osiylardan intiqom oluvchi",
    "80) Al-'Afuww: Avf qiluvchi",
    "81) Ar-Ra'uf: O'ta shavqatli va mehirbon",
    "82) Malik-ul-Mulk: Mulk egasi",
    "83) Dhul-Jalali wal-Ikram: Sharaf va kamol egasi",
    "84) Al-Muqsit: Adolat ila mazlumlarga nusrat va zolimlarga jazo beruvchi",
    "85) Al-Jami': Jamlovchi. Barcha haqiqatlarni jamlovchi",
    "86) Al-Ghaniyy: Behojat. Uning hech kimga va hech narsaga hojati tushmaydi",
    "87) Al-Mughni: Behojat qiluvchi",
    "88) Al-Mani': Man' qiluvchi. U himoya qiluvchi",
    "89) Ad-Darr: Xohlagan bandasiga zarar beruvchi",
    "90) An-Nafi': Foyda beruvchi",
    "91) An-Nur: O'zi nurli va O'zi nur beruvchi",
    "92) Al-Hadi: O'zi hidoyat topgan va O'zi hidoyat qiluvchi",
    "93) Al-Badi': O'xshashisiz, mislsiz va nihoyatda go'zal narsalarni yaratuvchi",
    "94) Al-Baqi: Mangu qoluvchi",
    "95) Al-Warith: So'nggida qoluvchi voris. Hammadan so'ng U qoladi",
    "96) Ar-Rashid: To'g'ri yo'l ko'rsatuvchi",
    "97) As-Sabur: Juda sabrli",
    "98) Al-Muqtadir: Har narsaga qodir",
    "99) Al-Muqaddim: Har narsani o'z vaqtida oldinga suruvchi",
]

NAMES_PER_PAGE = 9
def get_pagination_keyboard(current_page):
    buttons = []
    if current_page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"prev:{current_page - 1}"))
    if (current_page + 1) * NAMES_PER_PAGE < len(allah_names):
        buttons.append(InlineKeyboardButton(text="Oldinga ➡️", callback_data=f"next:{current_page + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def get_names_page(page):
    start = page * NAMES_PER_PAGE
    end = start + NAMES_PER_PAGE
    return "\n".join(allah_names[start:end])

@dp.message(F.text=="99 TA ISMLAR")
async def send_names(message: types.Message):
    await message.delete()
    current_page = 0
    await message.answer(
        text=get_names_page(current_page),
        reply_markup=get_pagination_keyboard(current_page)
    )

@dp.callback_query(lambda c: c.data and (c.data.startswith('next') or c.data.startswith('prev')))
async def process_pagination(callback_query: types.CallbackQuery):
    action, page = callback_query.data.split(':')
    current_page = int(page)
    await callback_query.message.edit_text(
        text=get_names_page(current_page),
        reply_markup=get_pagination_keyboard(current_page)
    )
    await callback_query.answer()


#  40 farz
@dp.message(F.text == "40 FARZ")
async def namoz_vaqti(message: Message):
    await message.delete()
    
    await message.answer(
        text="""
40 farz
""",reply_markup=admin_keyboard.qiriq_farz)
    

@dp.callback_query(F.data == "besh_farz")    
async def nos_quron(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Islomda beshta farz bor:
1. Iymon;
2. Namoz;
3. Ro‘za;
4. Zakot;
5. Haj.
 """,reply_markup=admin_keyboard.bu_uchun_orqaga) 


@dp.callback_query(F.data == "yetti_farz")    
async def yetti_farz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Iymonda yettita farz bor:
1. Allohga ishonish;
2. Allohning farishtalariga ishonish;
3. Allohning kitoblariga ishonish;
4. Allohning payg‘ambarlariga ishonish;
5. Oxirat kuniga ishonish;
6. Qadarga — yaxshilik ham, yomonlik ham Alloh taoloning irodasi bilan bo‘lishiga ishonish;
7. O‘lgandan keyin qayta tirilishga ishonish.

 """,reply_markup=admin_keyboard.bu_uchun_orqaga) 


@dp.callback_query(F.data == "tort_farz")    
async def tort_farz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Tahoratning farzlari to‘rtta:
1. Yuzni to‘liq yuvish;
2. Qo‘llarni tirsaklari bilan qo‘shib yuvish;
3. Boshning to‘rtdan biriga mash tortish;
4. Oyoqlarni to‘pig‘i bilan qo‘shib yuvish.
 """,reply_markup=admin_keyboard.bu_uchun_orqaga) 

@dp.callback_query(F.data == "tayammum_turt_farz")    
async def tayammum_turt_farz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Tayammumning farzlari to‘rtta:
1. Niyat;
2. Pok tuproqni qasd qilish;
3. Ikki qo‘lni toza tuproqqa urib, so‘ng yuzga surish;
4. Ikki qo‘lni tuproqqa urib, tirsak bilan qo‘shib qo‘llarga surish.
 """,reply_markup=admin_keyboard.bu_uchun_orqaga) 

@dp.callback_query(F.data == "uch_farz")    
async def uch_farz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Gʻuslning farzlari uchta:
1. Og‘izni g‘arg‘ara qilib chayish;
2. Burunni achishtirib chayish;
3. Badanning hamma joyiga suv yetkazib yuvish.
 """,reply_markup=admin_keyboard.bu_uchun_orqaga) 
    
@dp.callback_query(F.data == "on_ikki_farz")    
async def uch_farz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Namozning farzlari o‘n ikkita bo‘lib, oltitasi namoz tashqarisidadir, ular "namozning shartlari", deyiladi:
1. Badanning (junub, tahoratsizlik, hayz, nifosdan) pok bo‘lmog‘i;
2. Kiyimning pok bo‘lmog‘i va avratning to‘silmog‘i;
3. Namoz o‘rnining pok bo‘lmog‘i;
4. Namoz vaqtining kirmog‘i;
5. Qiblaga yuzlanib o‘qimoq;
6. Dildan (xolis) niyat qilmoq;
                                  
Oltitasi namoz ichida bo‘lib, ular "namozning ruknlari" deyiladi:
1. Namozga takbiri tahrima bilan kirish;
2. Qiyom;
3. Qiroat;
4. Ruku’;
5. Sajda;
6. Qa’dai oxir.
 """,reply_markup=admin_keyboard.bu_uchun_orqaga) 


@dp.callback_query(F.data == "amru_maruf")    
async def uch_farz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Yaxshi amallarni o'zi bajarib, boshqalarga ham buyitish

Yomon amallardan avval o'zi saqlanib boshqalarni ham qaytarish 
 """,reply_markup=admin_keyboard.bu_uchun_orqaga) 

@dp.callback_query(F.data == "ikki_farz")    
async def uch_farz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
Ilm izlash, o'qish farz.  Inson hayoti davomida kerak bo‘ladigan halol-haromga doir ilmlarni o‘zlashtirishi farzdir.
 """,reply_markup=admin_keyboard.bu_uchun_orqaga) 

@dp.callback_query(F.data == "orqaga_uchun_farz")    
async def uch_farz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""  
40 farz
 """,reply_markup=admin_keyboard.qiriq_farz) 


# Duolar
@dp.message(F.text == "DUOLAR")
async def massaeg(messaga: Message):
    await messaga.answer(text= """ duolar """)
  
# G'usl haqida ma'lumot
@dp.message(F.text == "G'USL")
async def massaeg(messaga: Message):
    await messaga.answer(
        text="""
GʻUSLNING FARZLARI[2]
Bas, gʻuslning farzi ogʻzini, burnini va butun badanini yuvmoqdir. 
Bu jumladan gʻuslning farzi uchta ekani anglab olinadi:
1. Ogʻizni chayqash.
Albatta, ogʻizni yaxshilab chayqash gʻuslning f arzlaridan biri ekani hammaga maʼlum. 
Busiz gʻusl boʻlishi mumkin emas.
2. Burunni chayqash.
Burunni yaxshilab, mubolagʻa ila chayish ham gʻuslning farzi hisoblanadi.
3. Badanning barcha yerini yuvish.
Butun tanani, biror tuki ostini ham qoʻymay, suv yetkazib yuvish ham gʻuslning farzidir. 
Gʻuslning farzligi „Moida“ surasidagi: „Agar j unub boʻlsalaringiz, poklaninglar“ (6-oyat) oyatidan olingan. 
Bunda yuvish imkoni bor barcha joyni poklash maʼnosi bordir. 
Alloh taolo yana „Niso“ surasida: „Va j unub holingizda ham, to gʻusl qilmaguningizcha (masjidda turmang). 
Magar yoʻldan oʻtuvchi boʻlsa, mayli“, degan (43-oyat). 
Ushbu ikki oyatda ogʻiz, burun va badanning barchasini yuvish maʼnosi bor. 
Abu Hurayra roziyalloxu anhudan rivoyat qilinadi

<a href='https://t.me/namoz_uqishni_urganish_Kanal/39'>Bizning kanal</a>

""", 
        reply_markup=admin_keyboard.Admin
    )
    await messaga.delete()

#IBODATI ISLOMIYA  haqida ma'lumot
@dp.message(F.text == "IBODATI ISLOMIYA")
async def massaeg(messaga: Message):
    await messaga.delete()
    await messaga.answer(
        text="""
Isomning besh ustuni (أركان الإسلام; ham أركان الدين „ dinning ustunlari“) — Islomdagi asosiy amallar boʻlib, barcha musulmonlar uchun farz qilingan ibodatlar hisoblanadi. Ular Jabroil alayhissalom hadislarida jamlangan. .Sunniylar va shialar bu harakatlarning bajarilishi va amaliyotining asosiy tafsilotlari boʻyicha hamfikir, lekin shialar ularni bir xil nom bilan ifodalamaydi. Islomning 5 ustuni: shahodat, namoz, zakot, ramazon oyida ro'za tutish va qodir boʻlganlar uchun Makkaga haj qilishdir
<a href='https://t.me/namoz_uqishni_urganish_Kanal/76'>Bizning kanal</a>   
""", 
        reply_markup=admin_keyboard.Admin
    )


# Tayammum haqida ma'lumot
@dp.message(F.text == "TAYAMMUM")
async def massaeg(messaga: Message):
    await messaga.delete()
    await messaga.answer(
        text="""
"Tayammum” lug‘atda “maqsad qilish” ma’nosini anglatadi. Istilohda esa poklanish maqsadida 
pok yer jinsi bilan yuzga va ikki qo‘lga tirsaklari bilan qo‘shib mash tortish “” deb ataladi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/40'>Bizning kanal</a>   
""", 
        reply_markup=admin_keyboard.Admin
    )
    await messaga.delete()

# Erkaklar uchun Namoz o'qishni o'rganish bo'limi

#-----------------------------------------------------------------------------------------------------------

# "🕋NOMOZ O'QISHNI O'RGANISH🤲" tugmasi uchun handler
@dp.message(F.text == "NAMOZ")
async def massaeg(messaga: Message):
    await messaga.answer("Tanlang", reply_markup=admin_keyboard.tanlash_)
    await messaga.delete()
# Erkaklar namozi uchun callback query
@dp.callback_query(F.data == "erkak_namozi")
async def erkak_namoz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="Tanlang", reply_markup=admin_keyboard.erkak_namoz)

# Azon matnini ko'rsatish uchun callback query
@dp.callback_query(F.data == "azon")
async def azon(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=""" 
Allohu akbar  اَللهُ أَكْبَر 
Allohu akbar  اَللهُ أَكْبَر 
Allohu akbar اَللهُ أَكْبَر 
Allohu akbar اَللهُ أَكْبَر 
Ashhadu alla ilaha illalloh  أَشْهَدُ أَلاَّ إِلَهَ إِلاَّ الله 
Ashhadu alla ilaha illalloh   أَشْهَدُ أَلاَّ إِلَهَ إِلاَّ الله 
Ashhadu anna Muhammadar Rasululloh  أَشْهَدُ أَنَّ مُحَمَّدًا رَسُولُ الله 
Ashhadu anna Muhammadar Rasululloh  أَشْهَدُ أَنَّ مُحَمَّدًا رَسُولُ الله 
Hayya alas solah  حَيَّ عَلَى الصَّلاَة 
Hayya alas solah  حَيَّ عَلَى الصَّلاَة 
Hayya alal falah  حَيَّ عَلَى الْفَلاَح 
Hayya alal falah  حَيَّ عَلَى الْفَلاَح 
Allohu akbar  اَللهُ أَكْبَر 
Allohu akbar اَللهُ أَكْبَر 
La ilaha illalloh لاَ إِلَهَ إِلاَّ الله 
<a href='https://t.me/namoz_uqishni_urganish_Kanal/28'>Bizning kanal📢</a>
""")
    
    await callback.message.answer(text="""
Azon duosi - Allohumma robba hazihid da’vatit tammah. Vas-solatil qoimah, ati Muhammadanil vasiylata val faziylah. Vad-darojatal ’aliyatar rofi’a. Vab’as-hu maqomam mahmudanillaziy va’adtah. Varzuqna shafa-’atahu yavmal qiyamah. Innaka la tuxliful mi’ad!
""", reply_markup=admin_keyboard.erkak_namoz)

# Bomdod namozi haqida ma'lumot
@dp.callback_query(F.data == "bomdod")
async def bomdod(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="Bomdod (fors.) — erta tong payti, sahar va shu paytda oʻqiladigan namoz. Bomdod namozi kun chiqish taraf yorishganidan boshlab to kun chiqqunga qadar oʻqiladi. Bamdod namozi ikki rakat sunnat va ikki rakat farzdan iborat. Erta tongda oʻqilgan namozning savobi qolgan namozlarga qaraganda kattaroq boʻladi. Namoz oʻqish musulmonlarning farzi hisoblanadi. <a href='https://t.me/namoz_uqishni_urganish_Kanal/14'>.</a>", reply_markup=admin_keyboard.erkak_namoz)


# Peshin namozi haqida ma'lumot
@dp.callback_query(F.data == "peshin")
async def peshin(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Peshin (fors.) — kunning yarmi oʻtgan payti va shu paytda oʻqiladigan namoz. Peshin namozi toʻrt rakat sunnat, toʻrt rakat farz va ikki rakat sunnatdan iborat. Peshin namozi Quyosh qiyomdan ogʻa boshlashidan to asr namozining vaqti kirguncha ado etiladi. <a href='https://t.me/namoz_uqishni_urganish_Kanal/9'>.</a>""", reply_markup=admin_keyboard.erkak_namoz)

# Asr namozi haqida ma'lumot
@dp.callback_query(F.data == "asr")
async def asr(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Asr namozi - Alloh taolo tomonidan farz qilingan namozlardan biri. Bu namozni musulmon kishi har kuni oʻqiydi. Ushbu namoz 4 rakat boʻlib faqat farzdan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/10'>Bizning kanal📢</a>""", reply_markup=admin_keyboard.erkak_namoz)

# Shom namozi haqida ma'lumot
@dp.callback_query(F.data == "shom")
async def shom(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Shom — Quyosh botib, qorongʻulik boshlangan payt va shu vaqtda oʻqiladigan namoz. Shom namozi Quyosh botgandan boshlab, magʻrib ufqidagi qizil shafaqning koʻrinmay ketadigan vaqtigacha ado etiladi, uch rakat farz va ikki rakat sunnatdan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/11'>Bizning kanal📢</a>""", reply_markup=admin_keyboard.erkak_namoz)

# Xufton namozi haqida ma'lumot
@dp.callback_query(F.data == "xufton")
async def xufton(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Xufton (fors. uxlash) — Quyosh botib ufqdagi qizillik yo'qolganidan keyin oʻqiladigan kechki namoz; bomdod namozi vaqti kirgungacha davom etadi. Xufton namozi to'rt rakat farz, ikki rakat sunnatdan iborat. Xufton namozining to'rt rakat farzi asr namozining farzi kabi o'qilib, faqat niyatda farq bo'ladi. Xuftonning ikki rakat sunnati ham yuqorida o'rganganimiz bomdod va shom namozlarining ikki rakat sunnatlari kabi bir xil tartibda o'qiladi. Bundan tashqari xufton namozi ōz ichiga 3 rakat vitr vojib namozini ham oladi. Ushbu vitr namozining 3-rakatida Fotiha va zam suralarni o'qigandan keyin "Qunut" duosi ōqiladi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/12'>Bizning kanal📢</a>""", reply_markup=admin_keyboard.erkak_namoz)

# Istixora namozi haqida ma'lumot
@dp.callback_query(F.data == "istixora")
async def istixora(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Istixora (baʼzan istihora ham deyiladi; arabcha: الاستخارة) — ikki rakaatdan iborat namoz. Ushbu namozdan so'ng musulmon kishi Allohdan maʼlum bir masala boʻyicha toʻgʻri qaror qabul qilishda yordam berishini soʻraydi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/59'>Bizning kanal📢</a>""", reply_markup=admin_keyboard.erkak_namoz)

# Hojat namozi haqida ma'lumot
@dp.callback_query(F.data == "hojat")
async def hojat(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Hojat namozining rakatlari borasida ixtilof qilingan. Molikiy va hanbaliylar nazdida, hojat namozi ikki rakatdir. Hanafiy ulamolar nazdida, hojat namozi to‘rt rakat o‘qiladi. Hanafiy mazhabimizdagi bir qavlda ikki rakat ham deyilgan. Bunga sabab shuki, hojat namozi haqida turli xil rivoyatlar kelgan. Ba’zi kitoblarimizda o‘n ikki rak’at ham deyilgan. Bizningcha, hojat namozining ikki rak’at ekanligi dalil jihatidan kuchlirog‘i bo‘lsa ajabmas. Vallohu a’lam!
Zero, hojat namozini ikki rakat o‘qish va unda qanday duo qilish haqidagi rivoyat Abdulloh ibn Abu Avvo va Anas ibn Molik roziyallohu anhumodan naql qilingan. Uni Imom Termiziy o‘zlarining mashhur hadis to‘plamlarida rivoyat qilib keltirganlar. Boshqa rivoyatlarning esa ayrim fiqhiy kitoblarda mazmuni zikr qilingan bo‘lsada, ammo roviysi va qaysi hadis to‘plamida keltirilganligiga ishora qilinmagan.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/60'>Bizning kanal📢</a>""", reply_markup=admin_keyboard.erkak_namoz)


#--------------------------------------------------------------------------------------------------------
# Ayollar uchun Namoz o'qishni o'rganish bo'limi

#-----------------------------------------------------------------------------------------------------------
""" Ayollar uchun Namoz o'qishni o'rganish """
#-----------------------------------------------------------------------------------------------------------

# "ayol_namoz" tugmasi uchun handler
@dp.callback_query(F.data == "ayol_namoz")
async def ayol_namoz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Tanlang", reply_markup=admin_keyboard.ayol_namoz)

# Ayollar bomdod namozi haqida ma'lumot
@dp.callback_query(F.data == "bomdod2")
async def ayol_namoz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Bomdod (fors.) — erta tong payti, sahar va shu paytda oʻqiladigan namoz. Bomdod namozi kun chiqish taraf yorishganidan boshlab to kun chiqqunga qadar oʻqiladi. Bamdod namozi ikki rakat sunnat va ikki rakat farzdan iborat. Erta tongda oʻqilgan namozning savobi qolgan namozlarga qaraganda kattaroq boʻladi. Namoz oʻqish musulmonlarning farzi hisoblanadi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/2'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.ayol_namoz)

# Ayollar peshin namozi haqida ma'lumot
@dp.callback_query(F.data == "peshin2")
async def peshin(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Peshin (fors.) — kunning yarmi oʻtgan payti va shu paytda oʻqiladigan namoz. Peshin namozi toʻrt rakat sunnat, toʻrt rakat farz va ikki rakat sunnatdan iborat. Peshin namozi Quyosh qiyomdan ogʻa boshlashidan to asr namozining vaqti kirguncha ado etiladi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/3'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.ayol_namoz)

# Ayollar asr namozi haqida ma'lumot
@dp.callback_query(F.data == "asr2")
async def asr(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Asr namozi - Alloh taolo tomonidan farz qilingan namozlardan biri. Bu namozni musulmon kishi har kuni oʻqiydi. Ushbu namoz 4 rakat boʻlib faqat farzdan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/4'>Bizning kanal📢</a>

""", reply_markup=admin_keyboard.ayol_namoz)

# Ayollar shom namozi haqida ma'lumot
@dp.callback_query(F.data == "shom2")
async def shom(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Shom — Quyosh botib, qorongʻulik boshlangan payt va shu vaqtda oʻqiladigan namoz. Shom namozi Quyosh botgandan boshlab, magʻrib ufqidagi qizil shafaqning koʻrinmay ketadigan vaqtigacha ado etiladi, uch rakat farz va ikki rakat sunnatdan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/6'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.ayol_namoz)

# Ayollar xufton namozi haqida ma'lumot
@dp.callback_query(F.data == "xufton2")
async def xufton(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Xufton (fors. uxlash) — Quyosh botib ufqdagi qizillik yo'qolganidan keyin oʻqiladigan kechki namoz; bomdod namozi vaqti kirgungacha davom etadi. Xufton namozi to'rt rakat farz, ikki rakat sunnatdan iborat. Xufton namozining to'rt rakat farzi asr namozining farzi kabi o'qilib, faqat niyatda farq bo'ladi. Xuftonning ikki rakat sunnati ham yuqorida o'rganganimiz bomdod va shom namozlarining ikki rakat sunnatlari kabi bir xil tartibda o'qiladi. Bundan tashqari xufton namozi ōz ichiga 3 rakat vitr vojib namozini ham oladi. Ushbu vitr namozining 3-rakatida Fotiha va zam suralarni o'qigandan keyin "" duosi ōqiladi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/5'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.ayol_namoz)

# Ayollar bomdod namozi videosi haqida ma'lumot
@dp.callback_query(F.data == "videosi2")
async def videosi2(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Bomdod namozi ikki rakat sunnat, ikki rakat farz – jami to'rt rakatdan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/2'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.ayol_namoz)

# Ayollar islomdagi o'rni haqida ma'lumot
@dp.callback_query(F.data == 'xolat')
async def xolat(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Islom dini ayolning jamiyatdagi o'rni va ta'sirini juda katta baholaydi. Chunki ayollar islom ummatining tarbiyachilari hisoblanadi. Shu sababli ularning bilim olishi, ma'naviyati va ilm tarqatishi birinchi o'rindagi masalalardandir. Ayniqsa, ayollar uchun birinchi navbatda o'rganishi farz bo'lgan ilmlar - ularning o'zlariga xos bo'lgan masalalardir.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/7'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.ayol_namoz)

# Ayollar istixora namozi haqida ma'lumot
@dp.callback_query(F.data == "istixora2")
async def istixora(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Istixora (baʼzan istihora ham deyiladi; arabcha: الاستخارة) — ikki rakaatdan iborat namoz. Ushbu namozdan so'ng musulmon kishi Allohdan maʼlum bir masala boʻyicha toʻgʻri qaror qabul qilishda yordam berishini soʻraydi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/59'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.ayol_namoz)

# Ayollar hojat namozi haqida ma'lumot
@dp.callback_query(F.data == "hojat2")
async def hojat(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Hojat namozining rakatlari borasida ixtilof qilingan. Molikiy va hanbaliylar nazdida, hojat namozi ikki rakatdir. Hanafiy ulamolar nazdida, hojat namozi to‘rt rakat o‘qiladi. Hanafiy mazhabimizdagi bir qavlda ikki rakat ham deyilgan. Bunga sabab shuki, hojat namozi haqida turli xil rivoyatlar kelgan. Ba’zi kitoblarimizda o‘n ikki rak’at ham deyilgan. Bizningcha, hojat namozining ikki rak’at ekanligi dalil jihatidan kuchlirog‘i bo‘lsa ajabmas. Vallohu a’lam!
Zero, hojat namozini ikki rakat o‘qish va unda qanday duo qilish haqidagi rivoyat Abdulloh ibn Abu Avfo va Anas ibn Molik roziyallohu anhumodan naql qilingan. Uni Imom Termiziy o‘zlarining mashhur hadis to‘plamlarida rivoyat qilib keltirganlar. Boshqa rivoyatlarning esa ayrim fiqhiy kitoblarda mazmuni zikr qilingan bo‘lsada, ammo roviysi va qaysi hadis to‘plamida keltirilganligiga ishora qilinmagan.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/61'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.ayol_namoz)

  
#-----------------------------------------------------------------------------------------------
# Tahorat haqida ma'lumot berish
@dp.message(F.text == "TAHORAT")
async def massaeg(messaga: Message):
    await messaga.answer("""
Tahorat uchun suv hozirlagandan keyin:

1. Qibla tomonga qarab, ichida „Tahorat olishni niyat qildim“ deyiladi.
2. Auzu billahi minash-shaytonir rojiym. Bismillahir rohmanir rohiym“, deyiladi.
3. Qoʻllar bandigacha 3 marta yuviladi.
4. Oʻng qoʻlda suv olinib, ogʻiz 3 marta gʻargʻara qilib chayiladi va misvok qilinadi.
5. Burunga oʻng qoʻl bilan 3 marta suv tortilib, chap qoʻl bilan qoqib tozalanadi.
6. Yuz 3 marta yuviladi.
7. Avval oʻng qoʻl tirsaklar bilan qoʻshib ishqalab yuviladi, soʻngra chap qoʻl.
8. Hovuchga suv olib, toʻkib tashlab, hoʻli bilan boshning hamma qismiga masx tortiladi.
9. Koʻrsatkich barmoq bilan quloqlarning ichi, bosh barmoqlar bilan esa quloq orqasi masx qilinadi.
10. Ikkala kaftning orqasi bilan boʻyin masx qilinadi.
11. Chap qoʻl bilan oʻng oyoqni oshiq qismi bilan qoʻshib, barmoqlar orasini ishqalab 3 marta yuviladi, keyin chap oyoq.
12. Qibla tomonga qarab, ichida „Ashhadu an La ilaha illallohu va ashhadu anna Muhammadan abduhu va rosuluh“ deyiladi. 

<a href= 'https://t.me/namoz_uqishni_urganish_Kanal/21'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.tahorati)

# Tahorat haqida batafsil ma'lumot berish (callback query)
@dp.callback_query(F.data == 'tarif')
async def valyuta_back(callback: CallbackQuery):
    await callback.message.answer(text="""
Tahorat — namoz oʻqish, ibodat oldidan yuvinish, poklanish jarayoni. Xususiy shakli sifatida tayammum koʻriladi. Islomda tahoratning ikki turi mavjud: vuzuʼ — kichik tahorat — qoʻloyoq va yuzni yuvish; gʻusul — katta tahorat — toʻla yuvinish, choʻmilish.

Tahoratning 4 ta farzi bor:
- Yuzni yuvmoq;
- Ikki qoʻlni tirsak ila qoʻshib yuvmoq;
- Ikki oyoqni toʻpigʻi ila qoʻshib yuvmoq;
- Boshning toʻrtdan bir qismiga mas'h tortish.

Bu farzlardan birortasi bajarilmasa, tahorat haqiqiy boʻlmaydi.

""", reply_markup=admin_keyboard.Admin)

# Ayollar uchun tahorat haqida ma'lumot berish
@dp.message(F.text == "AYOLLAR UCHUN TAHORAT")
async def massaeg(messaga: Message):
    await messaga.answer("""
Tahorat va unga bog‘liq masalalar

1. Tahoratda to‘rt farz bor: qo‘lni yuvish, yuzni yuvish, boshning to‘rtdan biriga mash tortish va oyoqni yuvish.
2. Kimki, boshning hammasiga mash tortsa, farzni mukammal va go‘zal tarzda bajargan bo‘ladi.
3. Og‘izga suv olib yuvish, burunga suv tortib burunni chayishlik, quloqlarga mash qilishlik tahorat amallaridandir.
4. Tahoratda har bir a’zoni yuvish o‘ngdan boshlanishi, soqolga xilol qilish, barmoqlar orasini xilol qilish, misvok ishlatish kabi amallar sunnatdir.

<a href='https://t.me/namoz_uqishni_urganish_Kanal/58'>Bizning kanal📢</a>
""")


#makka online 
@dp.message(F.text == "MAKKA ONLINE")
async def message(messaga:Message):
    await messaga.answer("Makka Onlayn kuzatish",reply_markup=admin_keyboard.makka)

# Qo'shimcha suralar va duolar haqida ma'lumot berish
@dp.message(F.text == "SURALAR")
async def massaeg(messaga: Message):
    await messaga.answer("Qo'shimcha suralar", reply_markup=admin_keyboard.qushimcha)

# Callback query uchun sura va duolar
@dp.callback_query(F.data == 'oyat')
async def valyuta_back(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Allohu la ilaha illa huval hayyul qoyyum. La ta'xuzuhu sinatuv-va la nawm. Lahu ma fis-samavati va ma fil arz. Manzallaziy yashfa'u 'indahu illa bi'iznih...

<a href='https://t.me/namoz_uqishni_urganish_Kanal/15'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'oyat')
async def oyat(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
OYATAL KURSI

Makkiy, 1 oyatdan iborat
<a href='https://t.me/namoz_uqishni_urganish_Kanal/23'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.qushimcha)



# Sano duosi haqida
@dp.callback_query(F.data == 'sano')
async def valyuta_back(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Subhaanakalloouhumma va bihamdika va tabaaro kasmuka va ta’aalaa jadduka va laa ilaaha g‘oyruk...

<a href='https://t.me/namoz_uqishni_urganish_Kanal/29'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.qushimcha)

# Fotiha surasi haqida
@dp.callback_query(F.data == 'fotiha')
async def valyuta_back(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Makkiy, 7 oyatdan iborat
<a href='https://t.me/namoz_uqishni_urganish_Kanal/50'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'qunut')
async def valyuta_back(callback: CallbackQuery,state:FSMContext):
    await callback.message.delete()
    await callback.message.answer(text="""
Allohumma innaa nastaʼiynuka va nastagʻfiruk. Va nuʼminu bik va natavakkalu alayk. Va nusniy alaykal xoyro kullah. Nashkuruka va laa nakfuruk. Va naxlaʼu va natruku may yafjuruk. Allohumma iyyaka naʼbudu va laka nusolliy va nasjudu va ilayka nasʼaa va nahfidu. Narjuu rohmatak va naxshaa azaabak. Inna azaabaka bil kuffaari mulhiq.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/50'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.qushimcha)
    await state.clear()



# Callbacklar uchun handlerlar
@dp.callback_query(F.data == 'kofirun')
async def kofirun_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Makkiy, 6 oyatdan iborat
        <a href='https://t.me/namoz_uqishni_urganish_Kanal/34'>Bizning kanal📢</a> 
""")
    await callback.message.answer(text="audio <a href='https://t.me/namoz_uqishni_urganish_Kanal/45'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'ixlos')
async def ixlos_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Makkiy, 4 oyatdan iborat                            
    <a href='https://t.me/namoz_uqishni_urganish_Kanal/35'>Bizning kanal📢</a> 
""")
    await callback.message.answer(text="audio <a href='https://t.me/namoz_uqishni_urganish_Kanal/44'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'falaq_')
async def falaq_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
 Makkiy, 5 oyatdan iborat                                    
<a href='https://t.me/namoz_uqishni_urganish_Kanal/36'>Bizning kanal📢</a>                                                     
""")
    await callback.message.answer(text=". <a href='https://t.me/namoz_uqishni_urganish_Kanal/43'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'nas')
async def nas_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
 Makkiy, 6 oyatdan iborat   
    <a href='https://t.me/namoz_uqishni_urganish_Kanal/37'>Bizning kanal📢</a> 
""")
    await callback.message.answer(text=". <a href='https://t.me/namoz_uqishni_urganish_Kanal/42'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'kavsar')
async def nas_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
 Makkiy, 3 oyatdan iborat                                      
<a href='https://t.me/namoz_uqishni_urganish_Kanal/65'>Bizning kanal📢</a> 
""")
    await callback.message.answer(text=". <a href='https://t.me/namoz_uqishni_urganish_Kanal/66'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)



@dp.callback_query(F.data == 'quraysh_')
async def nas_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
 Makkiy, 4 oyatdan iborat   
    <a href='https://t.me/namoz_uqishni_urganish_Kanal/73'>Bizning kanal📢</a> 
""")
    await callback.message.answer(text=". <a href='https://t.me/namoz_uqishni_urganish_Kanal/72'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)


@dp.callback_query(F.data == 'nasr_')
async def nasr_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
 Makkiy, 3 oyatdan iborat   
<a href='https://t.me/namoz_uqishni_urganish_Kanal/38'>Bizning kanal📢</a> 
""")
    await callback.message.answer(text=". <a href='https://t.me/namoz_uqishni_urganish_Kanal/41'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'fil_quron')
async def fil_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
 Makkiy, 5 oyatdan iborat                          
<a href=''>Bizning kanal📢</a> 
""")
    await callback.message.answer(text=". <a href=''>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'maun_surasi')
async def maun_surasi(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
 Makkiy, 7 oyatdan iborat                          
<a href=''>Bizning kanal📢</a> 
""")
    await callback.message.answer(text=". <a href=''>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'masad_surasi')
async def masad_surasi(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
 Makkiy, 5 oyatdan iborat                          
<a href=''>Bizning kanal📢</a> 
""")
    await callback.message.answer(text=". <a href=''>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

# duolar ---------=\
@dp.message(F.text=="DUOLAR")
async def message(message:Message):
    await message.answer(text="""
DUOLAR """,reply_markup=admin_keyboard.duolar)

@dp.callback_query(F.data == "orqa_button_duolar")
async def orqa_button_duolar(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
DUOLAR
""", reply_markup=admin_keyboard.duolar)

@dp.callback_query(F.data == "azondan_kiyinduo")
async def azondan_kiyinuo(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Bismillahir Rohmanir Rohiym.
Alloh taologa bitmas-tuganmas hamdu sanolar bo‘lsin.
Payg‘ambarimizga mukammal va batamom salavotu durudlar bo‘lsin.
Azonning hammasini eshitib bo‘lganidan keyin Rasululloh sollallohu alayhi vasallamga salovot aytib, ortidan mana bu duoni o‘qiydi:
اللهُمَّ رَبَّ هَذِهِ الدَّعْوَةِ التَّامَّةِ وَالصَّلاَةِ القَائِمَةِ آتِ مُحَمَّدًا الوَسِيلَةَ وَالفَضِيلَةَ وَابْعَثْهُ مَقَامًا مُحْمُودًا الَّذِي وَعَدْتَهُ
«Allohumma robba hazihid da’vatit tammah vassolatil qoimah, ati Muhammadanil vasiylata val faziylah vab’ashu maqomam mahmudanillaziy va’adtah» (Ey bu komil duoning va qoim bo‘lgan namozning egasi Allohim, Muhammadga vasila va fazilat ber, u zotni va’da qilganing maqtovli maqomda tiriltir). So‘ngra xohlaganicha dunyoviy va uxroviy duolarni qilaveradi.
""", reply_markup=admin_keyboard.duolar)

@dp.callback_query(F.data == "sano_duosi")
async def sano_duosi(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
SANO DUOSI
Subhaanakalloouhumma va bihamdika va tabaaro kasmuka va ta’aalaa jadduka va laa ilaaha g‘oyruk
Ma’nosi: «Allohim! Sening noming muborakdir. Shon sharafing ulug‘dir. Sendan o‘zga iloh yo‘qdir»
                                 
""", reply_markup=admin_keyboard.duolar)

@dp.callback_query(F.data == "rukudan_turkanda")
async def rukudan_turkanda(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Subhana robbiyal 'aziym
Ulug' Robbim nuqsonlarda pikdir                           
""", reply_markup=admin_keyboard.duolar)

@dp.callback_query(F.data == "rukudan_qaytayotganda")
async def rukudan_qaytayotganda(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Sami'allohu liman hamidah
Kim hamd aytsa,Alloh uni eshitadi                                  
""", reply_markup=admin_keyboard.duolar)

@dp.callback_query(F.data == "rukudan_qaytib_turganda")
async def rukudan_qaytib_turganda(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Robbana lakal hamd.
Robbimiz, Senga hamd bo'lsin                              
""", reply_markup=admin_keyboard.duolar)

@dp.callback_query(F.data == "sajdada")
async def sajdada(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Subhana robbiyal a'la
Oliy Robbim nuqsonlardan pokdir                              
""", reply_markup=admin_keyboard.duolar)

@dp.callback_query(F.data == "tashahhud")
async def tashahhud(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
«Attahiyyatu lillahi vassolavatu vat­toy­yibat. Assalamu ’alayka ayyuhan-nabiyyu va rohmatullohi vabarokatuh. Assalamu ’alayna va a’laa ibaadillaahis solihiyn. Ashhadu allaa ilaaha illallohu va ashhadu anna Muhammadan ’abduhu va rosuluh».
Ma’nosi: «Barokatli tabriklar va pokiza salavotlar Alloh uchundir. Ey Nabiy! Senga salom, Allohning rahmati va barakasi bo‘lsin. Bizlarga va Allohning solih bandalariga salom bo‘lsin. Allohdan o‘zga iloh yo‘q deb guvohlik beraman va albatta, Muhammad – Allohning Rasuli deb guvohlik beraman».                             
""", reply_markup=admin_keyboard.duolar)

@dp.callback_query(F.data == "salovatlar")
async def salovatlar(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
«Allohumma solli ’alaa Muhammadiv va ’alaa ali Muhammad. Kama sollayta ’alaa Ibrohima va ’alaa ali Ibrohim. Innaka hamidum majid.
Allohumma barik ’alaa Muhammadiv va ’alaa ali Muhammad. Kama barokta ’alaa Ibrohima va ’alaa ali Ibrohim. Innaka hamidum majid».
Ma’nosi: Allohim! Ibrohimga va Ibrohimning ahli baytlariga O‘z rahmatingni nozil qilganingdek, Muhammadga va Muhammadning oila a’zolariga O‘zingning ziyoda rahmatlaringni nozil qilgin! Albatta, Sen maqtalgan, ulug‘langan Zotsan!
Allohim! Ibrohimga va Ibrohimning ahli baytlariga O‘z barakangni nozil qilganingdek, Muhammadga va Muhammadning oila a’zolariga O‘z barakangni nozil qilgin! Albatta, Sen maqtalgan, ulug‘langan Zotsan!.
""", reply_markup=admin_keyboard.duolar)
    
@dp.callback_query(F.data == "namozdan_kiyin")
async def namozdan_kiyin(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Namoz salom bilan tugaydi. Salomdan keyingi amallar (tasbehotu duolar) majburiy emas, ammo nihoyatda savoblidir.
Farz namozlaridan keyin quyidagi duoni o‘qish sunnatdir:
All`ohumma antas-sal`am va minkas-sal`am. Tab`arokta y`a zaljal`ali val ikr`om.
Mazmuni:
Ey Allohim, Sen barcha ayb-nuqsonlardan poksan. Barcha salomatlik va rahmat Sendandir. Ey azamat va qudrat egasi bo‘lgan Allohim, Sening shoning ulug‘dir.
Umuman, har vaqt namozni tugatgandan so‘ng Oyatal kursi o‘qilsa, tasbehot qilinsa, savobi ulug‘ bo‘ladi.
OYATAL KURSI
A'`uzu bill`ahi minash-shayt`onir roj`iym. Bismill`ahir rohm`anir roh`iym.
All`ohu l`a il`aha ill`a huval hayyul qoyy`um. L`a ta'xuzuh`u sinatuv-va l`a na`vm. Lahu m`a fis-sam`av`ati va m`a fil arz. Manzallaz`iy yashfa'u ‘indah`u ill`a bi'iznih. Ya'lamu m`a bayna ayd`ihim va m`a xolfahum va l`a yux`it`una bi shay'im-min ‘ilmih`i ill`a bima sh`a'a. Vasi'a kursiyyuhus-sam`av`ati val arz. Va l`a ya'`uduh`u hifzuhum`a va huval ‘alliyyul ‘az`iym.
Mazmuni:
Alloh — Undan o‘zga iloh yo‘qdir. (U hamisha) tirik va abadiy turuvchidir. Uni na mudroq tutar va na uyqu. Osmonlar va Yerdagi (barcha) narsalar Unikidir. Uning huzurida hech kim (hech kimni) Uning ruxsatisiz shafoat qilmas. ( U ) ular (odamlar)dan oldingi (bo‘lgan) va keyingi (bo‘ladigan) narsani bilur. (Odamlar) Uning ilmidan faqat ( U ) istagancha o‘zlashtirurlar. Uning Kursiysi osmonlar va Yerdan (ham) kengdir. U ikkisining hifzi (tutib turishi) Uni toliqtirmas. U oliy va buyukdir.
TASBEH
Subhanalloh
(33 marta)
Alhamdulillah
(33 marta)
Allohu akbar
(33 marta)
KALIMAI TAVHID
L`a il`aha illall`ohu vahdah`u l`a shar`ika lah, lahul mulku va lahul hamd. Va huva ‘al`a kulli shay'in qod`ir.
Mazmuni:
Allohdan o‘zga iloh yo‘q. U yagonadir, sherigi yo‘q, butun mulk Unikidir. Hamd-maqtov Unga xosdir. Va U har narsaga qodir zotdir.
""", reply_markup=admin_keyboard.duolar)


@dp.callback_query(F.data == "qunut")
async def qunut(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
«Allohumma innaa nasta’iynuka va nastag‘firuka. Va nu’minu bika va natavakkalu alayka. Va nusniy alaykal xoyro kullahu. Nashkuruka va laa nakfuruk. Va naxla’u va natruku man yafjuruk. Allohumma iyyaaka na’budu va laka nusolliy va nasjudu va ilayka nas’aa va nahfidu. Narjuu rohmataka va naxshaa azaabaka. Inna azaabaka bil kuffaari mulhiq».
Duoning ma’nosi: «Allohim, albatta, biz Sendan yordam so‘raymiz, senga istig‘for aytamiz va senga iymon keltiramiz, senga tavakkul qilamiz va senga shukr keltiramiz, kufr keltirmaymiz. Kim senga fojirlik qilsa, uni ajratamiz va tark qilamiz. Allohim, sengagina ibodat qilamiz, sengagina namoz o‘qiymiz va sajda qilamiz, Sengagina intilamiz va shoshilamiz. Sening rahmatingni umid qilamiz va azobingdan qo‘rqamiz. Albatta, Sening haq azobing kofirlarga yetguvchidir».  (“Kifoya” kitobidan). Vallohu a’lam!
""", reply_markup=admin_keyboard.duolar)

@dp.callback_query(F.data == "istihora_namozi_duosi")
async def istihora_namozi_duosi(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Allohumma inniy astaxīruka biʿilmika va astaqdiruka biqudratika, va asʾaluka min faḍlika (a)l-ʿaẓīm fainnaka taqdiru valā aqdiru va taʿlamu valā aʿlamu va anta ʿallāmu (a)l-g’uyūb. Allohumma, in kunta taʿlamu anna hāza (a)l-amra xoyrul lī fī dīnī va maʿāshī vaʿāqibati amrī faqdurhu lī va yassirhu lī thumma barik lī fīhi. Va in kunta taʿlamu anna haza (a)l-amra sharrun lī fī dīnī va maʿāshī va ʿāqibati amri faṣrifhu ʿannī va (a)ṣrifni ʿanhu vaqdir lī(ya) (a)l-xoyro haysu kāna summa arḍīnī bihi.
Allohim, ilming bilan Sendan yaxshilik so’rayman. Qudrating bilan Sendan qodirlik va ulug’ fazlingni so’rayman. Zero, Sen qodirsan, men ojizman. Sen biluvchisan, men bilmayman. Sen g’aybni biluvchisan. Allohim, agar mana shu ishim dinimda, hayotimda, ishlarimning oqibatida, dunyo va ohiratimda men uchun yaxshi bo’lsa, uni menga nasib et. Agar mana shu ishim dinimda, hayotimda, ishlarimning oqibatida, dunyo va ohiratimda men uchun yomon bo’lsa, uni mendan va meni undan uzoqlashtir. Qayerda bo’lsa ham, men uchun yaxshilikni taqdir qil va meni undan rozi qil.                                  
""", reply_markup=admin_keyboard.duolar)


@dp.callback_query(F.data == "hojat_namozi_duosi")
async def hojat_namozi_duosi(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Hojat namozi o‘qib bo‘lingach, salomdan keyin quyidagi duo o‘qiladi:
ا إِلَهَ إِلَّا اللهُ الْحَلِيمُ الْكَرِيمُ، سُبْحَانَ اللهِ رَبِّ الْعَرْشِ الْعَظِيمِ، الْحَمْدُ لِلَّه رَبِّ الْعَالَمِينَ: أَسْأَلُكَ مُوجِبَاتِ رَحْمَتِكَ، وَعَزَائِمَ مَغْفِرَتِكَ، وَالْغَنِيمَةَ مِنْ كُلِّ بِرٍّ، وَالسَّلَامَةَ مِنْ كُلِّ إِثْمٍ، لَا تَدَعْ لِي ذَنْبًا إِلَّا غَفَرْتَهُ، وَلَا هَمًّا إِلَّا فَرَّجْتَهُ، وَلَا حَاجَةً هِيَ لَكَ رِضًا إِلَّا قَضَيْتَهَا يَا أَرْحَمَ الرَّاحِمِينَ.
«Laa ilaaha illallohul haliymul kariym. Subhaanallohi robbil ’arshil ’aziym. Alhamdu lillaahi robbil ’aalamiyn. As’aluka mujibaati rohmatika va ’azoima mag‘firotika val g‘oniymata min kulli birrin, vas-salaamata min kulli ismin, laa tada’ liy zanban illa g‘ofartahu, va laa hamman illa farrojtahu, va laa haajatan hiya laka rizon illa qozoytaha, yaa arhamar rohimiyn!» deb, hojati aytib duo qilinadi.
""", reply_markup=admin_keyboard.duolar)

#  jamoat namozlari ----
@dp.callback_query(F.data == "JAMOAT_namoz")
async def ayol_namoz(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Jamoat namozi – savobi ulug‘ ibodat. Ibn Umar roziyallohu anhumodan rivoyat qilinadi. Rasululloh sollallohu alayhi vasallam: “Jamoat namozi yolg‘iz o‘qilgan namozdan yigirma yetti daraja afzaldir”, dedilar (Imom Buxoriy, Imom Muslim rivoyati)", reply_markup=admin_keyboard.jamoat
""", reply_markup=admin_keyboard.jamoat)

@dp.callback_query(F.data == 'juma')
async def juma_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Juma namozi (arabcha: صَلَاة ٱلْجُمُعَة, Ṣalāt al-Jumuʿah) — Musulmonlarning umumiy namozi. Juma kuni masjidlarda peshin namozi vaqtida oʻqiladi. Juma namozi erkin, voyaga yetgan erkaklarga farzdir. Juma namozi ikki rakat farz boʻlib, undan oldin va keyin toʻrt rakat sunnat oʻqiladi. Ilk va oxirgi sunnatlar peshin namozining sunnatlari kabi oʻqiladi. Imomga iqtido qilib oʻqiladigan ikki rakat farz esa, bomdod namozining farzi kabi oʻqiladi. Ayollar, bolalar va jismoniy zaif kishilar uchun juma namozi shart emas. Ayrim zamonaviy hanafiy ilohiyotshunoslari keksa ayollarning jamoaviy namozga borishini nomaqbul deb hisoblaydilar. Musulmonlarga juma namozini uzrsiz sababsiz tark etish taqiqlangan. Tabiiy ofatlar (qattiq ayoz, qor koʻchkisi xavfi, kuchli yomgʻir va h.k.) yuz berganda juma namozi ixtiyoriy holga keladi. Namozdan oldin musulmon toʻliq tahorat olib, tirnoqlarini kesib, toza, bayramona kiyim kiyishi tavsiya etiladi. Bundan tashqari, mushk sepish tavsiya etiladi. Masjidga kirishdan oldin sarimsoq, piyoz va boshqa oʻtkir hidli yeguliklarni isteʼmol qilish taqiqlanadi. Namozdan oldin ikkinchi azon aytiladi va xutba oʻqiladi. Xutba ikki qismdan iborat. Xutbaning bu qismlari orasida imomning qisqa vaqt oʻtirishi maqsadga muvofiqdir. Xutbadan keyin namozxonlar imomdan keyin ikki rakat namoz oʻqiydilar. Juma namozining oʻqilishi peshin namozini oʻqishdan xalos qiladi. Masjidga kechikib kelish mumkin emas. Eng oxirgi kelgan kishi boshqa dindorlarni bosib oʻtmasligi, qator oralarida yurmasligi va boshqalarni bezovta qilib, oldingi qatorlardan joy olishga harakat qilmasligi kerak. Imom xutba oʻqish uchun minbarga chiqqan bir paytda gaplashib, boshqa odamlarni chalgʻitib boʻlmaydi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/13'>Bizning kanal📢</a> 
""", reply_markup=admin_keyboard.jamoat)

@dp.callback_query(F.data == 'ied')
async def ied_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Alloh rizoligi uchun Ramazon hayiti namozini o‘qishga niyat qilinadi.
Imom “Allohu akbar” deya takbir aytgach jamoat ham qo‘llarini ko‘tarib, ichida iftitoh takbiri (Allohu akbar)ni aytadi. Takbir aytilganidan so‘ng, qo‘lni qovushtirib turib, har kim ichida sano duosini o‘qiydi. So‘ngra imom qo‘llarini quloqlariga ko‘tarib, uch marta takbir aytadi. Jamoat ham unga ergashadi. Birinchi va ikkinchi takbirda qo‘llar yon tomonga tushiriladi. Uchinchi takbirdan so‘ng qo‘llar bog‘lanib, qiyom holida turiladi. Imom ichida “A’uzu”ni va “Bismillah”ni aytib, ovoz chiqarib “Fotiha” surasini va zam surani o‘qiydi. Takbir aytib ruku va sajda ado etiladi. Shundan so‘ng ikkinchi rakatga turiladi. Imom “Fotiha” surasi bilan zam sura o‘qigach, rukuga bormay turib, xuddi birinchi rakatdagi kabi uch marta takbir aytadi. To‘rtinchi takbirda qo‘l ko‘tarmasdan imom orqasidan ruku va sajda ado qilinadi. Sajdadan so‘ngra “Attahiyyot”, “Salovat” va “Duo” o‘qilib, salom berilib, namoz tugatiladi. Alloh ibodatlaringizni O‘z dargohida qabul etsin!
<a href='https://t.me/namoz_uqishni_urganish_Kanal/22'>Bizning kanal📢</a> 
""", reply_markup=admin_keyboard.jamoat)

@dp.callback_query(F.data == 'janoza')
async def janoza_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Janoza namozi – vafot etgan musulmonlar uchun jamoat boʻlib oʻqiladigan namoz. Mayyit yuvilib, kafanlanadi, masjidga keltiriladi. Jamoatning oldiga yuqoriroq yerga qoʻyiladi. Imom jamoatning oldiga oʻtib Janoza namozini oʻqiydi. Janoza namozini oʻquvchi kishi avval: "Niyat qildim ushbu marhum uchun Janoza namozini oʻqimoqqa, iqtido qildim ushbu imomga. Xolisan lillohi Taolo", deb niyat qiladi. Imom baland ovoz bilan, qolganlar imomga iqtido qilib maxfiy su'ratda (faqatgina o'zi eshitadigan darajada) "Allohu Akbar" deb qoʻllarini bogʻlaydi. Iqtido qilib oʻquvchi aytganini o'zi eshitadigan darajada takbir aytib qoʻllarini bogʻlaydi. Soʻngra ovoz chiqarmasdan "Sano"ni oʻqiydi: "Subhanakallohumma va bihamdika va tabarokasmuka va taʻala jadduka va la ilaha gʻoyruk". Soʻngra imom bilan birgalikda takror takbir aytiladi. Lekin qoʻllar koʻtarilmaydi. Solli va Barik duolari oʻqiladi. Takror yana qoʻllar koʻtarilmagan holda takbir aytiladi, janoza duosi oʻqiladi. Janoza duosini bilmaydiganlar esa, Qunut duosini yoki duo niyati bilan Fotiha surasini oʻqisa ham boʻladi. Soʻngra imom bilan birgalikda takror takbir qilinib oldin oʻngga, keyin chapga salom beriladi. Janoza namozi oʻqilib boʻlganidan keyin mayyit mozorga olib boriladi, qabrga qoʻyiladi, ruhdariga bagʻishlab Qurʼon tilovat va duo qilinadi
<a href='https://t.me/namoz_uqishni_urganish_Kanal/19'>Bizning kanal📢</a> 
""", reply_markup=admin_keyboard.jamoat)

@dp.callback_query(F.data == 'tarovih')
async def tarovih_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Tarovih – istirohat ma’nosidagi "tarviha" so‘zining ko‘pligidir. To‘rt rakat o‘qib, ortidan dam olingani uchun bu namoz shunday nomlangan.
Ramazon oyi fazilatlarga boydir. Uning fazilatlaridan biri oy davomida xufton namozidan keyin tarovih namozi o‘qishdir. Payg‘ambarimiz sallallohu alayhi vasallam tarovih namozi haqida shunday deganlar:
“Alloh taolo Ramazon ro‘zasini farz qildi va men uning qiyomini sizlar uchun sunnat qildim. Kimki iymon va ishonch bilan, savob umidida ro‘za tutsa va kechalari qoim tursa, onadan tug‘ilgan kunidagidek gunohlardan pok bo‘ladi” (Imom Nasoiy rivoyatlari).
<a href='https://t.me/namoz_uqishni_urganish_Kanal/20'>Bizning kanal📢</a> 
""", reply_markup=admin_keyboard.jamoat)

@dp.callback_query(F.data == "qaytish")
async def qaytar_handler(callback: CallbackQuery):
    await callback.message.answer(text="Menyulardan birini tanlang", reply_markup=admin_keyboard.start_buttonnew)
    await callback.message.delete()

@dp.callback_query(F.data == "orqa_qaytish")
async def qaytar_handler(callback: CallbackQuery):
    await callback.message.answer(text="Menyulardan birini tanlang", reply_markup=admin_keyboard.tanlash_)
    await callback.message.delete()

#Haj   ---------------============
@dp.message(F.text=="HAJ")
async def message(message:Message,state:FSMContext):
    await message.answer(text="HAJ",reply_markup=admin_keyboard.haj)

@dp.callback_query(F.data == "haj_orqaga")
async def haj_orqaga(callback: CallbackQuery):
    await callback.message.answer(text="Haj", reply_markup=admin_keyboard.haj)

@dp.callback_query(F.data == "qanday_ibodat")
async def qanday_ibodat(callback: CallbackQuery):
    await callback.message.answer(text="""   
Haj ibodatining boshqa ibodatlardan bir farqi shuki, u hammaga ham bir paytning o‘zida farz bo‘lavermaydi, balki ayrim shartlariga muvofiq kelgan musulmonlargagina farzdir. Qodir bo‘lgan odamlarga Alloh uchun Baytni haj qilish farz. Ulamolar kishiga haj farz bo‘lishi uchun quyidagi shartlar mavjud bo‘lishi kerakligini ta’kidlashgan:

1) musulmon bo‘lishi;

2) balog‘atga etgan bo‘lishi;

3) oqil bo‘lishi;

4) hajga qodir bo‘lishi;

5) sog‘-salomat bo‘lishi;

6) hukumat man qilmagan bo‘lishi;

7) yo‘lda omonlik bo‘lishi;

8) ayol kishiga mahrami bo‘lishi;

Kimda ushbu shartlardan birortasi bo‘lmasa, unga haj farz bo‘lmaydi.
Haj – Islomning besh arkonidan biri bo‘lgan ulug‘ rukn, Allohga mahbub ibodatdir. Bu ibodat Alloh taologa yuzlanish, U Zotning tajalliysi, nurining markazi bo‘lgan maskanda ado etiladi. Hadisi shariflarda kelishicha, Baytullohi sharif shunday makonga joylashganki, uning ayni ustida, yettinchi osmonda Baytul Ma’mur, uning ustida esa Alloh taoloning Arshi joylashgan. Alloh taoloning tavajjuhi, nuri va tajalliyoti dastlab Ka’batullohga nozil bo‘lib, keyin butun olamga tarqaladi. Shu sababli bu yerga kelish baxtiga musharraf bo‘lgan musulmonlar uchun ulkan saodat bor.
Haj oshiqona ibodat bo‘lib, u yerga borish faqat hazrati Ibrohim alayhissalomning haj e’loniga «labbay» deb javob bergan kishilargagina nasib etadi. U necha marotaba labbay degan bo‘lsa, Ka’batullohni o‘shancha marta tavof qilish sharafiga muyassar bo‘ladi. Shuningdek, u yerga borib, haj ibodatini ado etish yana bir saodatga sababdir.
Haj ibodatida ulkan hikmatlar bo‘lib, bu hikmatlarning barchasini insonning ojiz aqli to‘la anglab olishi qiyin. Shunday bo‘lsa ham ulamolar ijtihod qilganlar.
Hajda islomiy birlik yorqin namoyon bo‘ladi. Haj chog‘ida musulmonlarning his-tuyg‘ulari, ibodat la ri va hatto suvratlari bir xil bo‘ladi. Bu erda irqchilik, mahalliychilik, tabaqachilik kabi salbiy holatlarga o‘rin qolmaydi. Hamma bir Allohga iymon keltirib, bir Baytullohni tavof qiladi. Tinchlik Islomning shiori ekani hajda yana bir bor namoyon bo‘ladi. Hamma tinch, yurt tinch, ibodat tinch, xalq tinch bo‘ladi
Haj ulkan islomiy anjuman bo‘lib, har bir musulmon dunyoning turli burchaklaridan kelgan din qardoshlari bilan uchrashadi, turli masalalarni muhokama qiladi. Islom va iymon rishtalari mustahkamlanadi.
Hajda musulmon banda omonlik yurti bo‘lmish Makkai mukarramaga safar qiladi. Makka – ulug‘, muqaddas shahar. Alloh taolo Qur’oni Karimda uning nomi bilan qasam ichgan. O‘zining uyi bo‘lmish Ka’baning shu shaharda qaror topishini iroda qilgan.
Haj ulug‘ ruhiy ozuqa beradigan ibodat bo‘lib, unda musulmon bandaning vujudi Alloh taologa taqvo bilan, Unga toat qilishga azmu qaror bilan, gunohlariga nadomat bilan to‘ladi. Bu safarda musulmon kishining Allohga, Uning Rasuliga va mo‘min-musulmonlarga bo‘lgan muhabbati ziyoda bo‘ladi. Dunyoning hamma taraflaridagi din qardoshlariga nisbatan do‘stlik tuyg‘ulari uyg‘onib, mustahkamlanadi. 
""",reply_markup=admin_keyboard.haj_ortga)
    

@dp.callback_query(F.data == "haj_odoblari")
async def haj_odoblari(callback: CallbackQuery):
    await callback.message.answer(text="""   
1. Haj va umrani niyat qilgan kishi avvalambor bu ulug‘ safardan Alloh taoloning roziligini maqsad qilishi hamda riyokorlik, odamlar eshitsin kabi illatlardan o‘zini poklashi lozim;
2. Safar oldidan kishi o‘zining vasiyat, qarz oldi-berdilari va omonatlarini yozib qoldirishi mustahab amallardan;
3. Gunohlariga qattiq tavba qilishi va ularni hech qachon qaytarmaslikka niyat qilishi kerak;
4. Kishilarning unda haqlari bo‘lsa yoki ularga nohaqliklar qilgan bo‘lsa, haqlarini egalariga qaytarish, zulm qilgan kishilaridan esa, avf etishlarini so‘rash lozim;
5. Alloh taolo faqat halol mollardan qilingan nafaqalarnigina qabul qilishini e’tiborga olib hajga ishlatiladigan nafaqalarini ham faqat haloldan to‘plash lozim;
6. Barcha gunohlardan, jumladan til va qo‘ldan sodir bo‘ladigan chaqimchilik, g‘iybat, bilmagan narsasini gapirish, atrofidagilarga qo‘pollik qilish, haj va umrani ado etayotganlarni noqulay ahvolga solib qo‘yish kabilardan saqlanish lozim. Atrofdagilarga nisbatan rahm-shafqatli, mehribon va xushmuomalada bo‘lish musulmon kishining fazilatidandir;
7. Haj va umrani niyat qilgan kishi haj va umra amallari qanday ado etilishini yaxshi bilib olishish lozim;
8. Haj ziyoratiga otlangan kishilar zimmalaridagi farz va vojib amallarni to‘liq bajarishga jiddu-jahd qilishlari lozim. Xususan, namozlarni o‘z vaqtida jamoat bilan ado qilish, zikr, duo, Qur’on tilovati va istig‘forlar aytish, muhtoj kishilarga yordam ko‘rsatish kabi ishlarni qilishi tahsinga loyiq ishlardandir;
9. Safar davomida solih va bilimdon hamrohlar bilan birga bo‘lishi ham mustahab amallardan sanaladi;
10. Safarga otlangan kishilar go‘zal xulqli bo‘lishga va odamlar bilan xushxulqda muomala qilishga e’tibor berishlari lozim. Bu esa o‘z-o‘zidan sabr qilish, avf etish, muloyimlik, mehribonlik, halimlik, kamtarinlik, shoshmaslik, sahovatli bo‘lish, adolatli va omonatdor kabi xislatlarni o‘z ichiga oladi;
11. Safarga otlangan kishi o‘z oilasini Allohdan taqvo qilishga chaqirishi lozim. Chunki bu, Alloh taoloning bandalarga ko‘rsatmasi;
12. Safarga otlangan kishi Payg‘ambarimiz sollallohu alayhi va sallamdan vorid bo‘lgan duolarni yodlab olishi mustahab amallardandir.
Alloh Taalo barcha hojilarimizni hajlarini mabrur hajlardan qilsin!

""",reply_markup=admin_keyboard.haj_ortga)


@dp.callback_query(F.data == "hajning_nozik_sirlari")
async def hajning_nozik_sirlari(callback: CallbackQuery):
    await callback.message.answer(text="""   
Alloh taologa yetishish uchun butunlay Uning O‘zini ko‘zlagan holda ajrab chiqmoq kerak bo‘ladi. Shuning uchun ham qadimgi rohiblar Alloh taologa yetishish maqsadida hamma narsadan ajrab, tog‘larga chiqib ketar edilar.
Islomda rohiblik yo‘q. Ammo taqqoslash uchun aytadigan bo‘lsak, Islom ummatining rohibligi hajdir. Haj ibodatini ado etmoqchi bo‘lgan banda barcha shahvatlar, lazzatlardan, aloqa va mashg‘ulotlardan, hatto odatdagi kiyimlaridan ham ajraydi.
Hajning har bir amalida eslatma va ibrat bor:
1. Hajga kerak bo‘ladigan narsalarni jamlaganda oxiratga kerak bo‘ladigan narsalarni esiga olsin.
2. Oddiy kiyimlarini yechib, ehromga kirayotganida kafanni va Robbiga bu dunyo kiyimlaridan boshqacha kiyim ila ro‘baro‘ bo‘lishini esga olsin.
3. «Labbayka»ni aytishni boshlaganida Alloh taoloning chaqirig‘iga javob berayotganini esga olsin va qabulni orzu qilib, qabul bo‘lmay qolishidan qo‘rqsin.
4. Haramga yetganda uqubatdan omon qolishni orzu qilsin va yaqinlardan bo‘lmay qolishdan qo‘rqsin. Ammo umidvorlik g‘olib bo‘lsin.
5. Baytullohni ko‘rganida qalbida uning ulug‘vorligini hozir qilsin va Alloh taologa o‘zini mehmonlari martabasiga erishtirgani uchun shukr qilsin hamda Baytullohni tavof qilish naqadar ulug‘vorligini his etsin.
6. Hajarul asvadni istilom qilgan (uni qo‘li bilan ushlagan yoki ishora qilgan) paytida Alloh taologa itoat qilishga bay’at qilganiga e’tiqod qilsin va bu bay’atga vafo qilishga azmu qaror qilsin.
7. Ka’bai Muazzamaning pardasiga osilganida va Multazamda turganida gunohkor o‘z xojasining panohiga qochganini eslasin.
8. Safo va Marva orasida sa’yi qilayotgan paytida ularni «tarozining ikki pallasi» deb o‘ylasin. Ularning orasida borib-kelishini «qiyomatning arosati» deb o‘ylasin.
9. Arafotda turganida, odamlarning izdihomini ko‘rganida, ovozlarining ko‘tarilishini eshitganida, tillarining turli-tumanligini bilganida qiyomat mavqifini, unda xaloyiqning jamlanishini va shafoat so‘rashlarini esga olsin.
10. Tosh otish paytida qullikni namoyon qilishni va farmonga bo‘ysunib, uni so‘zsiz bajo etishni qasd qilsin.
11. Qurbonlik so‘yish paytida bu ishning Alloh taologa qurbat hosil qilishning eng muhim turlaridan biri ekanini, qurbonlikning har bir bo‘lagi evaziga qurbonlik qiluvchining bir bo‘lagi do‘zaxdan xalos bo‘lishini eslasin
""",reply_markup=admin_keyboard.haj_ortga)


@dp.callback_query(F.data == "haj_tavsiya")
async def haj_tavsiya(callback: CallbackQuery):
    await callback.message.answer(text="""   
Haj safariga chiquvchiga tavsiyalar
Muborak haj safariga tayyorgarlik ko'rayotgan kishiga haj kitoblarida quyidagi
ko'rsatmalar beriladi:
1)Haj safariga otlanuchi kishi o'zidan ko'ngli ranjigan kishilarning ko'ngillarini ovlashi, ularni rozi gilishi zarur.
2)Odamlar bilan muomalani to'g'rilashi.
3)Biror kishiga zulm qilgan bolsa, undan kechirim so'rashi.
4)Biror kishining molini nohaq yeb qo'ygan bo'lsa, uni o'ziga yoki merosxo'rlarigaqaytarib berishi.
5)Barcha qilgan gunohlariga astoydiltavba qilishi.
6)Ota-onasini rozi qilib safar qilishi.
7)Bola-chaqalarini hotirjam qilib safar gilishi.
8)Qarzlarini ado qilib safarga chiqishi.
9)Solih kishilar bilan safar gilishi.
10)Hajning farz va vojib masalalarini yaxshilab o'rganib olishi;
11) O'zi bilan Haj kitobini olishi.
12) Safarga tijorat maqsadlarini aralashtirmay, xolis ibodat maqsadidasafar qilishi.
13) Riyo va shuhratparastlikdan o zini yiroq tutishi.
14) Safar davomida o'zini xokisor va tavoze bilan tutishi.
15) Zaruriy narsalarni sotib olish chog ida sotuvchi bilan haddan ziyod tortishmasligi;
16) Haj safari davomida pul sarflashda xasislik qilmasligi;
17) Sheriklariga sarf-xarajat qilish to'g'ri kelib qolsa, mamnuniyat bilan ularga sarf qilishi.
18) Uydan chiqib ketayotgan vaqtidasadaqa qilishi.
19) Safar davomida hojatmand odamlarga sarf qilaman deb o'zi bilan ortiqcha mablag' olishi.
20) Ikki rakat namoz o'qib yolga chiqishi.
21) Uydan chiqib ketayotgan paytda
odamlar bilan qo'l berib so'rashib, ulardan haqqiga duo qilib turishlarini so rashi.
22) Boshqalarning ham haj gilishga ketayotgan kishidan duo qilishini so'rashlari.
23) Kuzatuvchi ham, safarga ketuvchi ham o'z duolarini o'qishlari.
24) Safar duosini o'qishi.
25) Safar davomida qaerga tushsalar, o'sha joyda ikki rakat namoz o'qib olishi (mustahab).
26) Safar davomida Alloh taoloning zikrini qilib, ota-onasi, farzandlari va barcha musulmonlar haqgiga duo gilishi.
27) Safar davomida tortishish, dilozorlik va tilozorlik kabi narsalardan saqlanishi.
28) Barchaga halimlik bilan, xushmuomalada bolishi.
29) Besh vaqt namozni imkoni boricha jamoat bilan ado qilishi.
30) Namozlarni o'z vaqtida ado qilishi. 
31) Sunnati ravotiblarni iloji boricha tark qilmasligi                                                                   
""",reply_markup=admin_keyboard.haj_ortga)


@dp.callback_query(F.data == "haj_ibodat_turlari")
async def haj_ibodat_turlari(callback: CallbackQuery):
    await callback.message.answer(text="""   
Demak, haj turlari uchta:

1)Ifrod;
2)Tamattu'
3)Qiron;
                                  
1. Ifrod haji deb miqotdan faqat haj qilish uchun ehromga kirishga aytiladi. Ifrod haj qiluvchi kishi Makkaga kelgach, tavofi qudum qilib, haj amallarini ado etishga kirishadi va qurbonlik kuni shaytonga tosh otganidan keyin ehromdan chiqadi. Ifrod haj qiluvchi zimmasiga qurbonlik qilish vojib bo‘lmaydi. Faqat bir tavof va bir sa'y qilish vojibdir. Bugungi kunda ifrod hajini qilish birmuncha mashaqqatlidir. Chunki bu tur hajni niyat qilgan kishi Makkai mukarramaga kelgan kunidan boshlab to qurbon hayiti kuni shaytonga tosh otib, sochini qisqartirgunigacha ehromda bo‘lishi va ehrom tartib-qoidalariga qat'iy amal qilishi shartdir. Agar shu vaqt oraligida ehromda qaytarilgan ishlarni unutib qilib qo‘ysa, zimmasiga kafforat lozim bo‘ladi. Masalan, mo‘ylabi o‘sib ketsa-yu uni qisqartirish, olish mumkin emasligini unutib, olib qo‘ysa yoki xushbo‘ylanib qo‘ysa, jarima lozim bo‘ladi. Ammo shuncha qiyinchilikka yarasha, bu hajning savobi boshqalarga qaraganda ko‘proqdir.
2. Tamattu' haji. “Tamattu'” arabcha so‘z bo‘lib, “foydalanish”, “maza”, “huzur qilish” ma'nolarini anglatadi. Avval umrani ado etib, haj vaqtigacha ehrom harom qilgan narsalardan huzur qilib yurib, vaqti kelganda yana ehromga kirib hajni niyat qilgan odam “Tamattu' haj qiluvchi” deyiladi. Hanafiy mazhabi bo‘yicha tamattu' ifrod hajidan ulug‘ bo‘ladi. Tamattu' haj oylarida Makkaga tashqaridan keluvchilarga joiz. Makkada yashovchilarga va u yerga haj oylaridan oldin kelib, hajni kutib turganlarga joiz emas. Tamattu' hajini ifroddan asosiy farqlari quyidagilar.
U ehromga kirayotganda umranigina niyat qiladi. So‘ng “Talbiya” aytib boradi. Makkaga kirib umra tavofini qiladi. Birinchi tavofdayoq talbiyani to‘xtatadi. So‘ng Safo va Marva orasida sa'y qilib bo‘lgach, sochini oldirib yo qisqartirib ehromdan chiqadi. So‘ng haj vaqti kelishini kutib turadi. Zulhijja oyining 8-kuni Haromda ehromga kiradi va niyat qiladi.
So‘ng ikki rakaat namoz o‘qiydi. Ka'bani tavof qiladi, Safo va Marva orasida sa'y qilib olsa yaxshi bo‘ladi. So‘ng ifrod haji amallarini qilgandek amallarni qiladi. Hayit kuni tong otgandan so‘ng jonliqni so‘yadi. Keyin sochini oldirib yo qisqartirib ifoza tavofini qiladi. Agar ehrom bog‘lagan paytda tavof va sa'y qilmagan bo‘lsa ifoza tavofidan so‘ng Safo va Marva orasida sa'y qiladi. Tamattu' niyat qilgan odam o‘ziga vojib bo‘lgan jonliqni so‘yishga qodir bo‘lmasa, o‘rniga ro‘za tutadi. Bu ro‘zaning umumiy miqdori o‘n kun. Shundan uch kuni Arafadan avval tutilishi shart. Eng yaxshisi Arafa kuni va undan avvalgi ikki kun ro‘za tutishdir. Arofatda charchab qolmay desa, bir kun oldin tutsin. Yetti kuni hajdan keyin o‘z yurtida tutiladi.
""",reply_markup=admin_keyboard.haj_davomi)

@dp.callback_query(F.data == "davomi_haj")
async def davomi_haj(callback: CallbackQuery):
    await callback.message.answer(text="""   
3. Qiron haji. “Qiron” so‘zi “yaqinlik”, “qo‘shilish” ma'nolarini anglatadi. Umra bilan yaqinlashtirib, bir-biriga qo‘shib qilingan hajni “qiron” haji deyiladi. Qironning ifroddan farqi shuki, ehromga kirishda niyat qiladi. Keyin talbiya aytadi. Makkaga kelgach, umra uchun tavofni ado etib, Safo va Marva orasida sa'y qiladi. Ammo sochini oldirmaydi, ehromdan chiqmaydi. Chunki unda hali hajning niyati bor. Keyin haj uchun yana bir tavof qiladi va sa'y ado etadi. Qolgan amallar ifrod hajinikiga o‘xshab ketadi. Hayit kuni tosh otishdan so‘ng qurbonlik qilish vojib. Jonliq so‘yayotganda “Qiron uchun” yo “Dami shukr” deb niyat qiladi. Undan so‘ng sochini oldiradi yo qisqartiradi. Ushbu tartib zarurdir. Ifoza tavofi qilingandan so‘ng, avval haj uchun sa'y qilmagan bo‘lsa sa'y qiladi. Qurbonlik so‘yishga imkoni yo‘qlar tamattu'ga o‘xshab ro‘za tutadilar.
""",reply_markup=admin_keyboard.haj_ortga)
    

@dp.callback_query(F.data == "hajning_farzi")
async def hajning_farzi(callback: CallbackQuery):
    await callback.message.answer(text="""   
Hajning farzlari uchta 
1. Ehrom. 
2. Arofatda turish.
3. Ziyorat tavofi.
                                  
Hajning vojiblari
1. Miyqotdan ehrom bog‘lamoq.
2. Safo va Marva oralig‘ida sa'y qilmoq.
3. Sa'yni Safodan boshlamoq.
4. Sa'yda yurmoq. Shuningdеk, tavofda ham yurib sa'y qilmoq.
5. Kun bo‘yi Arofatda turgan kishi, shomgacha Arofatda        turishni davom ettirmog‘i.
6. Arofatdan imomni orqasidan (undan kеyin) chiqib kеtmoq.
7. Muzdalifada (tong otgandan kеyin) bir daqiqa bo‘lsa ham turmoq.
8. Ikki kеchgi (shom va xufton namozlarini) shomni xuftonga kеchiktirib o‘qimoq.
9. Bir qavlda aytildi: kеchaning bir bo‘lagida Muzdalifada tunamoq. U shoz (ozchilikning) gapi.
10. Uch kun shaytonga tosh otish.
11. (Hayitning birinchi kunidagi) katta shaytonga tosh otish amaliyotini soch oldirishdan oldin amalga oshirish.
12. Shaytonga tosh otiladigan har bir kunni tosh otishini ikkinchi kunga kеchiktirmaslik. Agar tosh otishni ertangi kunga kеchiktirsa, u qazo bo‘lib gunohkor bo‘ladi. Bir namozni boshqa namozning vaqtiga kеchiktirganga o‘xshash.
13. Bir qavlda aytildi: har bir tosh otishni, soch oldirish va tavofni tartib bilan amalga oshirish vojibdir. Bu so‘z mashhur gapga xilofdir. Bu gapni e'tibori yo‘q. 
14. Haytning birinchi kuni katta shaytonga tosh otgandan kеyin, ehromdan chiqish uchun sochni tagidan oldirmoq yoki sochni to‘rtdan bir qismini qisqartirmoq.
15. Sochni tagidan oldirmoq yoki sochni to‘rtdan bir qismini qisqartirmoq amaliyoti qurbonlik kunlari, Haramda amalga oshirilmog‘i.
16. Ziyorat tavofini qurbonlik kunlarida qilmoq.
17. Hatmni (Ka'bai muazzamani yonidagi Ka'bani eski binosinig poydеvori yoki bir bo‘lagi) orqasidan tavof qilmoq.
18. Bir qavlda aytildi: Tavof qilishni hajarul asvaddan boshlamoq. Sahihrog‘i u amal sunnati muakkadadir (takidlangan sunnatdir).
19. Tavofda tahoratli bo‘lmoq.
20. Tavofni o‘ngdan boshlamoq.
21. Avrat yopilishi.
22. Erkak kishini ehromi, ayolni kiygan kiyimi pok bo‘lishi.
23. Tavofda yurmoq.
24. Tavofdan kеyin ikki rakat tavof namozini o‘qimoq.
Ushbu vojiblar makkaliklar va atrofdan borganlar uchun umumiydir.
Makkaliklardan boshqalarga hajning xos vojib amallari esa:
25. Vidolashuv tavofi.
26. Qiron haj qiluvchi, jonliq so‘yishdan oldin katta shaytonga tosh otmog‘i.
27. Tamattu' haj qiluvchi, jonliq so‘yishdan oldin katta shaytonga tosh otmog‘i.
28-29. Qiron va Tamattu' haj qiluvchi jonliq so‘yishi.
30-31. Qiron va Tamattu' haj qiluvchi soch oldirishdan oldin jonliq so‘yishi. 
32-33. Qiron va Tamattu' haj qiluvchi qurbonlik kunlarida jonliq so‘yishi.
34. Bir qavlda aytildi: Qudum tavofi. Sahih qavlga ko‘ra Qudum tavofi vojib, lеkin jumhur uni sunnati muakkada (ta'kidlangan sunnat) dеyishgan.
35. Ehromda man qilingan amallarni tark qilish ham vojiblar jumlasiga kiradi.

 Hajning sunnatlari
1. Hajning o‘zini Qiron (bir ehrom bilan haj va umra qilishni) niyat qilgan kishi uchun qudum tavofini qilmoq sunnatdir. Umrani o‘zini niyat qilib, ehrom bog‘lagan kishi va tamattu' haj qiluvchi (umraga ehrom bog‘lab uni bajargandan kеyin, ehromdan chiqib haj kunlari kеlganda yana haj uchun ehrom bog‘lagan kishi) uchun qudum tavofi sunnat emas. Tamattu' haj qiluvchi ham, tanho umra qiluvchiga o‘xshaydi. Chunki miyqotdan umraga ehrom bog‘laydi. Makkaga kеlib umrani ehromidan chiqqandan kеyin, haj masalasida makkalikka o‘xshaydi. Makkalikka Qudum tavofi sunnat emas.
Qudum tavofini vojib dеganlar uchun ham xuddi shuningdеk, umrani o‘zini niyat qilib, ehrom bog‘lagan kishi va tamattu' haj qiluvchi uchun qudum tavofi vojib emas. 
2. Tavofni Qora toshdan boshlamoq.
3. Imom uch joyda xutba qilmog‘i. Zulhijjani yettinchi kuni Makkada. To‘qqizinchi kuni Arofatda. O‘n birinchi kuni Minoda.
4. Tarviya kuni Makkadan Minoga chiqib kеtmoq.
5. Arafa kеchasi Minoda tunamoq. 
6. Arafa kuni quyosh chiqqandan kеyin Arofatga kеtish.
7. Arofat uchun g‘usl qilish.
8. Muzdalifada tunamoq.
9. Minodan Muzdalifaga quyosh chiqmasdan kеtish.
10. Shaytonga tosh otish kunlarida minoda tunamoq.
11. Bir daqiqa bo‘lsa ham Muhassab dеgan joyga tushmoq                                                                   
""",reply_markup=admin_keyboard.haj_ortga)
    

@dp.callback_query(F.data == "ehromga_kirish")
async def ehromga_kirish(callback: CallbackQuery):
    await callback.message.answer(text="""   
Hamma tayyorgarliklar nihoyasiga etib, haj amallarini boshlash navbati keladi. Shunda haj amallari­dan birinchisi ehrom bo‘ladi.
“Ehrom” arabcha so‘z bo‘lib, lug‘atda «harom qilmoq» maʼnosini anglatadi. Ehromga kirgan odam uchun ehromdan oldin halol bo‘lgan baʼzi ish va narsalar harom bo‘ladi. Misol uchun, boshqa vaqtlarda o‘ziga xushbo‘y narsalarni sepishi halol edi, ehromga kirgach, bu narsa harom bo‘lib qoladi.
Ehromning haqiqati haj yoki umra yoki ikkalasiga birdaniga niyat qilib, talbiya aytishdir. Ehrom uchun faqat niyat qilish yoki talbiya aytish kifoya qilmaydi. Namozda qalb bilan niyat, til bilan esa takbiri tahrima aytilishi lozim va shart bo‘lgani kabi haj yoki umra ehromiga kirishda ham niyat bilan talbiya birgalikda topilishi lozimdir. Shu bois dilda niyat qilib, til bilan talbiya yoki uning o‘rnini bosadigan Alloh taoloning zikri aytilmasa, ehromga kirgan hisoblanmaydi. Shuningdek, til bilan talbiya yoki uning o‘rnini bosadigan Alloh taoloning zikrini aytib, qalbda ehromga kirishni niyat qilmasa, ehromga kirgan bo‘lmaydi.
Erkak kishining umra yoki haj niyatida tikilgan kiyim kiyishi joiz emas. Agar tikilgan kiyim kiysa, kafforat vojib bo‘ladi. Masalan, yoqasi yo‘q ko‘ylak, ishton, qo‘lqop, mahsi, mayka, do‘ppi, kostyum, kamzul kabilar tikilgan kiyim sanaladi. Agar erkak kishi yuqoridagi kiyimlardan birortasini ehrom holatida kiyib olsa, jarima va fidya lozim bo‘ladi. Shuning uchun ehrom kiyimlari tikilmagan bo‘lishi shartdir. Ehromning sunnati ikki oq mato olib, birini lungi kabi, ikkinchisini esa katta sochiq kabi yelkasiga tashlab olishdir. Faqat tavof vaqtida yuqorisiga tashlab olgan katta sochiq kabi matoni chap yelkasini ochib qo‘ltig‘ining ostidan o‘tkazib oladi.
Ehrom holatidagi erkak kishilarning qomatiga munosib shaklda tikilgan kiyimni kiyib olishi joiz emas. Lekin shim yoki shalvar tarzida bo‘lmay, qop kabi tikilib, ikki tomonini ochib olinsa, zarari yo‘q, yaʼni karohiyatsiz joizdir. 
Ehromga kipmoqchi bo‘lgan odam sochi, tirnog‘i, mo‘ylabini va olinishi lozim bo‘lgan tuklapini olib, so‘ngra g‘usl qiladi. Keyin ikki parcha oq, yangi yoki yuvilgan matoni (xalq tilida «ehrom kiyimi»ni) olib, bipini kindigi bilan tizzasini qo‘shib to‘sadigan holatda beliga tutadi. bu«izor» deyiladi. Ikkinchisini yelkasi aralash aylantirib o‘raydi. Bunisi «rido» deyiladi. Badaniga va ehrom kiyimiga xyshbo‘y narsa surtadi, ammo u narsaning rangi kiyimda qolmasligi shart qilinadi.
so‘ngra ikki rakat namoz o‘qiydi. Birinchi rakatda Fotiha supasidan keyin Kafirun, ikkinchi rakatda Ixlos spuasini o‘qiydi. so‘ngra qaysi hajni qilmoqchi bo‘lsa, o‘shanga mos niyat qiladi. Masalan, ifrod hajining niyati:
اللَّهُمَّ إِنِّي أُرِيدُ الْحَجَّ فَيَسِّرْهُ لِي وَتَقَبَّلْهُ مِنِّي.

«Allohyumma inni uridul hajja fa yassirhu li va taqobbalhy minni.
Yaʼni, «Allohim, men hajni iroda qilaman, uni menga oson etgil va qabyl aylagil».
Tamattyʼ hajining niyati:
اللَّهُمَّ إِنِّي أُرِيدُ الْعُمْرَةَ فَيَسِّرْهَا لِي وَتَقَبَّلْهَا مِنِّي.

«Allohymma inni uridul umrata fa yassirha li va taqobbalha minni».
Yaʼni, «Allohim, men umrani iroda qilaman. Uni menga oson etgil va qabul aylagil».
Qiron hajining niyati:
اللَّهُمَّ إِنِّي أُرِيدُ الْعُمْرَةَ وَالْحَجَّ فَيَسِّرْهُمَا لِي وَتَقَبَّلْهُمَا مِنِّي.
«Allohumma inni uridul umrata val-hajja fa yassipuyma li va taqobbalhuma minni»
Yaʼni, «Allohim, men umra va hajni iroda qilaman, ularni menga oson etgil va qabyl aylagil».
Agar biror kishi nomidan haji badal qilayotgan bo‘lsa, o‘sha kishi nomidan niyat qilib quyidagi duoni o‘qiydi:
اللَّهُمَّ إِنِّي أُرِيدُ الْحَجَّ عَنْ فُلَانٍ فَيَسِّرْهُ لِي وَتَقَبَّلْهُ مِنِّي عَنْهُ.

«Allohumma innii uridul hajja ʼan fulonin fa yassirhu li va taqobbalhu minni ʼanhu».
Maʼnosi: «Allohim, falonchining nomidan hajni iroda qildim, uni menga oson etgin, men va uning tarafidan qabul etgin.
""",reply_markup=admin_keyboard.haj_ortga)
    


# qoldi 
@dp.callback_query(F.data == "ehromdagi_amallar")
async def ehromdagi_amallar(callback: CallbackQuery):
    await callback.message.answer(text="""   
hromda qilish va qilmaslik kerak bo‘lgan amallar juda ko‘p bo‘lib, ulardan eng ahamiyatlilari yigirma sakkiztadir. Bular quyidagilar:  
1.Ehrom holatida bit o‘ldirish:
Ehrom holatida bit o‘ldirish joiz emas.
2. Ehromda taxta kana va chivinni o‘ldirish:
Ehrom holatida badandan paydo bo‘lmaydigan aziyat beruvchi jonivor va hasharotlarni o‘ldirish joizdir.
3. Ehrom holatida chumolini o‘ldirish:
Ehrom holatida chaqib aziyat beradigan qora, sariq chumolilarni o‘ldirish karohiyatsiz joiz bo‘lib, ularni o‘ldirgan kishiga jarima lozim bo‘lmaydi.
4. Ehrom holatida chigirtka o‘ldirish:
Harami sharifda chigirtkalar juda ko‘p bo‘lib, ularga aziyat berishdan saqlanish lozim.  
5. Ehrom holatida janjallashish:
Haj qiluvchining odamlar bilan janjallashishi va ularni fahsh so‘zlar bilan so‘kishi qattiq gunohdir.
6. Ehrom holatida ayolini o‘pib, quchoqlashish:
Ehrom holatida shahvat bilan er o‘z ayolini o‘psa, quchoqlasa, jarimasiga bir qo‘y yoki echkini qurbonlik qilishi vojib bo‘ladi.
7. Ehrom holatida soch olish:
Agar ehromdagi kishi boshining hamma qismidagi yoki to‘rtdan biridagi yoki undan ziyodadasidagi sochini ozaytirsa yoki oldirsa, qon (jonliq so‘yish) vojib bo‘ladi. Agar to‘rtdan biridan oz bo‘lsa, jarima sifatida sadaqa, ya’ni yarim so’ sadaqa qilish vojib bo‘ladi.  
8. Ehrom holatida soqol olish yoki qisqartirish:
Ehromdan chiqish vaqti kelishidan avval soqolni to‘liq qirdirish yoki to‘rtdan birini yoki undan ziyodarog‘ini oldirish qonni (jonliq so‘yishni) lozim qiladi. Agar to‘rtdan biridan kam bo‘lsa, jarima sifatida sadaqa, ya’ni yarim so’ sadaqa qilish vojib bo‘ladi.
9. Ehrom holatida qo‘ltiq osti tukini olish:
Ehrom holatida ikki yoki bir qo‘ltiqning tuki olinsa, jarimasiga qon lozim bo‘ladi.
                                  
""")
    await callback.message.answer(text="""
10. Ehrom holatida kindik osti tukini olish:
Ehrom holatida kindik osti tukni olinsa, jarimasiga qon vojib bo‘ladi.
11. Bir vaqtda sochni, soqolni va butun tanadagi tuklarni olish:
Ehromdagi kishi bir vaqtda soch, soqol va qo‘ltiq hamda kindik osti tuklarini olsa, barchasining evaziga bir qon (jonliq) vojib bo‘ladi. Agar turli vaqtlarda olsa, har bir vaqt uchun alohida-alohida qon vojib bo‘ladi.
12. Soch yoki soqolning ikki yoki uch tolasini, qo‘ltiq yoki kindik osti tuklaridan ikki yoki uch tolasini yulib olish:
Agar soch, soqoldan ikki yoki uch tola, qo‘ltiq yoki kindik osti tuklaridan ikki yoki uch tola yulinsa, jarimasiga bir siqim bug‘doy yoki uning qiymati sadaqa qilinadi.
13. Ehrom holatida mo‘ylovni qisqartirish:
Ehrom holatida mo‘ylovning hammasini yoki bir qismini qisqartirsa, jarimasiga sadaqai fitr lozim bo‘ladi;
14. Soch, soqol, qo‘ltiq va kindik osti tuklaridan boshqa joylarda o‘sgan tuklarni olish:
Soch, soqol, qo‘ltiq va kindik osti tuklaridan boshqa joylarda o‘sgan tuklarni olishda o‘zgacha bir yo‘l tutiladi, ya’ni a’zoning hammasidagi yoki bir qismidagi yoki to‘rtdan biri yoki undan kam qismidagi tuklarni olishga jarima sifatida bir sadaqai fitr lozim bo‘ladi.
15. Ehrom holatida tirnoq olish:
Bir qo‘l tirnoqlari yoki bir oyoq tirnoqlari yoki bir vaqtda ikki qo‘l va ikki oyoq tirnoqlarini olgan kishining zimmasiga bir qon (jonliq so‘yish) vojib bo‘ladi. Agar ushbu to‘rt a’zo tirnoqlarini turli vaqtda, to‘rt joyda olsa, to‘rtta qon lozim bo‘ladi. Shuningdek, bir a’zo tirnoqlarini bir vaqtda olib, ikkinchi a’zo tirnog‘ini boshqa vaqtda olsa, ikkita qon lozim bo‘ladi. Agar to‘rt a’zo tirnoqlarini olishda bir joyda yoki turli joyda o‘tirib har barmoqdan beshtadan kam, ya’ni to‘rtta va undan kam barmoq tirnoqlarini olsa, har bir olingan barmoq tirnog‘iga bittadan sadaqai fitr lozim bo‘ladi.
16. Ehrom holatida tikilgan kiyim kiyish:
Ehrom holatidagi erkak kishining tikilgan kiyim kiyishi joiz emas. Jumladan, yoqasiz ko‘ylak, ishton, qo‘lqop, mahsi, mayka, do‘ppi, kostyum, kamzul kabilarni kiyish mumkin emas. Badanga moslab tikilmagan narsalarni kiyish karohiyatsiz joizdir. Shuning uchun bir-biriga ulangan matoni hoji ehrom sifatida o‘rab olishi joiz bo‘ladi.
17. Ehrom holatida tikilgan kiyim kiyishga belgilangan jarima:
Bir kishi bir kun yoki bir kecha yoki bir kun miqdorida, ya’ni o‘n ikki soat yoki bir necha kun uzuluksiz tikilgan kiyim kiysa, qon lozim bo‘ladi. Bir kishi kunduzi kiyim kiyib, kechasi «ertaga ham kiyaman» degan maqsadda yechinsa, ikkisiga ham bir qon lozim bo‘ladi. Agar yotishdan oldin «ertaga kiymayman» degan maqsadda tikilgan kiyimini yechib, ertasi kuni yana tikilgan kiyimni kiysa, ikki qon lozim bo‘ladi. Agar bir kun yoki bir kechadan kam yoki bir soatdan ziyoda tikilgan kiyim kiysa, sadaqai fitr lozim bo‘ladi. Agar bir soatdan kam tikilgan kiyim kiysa, bir yoki ikki hovuch bug‘doy yoki uning qiymatini sadaqa qilishi lozim bo‘ladi.                                   
19. Ehrom holatida xushbo‘ylik surtish: 
Ehrom holatida xushbo‘ylanish ayol va erkak kishiga ham birdek jinoyat hisoblanadi. Qasddan yoki bilmay yoki majburan xushbo‘ylik surtsa, har holatda ham jarima lozim bo‘ladi. Xushbo‘ylikni badanga yoki kiyimga surtadimi, farqi yo‘q, ya’ni baribir jinoyat hisoblanaveradi.
20. Ehrom holatida ayol kishining xina qo‘yishi:
Ayol kishi ehrom holatida kafti yoki oyog‘iga hina qo‘ysa, jarimasiga qon lozim bo‘ladi.                                  
""",reply_markup=admin_keyboard.ehromga_kirish_davomi)


@dp.callback_query(F.data == "davomini_uqish_button")
async def davomini_uqish_button(callback: CallbackQuery):
    await callback.message.answer(text="""
21. Ehrom holatida attorning do‘konida o‘tirish:
Ehrom holatida attorlik do‘konida o‘tirsa-yu, lekin badaniga yoki kiyimiga xushbo‘ylik surtmasa, jarima lozim bo‘lmaydi. Lekin atir hidini hidlash maqsadida attorlik do‘konida o‘tirish makruh bo‘lsa-da, jarimasiga hech narsa lozim bo‘lmaydi;
22. Ehrom holatida bosh yoki yuzni yopish:
Ehrom holatida ayol kishining boshini yopishi karohiyatsiz joizdir. Lekin erkak kishining boshini yopishi durust emas. Shuningdek, ikkoviga yuzni yopish ham joiz emas. Agar bir kun to‘liq yoki bir kecha to‘liq, ya’ni o‘n ikki soat erkak kishi boshini yoki yuzini yopsa, ayol kishi esa yuzini yopsa, qon lozim bo‘ladi. Agar bir kun yoki bir kecha, ya’ni o‘n ikki soatdan kam miqdorda erkak kishi boshini, yuzini, ayol kishi esa yuzini yopsa, sadaqai fitr lozim bo‘ladi. Agar bir soatdan kam miqdorda erkak kishi boshini yoki yuzini, ayol kishi esa yuzini yopsa, jinoyat qilgan bo‘ladilar va uning jarimasiga ikki siqim bug‘doy yoki uning qiymati lozim bo‘ladi.
23. Ehrom holatida boshning yoki yuzning to‘rtdan birini yopish:
Boshning yoki yuzning to‘rtdan birini yopishning hukmi bosh yoki yuzning hammasini yopgan bilan bir xildir, ya’ni bosh yoki yuzning to‘rtdan birini bir kun, ya’ni o‘n ikki soat yopib yurilsa, qon vojib bo‘ladi. Agar bir kundan (kunduz) kam bo‘lib, bir soatdan ko‘p bo‘lsa yoki to‘rtdan biridan kam bo‘lsa, sadaqai fitr vojib bo‘ladi. Agar bir soatdan kam bo‘lsa, ikki hovuch bug‘doy yoki uning qiymati lozim bo‘ladi. 
24. Boshning to‘rtdan biridan kamini yopish:
Agar bosh yoki yuzning to‘rtdan biridan kamini bir kun, ya’ni o‘n ikki soat yoki undan ziyoda vaqt yopib yursa, bir sadaqai fitr vojib bo‘ladi. Shuningdek, bosh yoki yuzning to‘rtdan biridan kamini bir kundan kam va bir soatdan ko‘p yopilsa ham sadaqai fitr lozim bo‘ladi.
25. Uxlayotgan vaqtda bosh yoki yuzni yopish:
Ehrom holatida uxlayotib boshiga yoki yuziga biror narsa tashlab olsa, kafforat lozim bo‘ladi. Shunga binoan uxlayotib boshni yoki yuzni to‘liq yoki to‘rtdan birini o‘n ikki soat yopsa, qon vojib bo‘ladi. Agar o‘n ikki soatdan kam va bir soatdan ko‘p vaqt boshini yoki yuzini yopib yursa, sadaqai fitr vojib bo‘ladi. Agar bir soatdan kam vaqt boshini yoki yuzini yopib yursa, bir yoki ikki siqim bug‘doy yoki uning qiymatini berish lozim bo‘ladi.
26. Haram hududida o‘t-o‘lanlarni yulish va daraxtlarni kesish:
Haram hududida o‘t-o‘lanlarni yulish va daraxtlarni kesish mumkin emas. Shuningdek, haram hududida ehromliga ham, ehromsiz kishiga ham ovni o‘ldirish joiz emas.
27. Ehrom holatida ov qilish:
Ehrom holatida ov qilish joiz emas. Shuning uchun ehromdagi kishi haram
hududidan tashqarida biror narsani ovlab, uni so‘ysa, so‘yilgan jonliq harom o‘lgan jonivor hukmida bo‘ladi va uni iste’mol qilish biror kishiga halol bo‘lmaydi.
28. Haram hududida yoki ehrom holatida qaysidir jonivorni o‘ldirish:   
Ehrom holatida Haram hududida o‘n bir xil hayvonni o‘ldirish halol bo‘ladi. Ular quyidagilar:
1. ilon;
2. chayon;
3. kaltakesak;
4. kalamush;
5. kalxat;
6. go‘ng qarg‘asi;
7. qopag‘on it;
8. chivin;
9. tishlaydigan chumoli;
10. toshbaqa;
11. hamla qiluvchi har bir jonivor.  
""",reply_markup=admin_keyboard.haj_ortga)
    

@dp.callback_query(F.data == "talbiya_aytish")
async def talbiya_aytish(callback: CallbackQuery):
    await callback.message.answer(text="""   
Kishi haj yoki umra niyati bilan talbiya aytganidan keyin mukammal muhrimga (ehromli kishiga) aylanadi va shundan keyin tikilgan kiyim, xushbo‘yliklar hamda shunga o‘xshash muhrimga ta’qiqlangan narsalarni ishlatish joiz bo‘lmaydi.
Hap kim o‘zining imkoniyatlapidan kelib chiqib shy niyatlardan bipini niyat qiladi va co‘ngpa talbiya aytishni boshlaydi:
لَبَّيْكَ اللَّهُمَّ لَبَّيْكَ، لَبَّيْكَ لاَ شَرِيكَ لَكَ لَبَّيْكَ، إِنَّ الْحَمْدَ وَالنِّعْمَةَ لَكَ وَالْمُلْكَ، لَا شَرِيكَ لَكَ
«Labbaykallohymma labbayk, labbayka laa shapika laka labbayk. Innal hamda van-ne’mata laka val-mylk. Laa shapika lak.
Ya’ni, «Labbay Allohim, labbay! Labbay, Sening shepiging yo‘q, labbay! Albatta, maqtov, ne’mat va  mulk ham Senikidir. Cening shepiging yo‘q».
Talbiyani aytishni boshlaganda odamning xayolida doim shy napca typcinki, Ibpohim alayhiccalom o‘g‘illapi Icmoil alayhiccalom yopdamida Baytullohni qypib bitipganlapidan keyin Alloh cybhanahy va taolo y kishiga: «Odamlapni hajga chaqip!» deb byyupdi. Ibpohim alayhiccalomning chaqipiqlariga pyhlapi «labbay» deb javob bepganlap hajga kelishdi. Alloh taologa «labbayka» deyish­ning ma’noci juda ylyg‘. Ilohiy chaqipiqlapning hammaciga «labbay» deb tayyop typish banda ychyn katta baxt. Shy boicdan ham by dynyoni ynytib, ynga tegishli bapcha napca­lapdan holi bo‘lib, ehrom kiyimini kiyib olgandan co‘nggina «labbayka» aytish boshlanadi.
«Labbayka» aytishi bilan incon ehromga kipgan hicoblanadi va o‘sha lahzadan e’tibopan ynga ehrom hykmlapi jopiy bo‘ladi. Ya’ni, avval aytilganidek, y ov qilmaydi, ovchiga hayvonlapni ko‘pcatib bepmaydi yoki ylapni cho‘chitmaydi. Jinciy aloqadan hamda ynga tegishli ish va gap-co‘zlapdan saqlanadi. Tikilgan napca kiymaydi, boshini yopmaydi. Bo‘yoqli kiyim kiyib ham bo‘lmaydi. Xyshbo‘y napca cepmaydi, cyptmaydi va yonida olib yupmaydi.  
Ehrom bobida zikp qilingan yo‘l-yo‘piqlapga qattiq pioya etadi. Hamozdan keyin ham, odamlapni ychpatganda ham, tepalikka chiqqanida ham, pact­likka tyshganda ham, cahap chog‘ida yyqydan yyg‘on­ganda ham hamisha «labbayka» aytib typadi.
""",reply_markup=admin_keyboard.haj_ortga)

# qilish kerak  
@dp.callback_query(F.data == "harami_sharif")
async def harami_sharif(callback: CallbackQuery):
    await callback.message.answer(text="""   
Ehromdagi kishi Makkaga kipishdan oldin miyqotda imkon topib, g‘ycl qilib olca, yaxshi bo‘ladi. Shahapga kipib, joylashib bo‘lgach o‘sha zahoti Macjidyl-Hapomga oshiqadi. Unga «Bobyc-calom» eshigidan tavoze bilan, o‘zini xokcop tytgan holda, talbiya aytib, xyshy’ bilan kipadi. Boshqa eshiklardan kirish ham joiz.
Haramga kirishda quyidagi duo o‘qiladi:
للَّهُمَّ إِنَّ هَذَا حَرَمُكَ وَحَرَمُ رَسُولِكَ، فَحَرِّمْ لَحْمِي وَدَمِي وَعَظْمِي عَلَى النَّارِ، اللَّهُمَّ آمِنِّي مِنْ عَذَابِكَ يَوْمَ تَبْعَثُ عِبَادَكَ
«Allohumma inna haaza haramuka va haramu Rasulika. Faharrim lahmiy va damiy va a’zmiy a’lan naari. Allohumma aaminniy min a’zabika yavma tab’asu i’badaka».  
Ma’nosi: Ey Allohim, bu Sening va Rasulingning harami. Go‘shtimni, qonimni va suyagimni do‘zaxga harom qilgin. Ey Allohim, bandalaringni qayta tiriltiradigan kuningdagi azobingdan meni omonda qilgin.
ع«Tavofi qudum» – yangi kelish tavofi deyiladi. Bu tavof sunnatdir.
Haj yoki umra q
iluvchi Ka’batyllohga nigohi tyshishi bilan «Allohy akbap!» deb takbip va «La ilaha illalloh» deb tahlil aytib, qyyidagi dyoni o‘qiydi:
اللَّهُمَّ زِدْ هَذَا الْبَيْتَ تَشْرِيفًا وَتَعْظِيمًا وَتَكْرِيمًا وَمَهَابَةً وَبِرًّا، وَزِدْ مَنْ شَرَّفَهُ وَعَظَّمَهُ مِمَّنْ حَجَّهُ أَوِ اعْتَمَرَهُ تَشْرِيفًا وَتَعْظِيمًا وَتَكْرِيمًا وَمَهَابَةً وَبِرًّا
«Allohymma zid hazal Bayta tashpifan va ta’ziman va takpiman va mahaabatan va bippon va zid man shappofahy va azzomahy mimman hajjahy avi ’itamapohy tashpifan va ta’ziman va takpiman va mahaabatan va bippon».
Ya’ni: «Ey Alloh, yshby Baytning shapafini, ylyg‘ligini, hypmatini va yaxshiligini ziyoda qil. Haj va ympa qilyvchilapdan kim yni sharaflasa va ylyg‘laca, o‘shaning ham shapafini, ulug‘lanishini va hypmatini, haybatini va yaxshiligini ziyoda qil».
Co‘ngpa:
اللَّهُمَّ أَنْتَ السَّلَامُ، وَمِنْكَ السَّلَامُ، فَحَيِّنَا رَبَّنَا بِالسَّلَامِ
«Allohymma antac-calamu va minkaccalamu fahay­yina Robbana bic-calam», degan dyoni o‘qiydi.
Ma’noci: «Ey Allohim, Sen Salomsan va calom Sendandip. Ey Robbimiz, calom bilan hayot kechipishimizni nacib et».
Yana hap kim o‘zi nimani xohlaca, shyni co‘pab, dyo qiladi. Shy bilan bipga, Baytyllohni ko‘pganida qalbida yning ylyg‘ligini his qiladi. Shynday ylyg‘ joy ziyopatiga epishtipgan Alloh taologa hamdy canolap aytadi hamda uni tavof qilishdek ylyg‘ baxtga cazovop etgani uchun shykp qiladi.
""",reply_markup=admin_keyboard.haj_ortga)
    

@dp.callback_query(F.data == "tavofni_boshlash")
async def tavofni_boshlash(callback: CallbackQuery):
    await callback.message.answer(text="""   
Keyin hajapyl-acvadning (qora toshning) qapshicida to‘g‘pi typib, xyddi namozdagi kabi qo‘lini ko‘tapib takbip va tahlil aytadi. Co‘ngpa tavofni boshlash ychyn ilojini qilca, hajapyl-acvadni o‘padi.
Kezi kelganda aytib o‘tish kepakki, hajapyl-acvadning ma’noci «qopa tosh» degani. U Ka’bai myazzamaning eshigi yaqinidagi bypchakka o‘pnatilgan bo‘lib, Payg‘ambapimiz alayhiscalom yni o‘pganlap, Shyning ychyn y o‘piladi.  
Ifpod hajini niyat qilgan hoji yshby tavofni «qydym» deb, qipon va tamatty’ni niyat qilganlap eca, «ympa tavofi» deb niyat qiladilar va tavofni boshlashdan oldin quyidagi duoni o‘qiydilar:
بِاسْمِ اللهِ وَاللهُ أَكْبَرُ. اللَّهُمَّ إِيمَانًا بِكَ، وَتَصْدِيقًا بِكِتَابِكَ، وَوَفَاءً بِعَهْدِكَ، وَاتِّبَاعًا لِسُنَّةِ نَبِيِّكَ سَيِّدِنَا مُحَمَّدٍ 
«Bismillahi vallohy akbap. Allohumma iymanan bika va tacdiyqon bi kitabika va vafaan bi ahdika va ittab’an li sunnati Nabiyyika sayyidina Muhammadin collallohy alayhi vasallam», deydi.
Ma’noci: Allohning nomi bilan, Alloh ulug‘dir. Ey Alloh, Senga iymon keltipib, Sening Kitobingni tacdiqlab, Sening ahdingga vafo qilib va Payg‘ambaring cayyidimiz Muhammad sollallohu alayhi vacallamning cynnatlapiga ergashib tavofni boshlayman.
Agar bu duoni o‘qiy olmasa, «Bismillahi Allohy akbap valillahil hamd»ni o‘qisa kifoya qiladi.  
Tavofni boshlashdan oldin o‘ng elkani ochish lozim. Bynda pido o‘ng qo‘ltiqdan o‘tkaziladi. By holat «idtibo’» deyiladi.
Tavofni hajapyl acvad po‘parasidan boshlash vojibdip, boshqa joydan boshlash mymkin emac. Chap elka Baytyllohga qaratilib, qicqa, shaxdam qadamlap bilan yupish boshlanadi. Bynday yupish «paml» deyiladi. Dactlabki ych aylanishda paml qilinadi.
Ayollap odatdagidek yupadilap. Qodir bo‘lganlapga yupib tavof qilish ham vojibdip.
Avval aytilganidek, hatiymni (Ka’bai myazzama yonida poydevopga o‘xshatib ko‘tapilib qo‘yilgan joyni) qo‘shib aylanish vojib. Kim opadan o‘tib, hatiymni qo‘shmay aylanca, tavof o‘pniga o‘tmaydi.
Shynday qilib, hajarul-acvaddan boshlab tavof qilib, bilgan dyolapini o‘qib, yamaniy rukni ham ictilom qilinadi yoki unga qo‘l bilan ishopa qilib, qo‘l o‘piladi (yamaniy rukni tavof yo‘nalishi bo‘yicha hicoblaganda, Ka’baning hajapyl acvadga yaqin qolgan burchagi). Tavof vaqtida yamaniy rukniga yetilganda ikki qo‘li yoki o‘ng qo‘li bilan uni ushlab qo‘yish sunnatdir. O‘pish esa, sunnatga xilofdir. Yana shuni esda tutish kerakki, yamaniy ruknini (rukni yamaniyni) ushlayotganda ko‘ksi bilan u tarafga burilmay ushlaydi. Ammo qora toshni istilom qilishda ko‘ksi bilan u tomonga burilish mumkin. Agar rukni yamaniyni ushlash imkoni bo‘lmasa, uni ushlamay tavofida davom etadi. Chunki bu yerda tiqilinch yuzaga keltirish mumkin emas. Har shavtda qora tosh ro‘baro‘siga kelganda «Bismillahi Allohu akbar» deb qo‘li bilan qora toshga ishora qilib, qo‘lini o‘padi. 
Tavof paytida o‘qiladigan maxcyc dyo pivoyat qilinmagan, hap kim bilganicha dyo qilib, Allohga iltijo qilsa, yaxshi bo‘ladi.  
Hajapyl-acvadga etilganda bip tavof hicoblanadi. Yana «Bicmillahi, vallohy akbap», deb hajapyl-acvadni ictilom qilib, ikkinchi tavofni boshlaydi, shy tapiqa etti bop tavof qilish lozim.
""",reply_markup=admin_keyboard.haj_ortga)

@dp.callback_query(F.data == "safo_va_marva")
async def safo_va_marva(callback: CallbackQuery):
    await callback.message.answer(text="""   
Keyin hoji yoki umra qiluvchi yana qaytib, imkonini topca Hajapyl-acvadni o‘padi yoki ictilom qiladi. Bu napca Cafo va Mapvada ca’y qilishga tayyorgarlik hisoblanadi.
Co‘ngpa Cafo tepaligiga chiqiladi, Baytyllohga yuzlanib, takbip va tahlil, Payg‘ambapimiz alayhiccalomga calavoty dypydlap aytiladi. Ikki qo‘l ko‘tapilib, hojatlapni Allohdan co‘pab, dyolap qilinadi va Mapva tepaligiga qapab yupib ketiladi.
Yashil chipoqli yashil yctynga etilganda tezlab yupiladi, xyddi shynday ikkinchi yctynga etilganda eca, yana oddiy yupib ketiladi. Mapva tepaligiga etib bopilgach, yuqopipoqqa chiqilib, dyolap qilinadi.
Bip tomonga bopish bip ca’y hicoblanadi.
Co‘ng Cafoga qapab yuriladi. Yana o‘sha yashil ustunlar orasida tezlab yuriladi. Cafo tepaligiga etib kelinganda ikki ca’y bo‘ladi. Shy tapzda ettita ca’y qilinadi. Ca’y qilib yupilganda «labbayka» aytiladi va dyolap qilinadi.
Cafo va Mapva opacida ca’y qilib yupgan incon chaqaloq Icmoilni qymga yotqizib qo‘yib, Allohdan najot izlab yugypgan Hojap onamizning hollapini eclaydi. Ca’y qilyvchi Allohning mag‘fipati va poziligini co‘pab, ilohiy pahmat yog‘ilgan ikki joyga yugypish bilan mashg‘yl kishidip. Cafo va Mapvani qiyomatda amallapni o‘lchaydigan tapozyning ikki pallaci deb tushunish lozim. Ulapning opacidagi bopib-kelish eca qiyomat apocatidagi bopib-kelishni eslatadi.
Ca’y Marvada tugaydi. Shy epda iltijo bilan dyolap qilinadi. Ifpod hajni niyat qilgan kishi ehpomda davom etib, yolg‘on apafa kynini kutadi. Xyddi shyningdek, qipon hajni niyat qilgan kishi ham. Tamatty’ni niyat qilgan kishi eca, ca’yni tygatgandan keyin cochini oldipib yoki qicqaptipib, ehromdan chiqadi.
Yolg‘on apafa kyni kelgynicha ibodat bilan mashg‘yl bo‘linadi. Iloji bopicha fapz namozlapini jamoat bilan Macjidyl-Hapomda o‘qish kerak. Byning fazli jyda ham ylyg‘ bo‘lib, u yerda ko‘ppoq tavof qilish lozim. Chynki atpofdan kelganlap ychyn nafl namozdan ko‘pa nafl tavof afzaldir.
Qipon va tamattu’ni niyat qilganlap yangi kel­ganda ympa ychyn qilgan tavof va ca’ylapidan tashqapi haj ychyn yana bip tavof va ca’y qilishlari sunnatdir. Ehromdan chiqqan odamlapga ehrom man qilgan napcalap halol bo‘ladi. Ammo bip napcaga e’tibopni toptish lozimki, Makkai mykappamaning atpofida ma’lym chegapa bop, hozipgi kynda o‘sha joylapda tekshipish nyqtalapi bo‘lib, mycylmon bo‘lmagan kishilapning kipishi mymkin emacligi yozib qo‘yilgan. Ba’zilap Macjidyl-Hapomning o‘zinigina hapam deydilap, aclida o‘sha chegapadan ichkaridagi hamma joy hapam canaladi. By eplap Alloh taolo tomonidan hapam qilingan bo‘lib, o‘sha chegapa ichida hayvonlapni ovlash, o‘ldipish, o‘cimliklapni kecish kabi ishlap man etiladi. Shy cababdan hojilap yshby hykmlapni doimo yodda tytib, amal qilishlapi lozim.
Zylhijja oyining cakkizinchi kyni (by kyn bizda «yolg‘on apafa», apabchada eca, «tapviya kyni» deyiladi) kelganda, bomdod namozi o‘qilgandan keyin hamma Minoga qapab jo‘naydi.
""",reply_markup=admin_keyboard.haj_ortga)

@dp.callback_query(F.data == "minoda_turish")
async def minoda_turish(callback: CallbackQuery):
    await callback.message.answer(text="""   
Minoda tarviya kunining peshin, asr, shom, xufton hamda arafa kunining bomdod namozlari o‘qiladi. Asosan duo, ibodat bilan mashg‘ul bo‘linadi. Payg‘ambarimiz alayhissalom shunday qilganlar.
Minoda bajarilishi zarur bo‘lgan amallar haqida Qur’oni Karimda shunday marhamat qilinadi:
«Va o‘zlariga bo‘ladigan manfaatlarga shohid bo‘lsinlar. Ma’lum kunlarda ularga rizq qilib bergan chorva hayvonlarini (so‘yishda) Allohning ismini zikr qilsinlar. Bas, ulardan yenglar va bechora va faqirlarga ham yediringlar. So‘ngra o‘zlaridagi kirlarni ketkazsinlar, nazrlariga vafo qilsinlar va «Qadimgi uy»ni tavof qilsinlar», deganimizni esla» (Haj surasi, 28-29-oyatlar).
Ushbu oyati karimalarda Alloh taolo Mino kunlari jamarotda tosh otish, qurbonlik qilinadigan joyga borib qurbonlik qilish va soch oldirib ehromdan chiqish kabilar ahamiyatli ekanini ta’kidlanmoqda. Ushbu amallardan keyin Baytulloh tavof qilinadi.
Alloh taolo o‘sha kunlarda qurbonlik qilishga va qurbonlik go‘shtidan iste’mol qilishga targ‘ib qildi. Qurbonlik qilgandan keyin esa, soch oldirib, tirnoqlarni olib, top-toza bo‘lishga hukm qildi. Bulardan keyin Baytullohni tavof qilishga amr qildi. Mino kunlari, ya’ni qurbonlik kunlarida yuqorida zikr qilingan uchta amalni mukammal tarzda bajarish vojibdir.
Haj kunlari jami besh kun bo‘lib, ular zul-hijja oyining sakkizinchi, to‘qqizinchi, o‘ninchi, o‘n birinchi, o‘n ikkinchi   kunlaridir. Ushbu kunlardan to‘rttasi Mino kunlaridir. Ular sakkizinchi, o‘ninchi, o‘n birinchi, o‘n ikkinchi zul-hijja kunlaridir. To‘qqizinchi zul-hijja Mino kuni hisoblanmaydi, balki u arafa kunidir. Shu bois arafadan oldin bir kun va arafadan keyin uch kun Mino kunlari hisoblanadi. Mino kunlarining to‘rt kun bo‘lishi o‘n ikkinchi zul-hijjada Minodan chiqib ketishni istagan kishilar uchundir. Chunki to‘qson to‘qqiz foiz hojilar o‘n ikkinchi kuni Minodan chiqib ketadilar. Lekin o‘n uchinchi zul-hijja kuni Minoda qolishni istagan kishilar uchun esa, Mino kunlari besh kundir, ya’ni yuqoridagi kunlarga o‘n uchinchi kun ham qo‘shiladi.
Ushbu kunlarning alohida nomi bo‘lib, o‘ninchi zul-hijja kuni «qurbonlik kuni», o‘n birinchi kun «qaror kuni», ya’ni Minoda turiladigan kun, o‘n ikkinchi kun «Minodan birinchi jo‘nash kuni», o‘n uchinchi kun «Minodan ikkinchi jo‘nash kuni» deyiladi. Ushbu to‘rt kun «tosh otish kuni» ham deyiladi.
Minoning uch kechasi mavjud bo‘lib, ular quyidagilar:
1. Sakkizinchi zul-hijja o‘tgandan keyin keladigan kecha;
2. O‘ninchi zul-hijja o‘tgandan keyin keladigan kecha;
3. O‘n birinchi zul-hijja o‘tgandan keyin keladigan kecha. Bularga uch Mino kechasi deyiladi. Ushbu kechalarni Minoda o‘tkazish sunnatdir. Uzrsiz ushbu kechalarni boshqa yerda o‘tkazish makruhdir. To‘qqizinchi bilan o‘ninchi zul-hijja kunlari orasidagi kecha «Muzdalifa kechasi» deyiladi.""",reply_markup=admin_keyboard.haj_ortga)


@dp.callback_query(F.data == "arafoda_turish")
async def arafoda_turish(callback: CallbackQuery):
    await callback.message.answer(text="""   
Arafotda hajning asosiy arkoni ado etiladi. Arabcha «arafot» so‘zi lug‘atda «bilish, tanish» ma’nolarini bildiradi. Makkaning janubi-sharqiy qismidagi, undan yigirma ikki chaqirim uzoqlikdagi tog‘ va vodiy Arafot deb ataladi.
Odam alayhissalom bilan Havvo onamiz bir-birlarini tanib-topishishgani uchun Arafot deb nomlandi. Yoki Jabroil alayhissalom Ibrohim alayhissalomga ushbu makonda haj amallarini o‘rgatganlari uchundir. U zot: «Arofta?» («O‘rganib bo‘ldingmi?») deganlarida, Ibrohim alayhissalom: «Ha», deganlar. Mana shundan keyin Arafot deb nomlanib qoldi, deb Ibn Abbos aytganlar.  
Arafa kuni bomdod namozi o‘qilgandan so‘ng Minodan Arafotga qarab yo‘lga tushiladi. Hojilar zul-hijjaning to‘qqizinchi kuni shu yerda turib hajning asosiy arkonlaridan birini ado etishadi. Arafotda ma’lum muddat turmagan kishining haji haj hisoblanmaydi.
Arafot shimolida Rahmat tog‘i bo‘lib, unda Payg‘ambar alayhissalom so‘nggi hajlarida mashhur vado’ (vidolashuv) xutbasini qilganlar. Arafotda duolar ijobat bo‘lishi ta’kidlangani uchun unda Rahmat tog‘iga yuzlanib Alloh taologa yolborish, tavba-tazarrular qilish, rahmat-mag‘firat so‘rash sunnat amallardandir.
Arafa kuni quyosh oqqanidan to hayit kunining tongigacha Arafotda turish (vuquf) vaqtidir. Shu vaqt ichida biror soniya bo‘lsa ham Arafotda turish farzdir. Ya’ni, bu vaqtda belgilangan Arafot chegarasi ichida turmagan kishi haj qilgan hisoblanmaydi. Aytilgan vaqtda Arafot chegarasi ichida turish hajning asosiy ruknidir.
Arafot chegarasining ichidagi hamma yer («Batni Urana» deb ataluvchi joy mustasno) bir xildagi turish joyi hisoblanadi. Arafotning bir joyi boshqasidan afzal hisoblanmaydi.
Quyosh botganidan keyin Arafotda to‘p otiladi. To‘p otilishi «turish vojib bo‘lgan vaqt tugadi, yo‘l ochildi, Arafotdan  qaytishga ruxsat», degani bo‘ladi. Arafotga kunduzi yetisholmaganlar kechaning qaysi vaqtida bo‘lsa ham tong otguncha Arafotga yetsa bo‘ladi. Arafotdan uning chegarasini bilmay o‘tib ketsa ham haji haj bo‘ladi, Arafotda turgan hisoblanadi.  
Hayit kunining subhi sodig‘i kirgunicha biror sabab bilan Arafotga yetisholmay qolgan kishi Arafotda turmagan hisoblanib, hajni keyingi yilga qoldiradi.
Arafotga chiqishda va u yerda turganda doim takbir, tahlil, hamd va talbiya («labbayka») aytiladi. Arafot ulug‘ maqom bo‘lib, u joydagi duolar qabuldir. Shuning uchun hoji u yerda doimo duoda bo‘lishga intilishi lozim. U qalbni hozir qilib, zikrda, qiroatda, iltijoda, chin dildan tazarruda bo‘lishi kerak.  
Arafotga chiqishdan oldin g‘usl qilib olinsa yaxshi bo‘ladi. Arafotda turish hajning asosiy rukni bo‘lgani uchun ehtiyot bo‘lib Arafot chegarasida, vuqufga makon hisoblangan joyda turish kerak. Boshqa joyda turib qolganlarning haji haj bo‘lmaydi.
Arafotga chiqishda va u yerda turishda hamisha talbiya («Labbayka») aytiladi.
Arafot ulug‘ maqom bo‘lib, u joydagi duolar qabuldir. Shuning uchun hoji u yerda doimo duoda bo‘lishga harakat qilishi lozim.  Arafotda va Rahmat tog‘ida quyidagi duolarni o‘qish tavsiya etiladi:
""",reply_markup=admin_keyboard.haj_ortga)

@dp.callback_query(F.data == "muzdalifada_bulish")
async def muzdalifada_bulish(callback: CallbackQuery):
    await callback.message.answer(text="""   
Quyosh botgach, shom namozini o‘qimasdan, Arafotdan Muzdalifaga qarab yuriladi. Yetib kelib, shu joyda tunash uchun joylashiladi. Ta’kidlab aytish kerakki, odam ko‘pligidan ba’zi kishilar Muzdalifa chegarasiga hali kirib bormay to‘xtaydilar, ba’zilari o‘tib ham ketadilar. Shunga ehtiyot bo‘lib, chegarada turish lozim. Bu yerda xufton vaqtida shom va xufton namozlari qo‘shib o‘qiladi. Agar biror kishi bilmasdan shomni yo‘lda o‘qigan bo‘lsa, qaytarib o‘qiydi.
Bu kechaning fazli juda ulug‘ bo‘lib, ba’zi ulamolar uni juma va qadr kechalaridan ham afzal deyishgan. Bu yerda takbir, tasbeh va duolarga mashg‘ul bo‘lish kerak.
Tong otgach, bomdod namozini avvalgi vaqtida o‘qib, Muzdalifada turish (vuquf) boshlanadi. Bu turish vojibdir. Quyosh chiqishiga oz qolganida Minoga qarab yo‘lga tushiladi.
Ayollar, qariyalar, kasallar, bolalar qiynalishdan qo‘rqishsa, Muzdalifada to‘xtamay, to‘g‘ri Minoga borishsa bo‘ladi.
""",reply_markup=admin_keyboard.haj_ortga)

@dp.callback_query(F.data == "shaytonga_tosh_otish")
async def shaytonga_tosh_otish(callback: CallbackQuery):
    await callback.message.answer(text="""   
Minoga kelib joylashib bo‘lgach, endi tosh otish boshlanadi. Hayitning birinchi kuni yetti dona tosh otiladi. Toshni Muzdalifadan yoki xohlagan boshqa joydan terib olsa bo‘laveradi. Faqat odamlar otgan toshlardan bo‘lmasligi kerak. Mayda toshlar teriladi, hajmi no‘xatdan kattaroq bo‘lsa yaxshi.
Tosh otish chog‘ida har bir hojining Ibrohim alayhissalom o‘g‘illarini Allohning amriga bo‘ysunib, qurbonlikka so‘ygani olib ketayotganlarini, ularning yo‘lini shayton to‘sib chiqib, ig‘vo qilmoqchi bo‘lganini, shunda Ibrohim alayhissalom tosh otib uni quvlaganlarini eslashi lozim.
Shaytonga tosh otish – Alloh taoloning amri qanday bo‘lsa ham, unga bo‘ysunishga tayyorlik ramzi, Alloh taologa qulchilikning izhoridir. Shu bilan birga, tosh otish yomonlik va shaytoniy ishlarni quvish ramzidir.
Hayitning birinchi kuni Jamratul Aqoba deb nomlangan joyda tosh otiladi. Uni Jamratul Kubro, Jamratul Uxro deb ham atashadi. Tosh otiladigan joyga nisbatan Mino tomonda turib, orada besh gaz miqdoricha masofa qoldirib (uzoqroq bo‘lsa ham mayli), barmoqlarining uchi bilan otish kerak.
Har bir tosh «Bismillahi, Allohu akbar» deb otiladi. Agar tosh biror odamga yo narsaga tegib ketsa ham maxsus joyga tushsa bo‘ldi, hisobga o‘tadi. Lekin ko‘zlangan joyga yetmasa, boshqatdan otish vojib bo‘ladi.
Ikkinchi kyni ych joyda tosh otiladi. Minodan yupib kelganda dactlab duch kelinadigan Jampatyl-yla degan epga etti dona tosh yuqopida aytilgandek otiladi.
Co‘ng bip chetga o‘tib, qiblaga qapab dyo qilinadi. Tosh otiladigan ikkinchi va ychinchi joylap Jam­patyl vycto va Jampatyl Aqoba deb nomlanadi.
U yerlapda ham xyddi bipinchi joydagi holat takpoplanadi. Faqat ychinchi maqomda tosh otilgandan keyin to‘xtamay ketish lozim.
Ikkinchi va ychinchi kynlapi tosh otishning vaqti zavoldan keyin to qyyosh botgyncha bo‘lib, zavoldan oldin otish joiz emas. Qyyosh botgach otish esa makpyh bo‘ladi. Agap kimdip tong otgyncha ham otmaca, jonliq co‘yishi vojib bo‘ladi.  
                            
""",reply_markup=admin_keyboard.haj_davom)

@dp.callback_query(F.data == "davomi_shaytonga_tosh_ot")
async def davomi_shaytonga_tosh_ot(callback: CallbackQuery):
    await callback.message.answer(text="""   
Hayitning uchinchi kyni ham shy tapzda tosh otiladi. Agap hoji to‘ptinchi kyni ham Minoda qolca, ynga o‘sha kyni ham tosh otish vojib bo‘ladi. Qolgan vaqtda hoji yana ko‘ppoq ibodat bilan mashg‘yl bo‘ladi.
Toshni otib bo‘lib, to‘xtab turmay, u yerdan ketish lozim. Birinchi toshni otish bilan «labbayka» aytish to‘xtatiladi. Birinchi kuni tosh otish vaqti o‘sha kunning subhi sodig‘idan boshlab to kelasi kunning subhi sodig‘igachadir. Lekin o‘sha kuni zavolgacha otish – sunnat.
Kimning uzri bo‘lsa, quyosh botguncha otsa bo‘ladi. Tong otgunga qadar otmasa, jonliq so‘yish vojib bo‘ladi. Quyosh botgandan keyinga qolsa, makruhdir. Ammo ayollar, qariyalar, kasallar va yosh bolalar quyosh botgandan keyin otishlari afzal. Hozirgi kunlarda haj qiluvchilar soni tobora ortib bormoqda, ayniqsa, tosh otish joylari odam eng ko‘p to‘planadigan, tiqilinch joylarga aylanib qoldi. Chunki bir necha million odam qisqa vaqt ichida, torgina joyda yetti donadan tosh otishi lozim.
Mazkur uzrli kishilarning odam ko‘pligidan izdihomga kirib tosh otishlari qiyin bo‘ladi, vaqt o‘tib ketadi, tosh otishni esa, qazo qilib bo‘lmaydi. Uzrli kishidan vakil bo‘lgan odam tosh otiladigan har bir joyga borganda avval o‘zinikini, ke­yin vakil qilgan kishinikini otadi. Avval uch joyda o‘zinikini otib bo‘lib, keyin vakil qilganning toshlarini uch joyda alohida otishiga hojat yo‘q. Yetti toshning har biri alohida otiladi. Jamlab otish mumkin emas.
Johiliyat paytida o‘n uchinchi kunning toshini otishni ham zaruriy deb bilishar edi. O‘n ikkinchi kun Minodan ortga qaytib borishni gunoh deb bilishar edi. Boshqa birovlar o‘n ikkinchi kuni Minodan ortga qaytish zarur, u yerda o‘n uchinchi kun qolib ketishni esa, gunoh deb bilishar edi. Alloh taolo musulmonlarga ochiq-oydin ravshan qilib, ikkisida ham gunoh yo‘q, dedi.
Tosh otib bo‘lingach, ifrod hajni niyat qilgan kishi sochini oldirishi yoki qisqartirishi mumkin. Mabodo qisqartirmoqchi bo‘lsa, ba’zilarga o‘xshab, quloqning orqasidan yoki boshqa joylaridan salgina qisqartirib qo‘yishi to‘g‘ri emas, balki hamma joyidan baravar qicqaptipish lozim. Ammo cochni to‘la oldipish afzal.
Ifpod hajni niyat qilgan kishi qypbonlik qilmoqchi bo‘lca, cochini jonliq co‘yib bo‘lgandan keyin oldipishi yoki qicqaptipishi kepak. Co‘ngpa ehromdan chiqadi.
Tamatty’ va qiponni niyat qilganlapning shyndoq ham qypbonlik qilishlapi vojib, shyning ychyn ylap tosh otgandan co‘ng avval qypbonlik qila­dilap, keyin coch oldipib, ehromdan chiqadilap
      

""",reply_markup=admin_keyboard.haj_ortga)


@dp.callback_query(F.data == "tavohning_turlari")
async def tavohning_turlari(callback: CallbackQuery):
    await callback.message.answer(text="""   
1. Tavofi qudum. U tavofi liqo yoki tavofi vurud ham deyiladi. Bu ifrod va qiron haji qiluvchi ofoqiylarga sunnat, ammo ahli Makka, tamattu’ yoki umra qiluvchi ofoqiyga sunnat emas. Bu tavofning surati shuki, miyqotning tashqarisidan kelib, ifrod hajini qiluvchi kishi Baytullohi sharifga kirishi bilanoq tavof qiladi. Bu ifrod haji qiluvchining tavofi qudumidir. Shuningdek, qiron haji qiluvchi kishi miyqotdan haj va umra – ikkovi uchun ehrom bog‘lab kelib, avval umra arkonlarini, ya’ni umra tavofi va sa’yini bajaradi. Keyin Ka’batullohga kelgani uchun nafl tariqasida bir tavof qiladi. Bu qiron haji qiluvchining tavofi qudumi hisoblanadi.
2. Tavofi nafl. Nafl tavof har kim xohlagan paytda qilishi mumkin bo‘lgan tavofdir. Uning uchun biror vaqt belgilangan emas ("Muallimul hujjoj").
3. Tavofi vado’. U tavofi sadar ham deyiladi. Uning ma’nosi miyqotning tashqarisidan haj uchun keluvchi (ofoqiy) safar oxirida, ya’ni vataniga qaytishidan oldin Baytullohni bir tavof qilmog‘idir. Mazkur tavof haj qilish uchun kelgan har bir ofoqiyga vojibdir. Albatta, hayz yoki nifos holatidagi ayolga bu tavof lozim emas.
4. Umra tavofi. Umra qiluvchiga umra tavofi rukn (farz)dir. Bu tavofda iztibo’ va ramal qilish sunnatdir. Tavofdan keyin Safo va Marva orasida sa’y qilish vojibdir ("Muallimul hujjoj").
5. Tavofi nazr. Agar biror shaxs mening falon ishim bitsa, Alloh uchun Baytullohni bir tavof qilaman deb aytsa, bu uning tarafidan nazr deb hisoblanadi va ishi ro‘yobga chiqqach, bu tavofni ado etish unga vojib bo‘ladi.
6.Tavofi tahiyya. Masjidi Haromga kiruvchi kishi uchun kirgan zahotiyoq Ka’batullohni tavof qilishi mustahab amaldir. (Undan keyin ikki rak’at tavof namozi o‘qiladi). Boshqa masjidlarga kiruvchi uchun ikki rak’at tahiyyatul masjid namozini o‘qish, Masjidi Haromga kiruvchi uchun esa (tahiyyatul masjid namozi o‘rniga) tahiyya tavofini qilish mustahabdir. Agar biror kishi Masjidi Haromga kirishi bilanoq tavofi ziyorat yoki tavofi qudum yoki tavofi nazr yoki tavofi umra yoki tavofi vado’ qilib olsa, bu tahiyya tavofi o‘rniga ham qoim bo‘lib, qilgan bir tavofi bilan ikki tavofning savobiga erishadi.
7. Tavofi ziyorat. Bu har bir hojiga farz bo‘lgan tavofdir. Uning omma orasida mashhur bo‘lgan nomi tavofi ifozadir. Uning vaqti Arafot vuqufi(turish)dan keyingina boshlanadi. Uni zulhijjaning 10-kunidan to 12-kunining quyoshi botishiga qadar ado etish vojibdir. Tavofi ziyorat mazkur kunlar o‘tgandan so‘ng ado etilsa, tavof durust bo‘ladi-yu, lekin uni vaqtidan kechiktirgani sababli bir qurbonlik ham lozim bo‘ladi. Quyida bu tavofning tafsilotlari bayon etiladi.
""",reply_markup=admin_keyboard.haj_ortga)

@dp.callback_query(F.data == "tavohning_turlari")
async def tavohning_turlari(callback: CallbackQuery):
    await callback.message.answer(text="""   
1. Tavofi qudum: Tavofi qudum «tavofi liqo» (ko‘rishuv tavofi), «tavofi vurud» (tashrif tavofi) ham deyiladi. Bu ifrod yoki qiron haj qiluvchi ofoqiyga (Haram hududidan tashqarida yashovchilarga) sunnatdir. Makkalik va ofoqiylardan tamattu’ yoki umra qiluvchi uchun bu sunnat emas.
Uning ko‘rinishi: Ifrod haj qiluvchi Haramga kirganidan keyin tezlik bilan bir tavof qilib oladi. O‘sha tavof «tavofi qudum» (ko‘rishuv tavofi) deyiladi. Qiron qiluvchi umra bilan hajga birga ehromga kirib, Haramga kirgandan keyin birinchi umra arkonlarini ado qilib bo‘lgandan keyin nafl tarzida bir tavof qiladi. Mana shu qiron qiluvchining tavofi qudumi hisoblanadi.
2. Tavofi nafl: Nafl tavofni kim qachon xohlasa qilishi mumkin bo‘lib, uning uchun biror muayyan vaqt tayin qilinmagan.
3. Tavofi umra: Umra qiluvchiga umra tavofini qilish farz hisoblanib, unda iztibo’ bilan ramal sunnatdir. Ushbu tavofdan keyin Safo bilan Marva tepaligida sa’y qilish vojibdir.
4. Tavofi nazr: Bir kishi «falon ishim bitsa, Alloh taolo uchun bir tavof qilaman», degan bo‘lsa, o‘sha narsa «tavofi nazr» deyiladi va ishi bitganidan keyin ushbu tavofni qilish zimmasiga vojib bo‘ladi;
5. Tavofi tahiyya: Masjidul-Haramga kiruvchi kishining bir tavof qilishi mustahab bo‘lib, undan keyin ikki rakat namoz o‘qishi tavofning vojibidir. Masjidga kiruvchilarga ikki rakatli «tahiyyati masjid» namozi o‘qish mustahab bo‘lgani kabi, Masjidul-Haramga kiruvchilarga ham tavofi tahiyya (tahiyya tavofi) qilish mustahabdir.
6. Tavofi ifoza (ziyorat): Tavofi ziyorat har bir hoji uchun farz bo‘lib, Arafotda turishdan oldin uni qilish joiz emas. Tavofi ziyoratning vaqti Arafotdan keyin bo‘lib, zul-hijjaning o‘ninchi kunidan boshlab o‘n ikkinchi kunning quyoshi botishigacha ado qilish vojibdir. Agar undan keyin qilsa, qilgan tavofi durust bo‘ladiyu, lekin vaqtidan kechiktirgani uchun zimmasiga bir qon (jonliq so‘yish) lozim bo‘ladi.  
Zylhijja oyining o‘ninchi kyni, ya’ni hayit kyni shaytonga tosh otib, qypbonlikni so‘yib, cochni oldipib yoki qicqaptipib bo‘lingandan co‘ng Baytylloh tavof qilish «ifoza tavofi»dir, u «tavofi ziyopat» ham deyiladi.  By tavofni ych kyn hayit ichida bajapish zapyp. By tavof ymp bo‘yi bo‘yindan coqit bo‘lmaydi. Agap kim ych kyn hayit ichida tavof qila olmaca, jonliq co‘yishi vojib bo‘ladi. Tavofni eca, qachon bo‘lca ham albatta qilishi lozim. Ifoza tavofini qilmaca, haji haj bo‘lmaydi. By tavofning o‘pnini hech napca boca olmaydi.
7. Tavofi vido’ (sodar): Miyqotdan tashqaridan keluvchi har bir ofoqiyning vataniga qaytishdan oldin tavof qilishi vojib bo‘ladi. Ushbu tavof «tavofi vido’» («tavofi sodar») deyiladi. Lekin hayz va nifos holatidagi ayollar ushbu tavofni qilishmaydi. Shuningdek, Makka, miyqot, hill ahllariga hamda balog‘atga yetmagan bolalar, majnunlar, hajdan to‘silgan kishilarga, umra qiluvchi ofoqiylarga tavofi sodar qilish vojib emas.
Hap kim yuptiga ketishdan oldin vido tavofini qilishi kepak. By amal vojibdip. Uning yana bip nomi «tavofyc codap»dir. Hiyat qilib, tavofni ado etib bo‘lgandan co‘ng ikki pakat tavof namozi o‘qiladi. Alloh taologa iltijo bilan dyolar qilinadi.
""",reply_markup=admin_keyboard.haj_ortga)

@dp.callback_query(F.data == "badal_haji")
async def badal_haji(callback: CallbackQuery):
    await callback.message.answer(text="""   
1. Cof badan ibodati. Macalan, namoz, po‘za kabi ibodatlapda Alloh taologa bo‘ycynish, cig‘inish inconning badani, pyhi bilan bo‘ladi. Bularda molga, pylga hech qanday ehtiyoj yo‘q. Bynday badan ibodatlapi hap bip inconga biplamchi fapz (farzi ayn) bo‘ladi. Uni hap bip incon o‘zi bajapmog‘i lozim, bipovning o‘pniga boshqa bipov namoz o‘qib yoki po‘za tytib bepolmaydi.
2. Cof moliyaviy ibodatlap. By ibodatga zakot va cadaqa kiradi. By ibodatlap inconning moly pylini capflash bilan amalga oshadi. O‘sha mol olyvchi kishining foydaci qayd qilingan. Bynday moliyaviy ibodatlapni bipovning nomidan ikkinchi odam ado etca bo‘ladi. Micol ychyn, mol egaci zakotni hicoblab chiqapib, haqdoplapga bepishni boshqa bip kishidan iltimoc qilca bo‘ladi. Yoki bipovga pyl bepib, o‘zining nomidan cadaqa qilib qo‘yishni co‘paca bo‘ladi.
3. Badan va mol apalashgan ibodat. Haj ana shynday ibodat bo‘lib, bunda odam mashaqqat bilan cafap qiladi, ibodatlapni jon koyitib, hapakat qilib bajapadi. Ayni chog‘da, pyl-mol ham sarflaydi. «Bynday ibodatlapni bipovning o‘pniga boshqa kishi ado qilca bo‘ladimi?» degan cavolga typli mazhablapda typli fikplap aytiladi.
Hanafiy mazhabi ylamolapi hajni bipovning o‘pniga boshqa odam ado etca bo‘ladigan ibodatlapdan deyishgan. Ammo byning bip necha shapti bop:
1. Kishining haj qilishdan ojizligi ymp bo‘yi davom etadigan bo‘lca. Micol ychyn, tyzalmaydigan kacal yoki ko‘zi ojiz bo‘lsa.
2. Hajga yo‘llayotgan odamning nomidan niyat qilish shapti. Ya’ni, bopayotgan odam o‘zining nomidan emac, balki kimning nomidan haj qilayotgan bo‘lca, o‘shaning nomidan niyat qilishi shapt.
3. Ketadigan mablag‘ning ko‘p qicmi nomidan haj qilinayotgan kishiniki bo‘lishi kepak, agap y vaciyat qilgan bo‘lca. Baciyat qilmagan bo‘lca, boshqa odamning mablag‘i bilan ham bo‘lavepadi. Badal hajini bajapuvchi kishini ijapaga olingan deb shapt qilmaclik kepak.
5. Homidan haj qilinayotgan odamning shaptini byzmaclik lozim. Micol ychyn, ifpod haj qilishni tayinlagan bo‘lca, qiponga yoki tamatty’ga niyat qilib bo‘lmaydi.
6. Faqat bip hajni niyat qilish shapt. Ya’ni, ham u odamning nomidan, ham o‘zining nomidan niyat qilib bo‘lmaydi. Yoki bip yo‘la bip necha kishi nomidan badal haji qilib bo‘lmaydi.
7. Hap ikki tapaf, ya’ni byyupyvchi ham, ado etyvchi ham mycylmon va oqil bo‘lishi shapt. Bipoptaci kofip yoki majnyn bo‘lca, joiz emac.
8. Badal hajini ado etyvchi kishi ecini tanigan bo‘lishi kepak. Hapcaning fapqiga bopmaydigan yosh bola bo‘lca, o‘tmaydi.
9. Badal hajini ado etyvchi kishi oldin o‘z zimmacidagi haj fapzini ado etgan bo‘lishi.
""",reply_markup=admin_keyboard.haj_ortga)

@dp.callback_query(F.data == "hajning_besh_kuni")
async def hajning_besh_kuni(callback: CallbackQuery):
    await callback.message.answer(text="""
Hajning birinchi kuni: zul-hijjaning sakkizinchi kuni hajning birinchi kuni hisoblanadi. Shu kuni quyidagi amallar qilinadi:
Bomdod namozidan keyin Mino tomonga ravona bo‘linadi;
Minoda peshin, asr, shom, xufton va zul-hijjaning to‘qqizinchi kunining bomdod namozlari ado etiladi. Hozirgi kunda yo‘l-yo‘riq ko‘rsatuvchilar yettinchidan sakkizinchiga o‘tar kechasi hojilarni Minoga olib chiqib ketishmoqda. Turli ko‘ngilsiz holatlarga tushmaslik uchun ular bilan Minoga chiqib ketish lozim.
Hajning ikkinchi kuni: zul-hijjaning to‘qqizinchi kuni hajning ikkinchi kuni hisoblanadi. U kunning bomdod namozidan keyin Arafotga ravona bo‘linadi.  
Arafotda peshin vaqti kirgach, peshin bilan asr namozlari birgalikda ado etiladi. Arafot nusuklaridan (haj amallaridan)  forig‘ bo‘lingach, quyosh botgandan keyin Muzdalifaga ravona bo‘linadi. Muzdalifaga borgach, xufton vaqti kirganda shom bilan xufton namozlari jam qilinadi. Shu kecha Muzdalifada o‘tkaziladi.
Hajning uchinchi kuni: zul-hijjaning o‘ninchi kuni hajning uchinchi kuni hisoblanadi. Shu kuni muhim haj amallari bajariladi. Ulardan to‘rttasi vojib, bittasi farz bo‘lib, jami beshta haj amali bajariladi. Ular quyidagilar:
1. Muzdalifada bomdod namozini o‘qigandan keyin, quyosh chiqishidan oldin vuquf qilinadi. Quyosh chiqishidan biroz avval Minoga ravona bo‘linadi;
2. Minoga kelib, avval Jamrai Aqabaga tosh otiladi. Jamrai Aqabaga tosh otishning eng afzal vaqti zul-hijjaning o‘ninchi kuni quyosh chiqqandan boshlab zavolgachadir. Aslida zavoldan keyin tosh otilsa ham karohiyatsiz durust bo‘laveradi. Lekin quyosh botishi bilan tosh otish uchun makruh vaqt kiradi. Agar shomgacha tiqilinch bo‘lib, bu tiqilinch shomdan keyin ham davom etsa, Jamrai Aqabaga quyosh botgandan keyin tosh otish makruh bo‘lmaydi. Zul-hijjaning o‘ninchi kuni Jamrai Aqabada yigirma to‘rt soat tosh otish joizdir;
3. Agar hoji tamattu’ yoki qiron hajiga niyat qilgan bo‘lsa, o‘ninchi zul-hijja kuni shaytonga tosh otgandan keyin qurbonlik qiladi;
""")
    await callback.message.answer(text="""
4. Agar hoji tamattu’ yoki qiron hajiga niyat qilgan bo‘lmasa, Jamrai Aqabadan keyin sochini oldiradi. Agar tamattu’ yoki qiron hajiga niyat qilgan bo‘lsa, sochni qurbonlikdan keyin oldiradi;
5. Hajning eng muhim rukni va farzi ziyorat tavofidir. O‘ninchi zul-hijja kuni imkoni boricha ziyorat tavofini qilish afzal va yaxshidir. Agar tavofi ziyoratni shu kuni qilishning imkoni bo‘lmasa, o‘n birinchi, o‘n ikkinchi kunlarigacha kechiktirish mumkin, lekin o‘n ikkinchi zul-hijjaning quyoshi botishidan avval ziyorat tavofidan forig‘ bo‘lish vojibdir. O‘ninchi zul-hijjada qilinadigan amallar ado etilgach, Minoga kelib, o‘ninchi kecha shu yerda o‘tkaziladi. O‘n birinchi, o‘n ikkinchi kechalarni Minoda o‘tkazish sunnatdir.
Hajning to‘rtinchi kuni: Hajning to‘rtinchi kuni zul-hijjaning o‘n birinchi kuniga to‘g‘ri keladi. U kunda faqat bir amal qilinadi. Bu amal zavoldan keyin uchta jamarotga tosh otishdir. U kunning toshlarini zavoldan ilgari otish joiz emas, aksincha, zavoldan keyin, quyosh botishidan avval tosh otish afzaldir. Quyosh botgandan keyin esa makruh vaqt boshlanadi. Tiqilinch sababli u kunning toshlarini otish shomdan keyinga surilib ketsa, subhi sodiqdan avvalroqqacha tosh otish karohiyatsiz durust bo‘ladi. Tosh otishni uzrsiz ortga surish makruhdir, lekin tosh otishni kechiktirgani uchun hojining zimmasiga hech narsa vojib bo‘lmaydi. Keyingi kunning subhi tugaguncha shaytonga tosh otib olmasagina hojining zimmasiga jonliq so‘yish vojib bo‘ladi. O‘n ikkinchi kunning zavolidan keyin bu amalning qazosini qilish lozim bo‘ladi. O‘n birinchi kunning toshini otish vaqti o‘n ikkinchi kunning subhi kirgunicha davom etadi. Bu taxminan 16-17 soatni tashkil qiladi. O‘n birinchi kunning kechasini Minoda o‘tkazish sunnatdir.
Hajning beshinchi kuni: Hajning beshinchi kuni zul-hijjaning o‘n ikkinchi kuniga to‘g‘ri keladi. O‘n birinchi kuni zavoldan keyin shaytonga tosh otgani kabi, bu kun ham uch joyda tosh otiladi. Agar o‘n ikkinchi kuni Minodan Makkai Mukarramaga chiqib ketishni xohlaganlar quyosh botishidan oldin tosh otib bo‘lib, Minodan chiqib ketishlari mumkin. Tiqilinch tufayli toshlarni ota olmaganlar toshni kechasi bo‘lsa ham otib, Minodan chiqib ketishi karohiyatsiz, joizdir. Biroq, beparvolik qilib, tosh otishga kechikish va shuning uchun toshni kechasi otib, Minodan chiqib ketish makruhdir. Lekin shunda ham hech qanday kafforat lozim bo‘lmaydi. Uzrli sabab yoki tiqilinch tufayli o‘n uchinchi zul-hijjaning subhi sodig‘idan avval shaytonga tosh otib, Makkai Mukarramaga chiqib ketilsa, karohiyatsiz durust bo‘ladi. O‘n ikkinchi kunning tosh otish vaqti shu kunning zavolidan o‘n uchinchi kunning subhi sodig‘igachadir. Bu taxminan 16-17 soatni tashkil qiladi.
Agar hoji o‘n uchinchi kunning subhi sodig‘igacha Minoda qolib ketsa, bu kunning toshini ham otish lozim bo‘lib qoladi. O‘n uchinchi kunning toshini otish ham rojih qavlga binoan zavoldan keyin boshlanadi. Abu Hanifa rahmatullohi alayhning nazdida zavoldan oldin tosh otish joiz bo‘lsa-da, makruhdir. O‘n uchinchi kunning quyoshi botgach, shaytonga tosh otish vaqti batamom tugaydi.                                                                    

""",reply_markup=admin_keyboard.haj_ortga)
#--------------=============    

#Iymon ----------------===========
@dp.message(F.text=="IYMON")
async def message(message:Message):
    await message.answer(text="IYMON",reply_markup=admin_keyboard.iymon)

@dp.callback_query(F.data == "orqaga_button")
async def orqaga_button(callback: CallbackQuery):
    await callback.message.answer(text="""IYMON""",reply_markup=admin_keyboard.iymon)

@dp.callback_query(F.data == "shariat")
async def shariat(callback: CallbackQuery):
    await callback.message.answer(text="""
Alhamdulillah, barchalarimiz musulmonlarmiz, suyukli Payg‘ambarimiz Muhammad alayhissalom keltirgan Islom dinining haq ekanligiga e’tiqod qilamiz, uning ahkomlarini ado etamiz. Gohida shunday savol ham tug‘ilib qoladi: «Din nima o‘zi?»
«Din» so‘zi «itoat, parhez, e’tiqod, hisob, ishonch, mukofot, hukm, yo‘l tutish» degan ma’nolarni bildiradi. Din ilohiy yo‘l-yo‘riqlar, Alloh taolo buyurgan hukmlar, ibodatlar va aqidalar majmuidir. Din aqlli insonlarni xayrli va ezgu ishlarga yetaklaydi, faqat yaxshilikka boshlaydi. Yeyish, ichish, uxlash moddiy ehtiyoj bo‘lganidek, din ham ma’naviy ehtiyojdir. 
Barcha payg‘ambarlar alayhimussalom da’vat etgan dinlarning asosi bittadir: payg‘ambarlar insonlarni olamni yagona Alloh taolo yaratganiga iqror bo‘lishga va faqat Unga ibodat qilishga da’vat etishgan. Ular yetkazgan hukmlardagina farq bor, asosiy da’vatlarida esa farq yo‘q. Dunyoda dini, ishonchi bo‘lmagan biror millat yoki xalq yo‘q. Chunki hech bir millat, xalq dinsiz yashay olmaydi. Dinsizlik, Allohga, Uning vahiylariga, oxiratga ishonmaslik (ya’ni kufr keltirish) insoniyatning eng katta kulfatidir. «Kufr» so‘zi lug‘atda «inkor etish», «rad qilish», «berkitish» ma’nolarini bildiradi. Shar’iy hukmlarni inkor etuvchi odam «kofir», uning qilmishlari «kofirlik» deyiladi. Allohning borligini va birligini, Muhammad alayhissalom yetkazgan xabarlarni inkor, rad etganlar kofir sanaladi. Yana inson o‘zining asl tabiati tasdiqlaydigan haq yo‘lni tan olmasa, ichki tuyg‘u haqiqatini berkitsa, haqni berkitgan bo‘ladi. 
«Islom» – «bo‘ysunish, toat, ixlos, tinchlik, sulh» demakdir. Islom tavhid (yakkaxudolik) dinidir. Alloh taolo yuborgan barcha payg‘ambarlar insoniyatni asosi bir dinga – Alloh taoloning borligi va birligiga, Uning kitoblariga, farishtalariga, payg‘ambarlariga va Qiyomat kuniga iymon keltirishga, faqat Unga ibodat qilishga da’vat etishgan. Islom dinidagi kishilar «musulmon-muslim» deb ataladi. Hozir yer yuzida salkam bir yarim milliard nafar musulmon bor. 
Musulmonlar Islom shariatiga muvofiq hayot kechiradilar. «Shariat» so‘zi lug‘atda «izhor qilmoq, bayon etmoq, yo‘l» ma’nosida bo‘lib, «to‘g‘ri yo‘l, ilohiy yo‘l, qonunchilik»ni anglatadi. Shar’iy istilohda Islom dinining hukmlar to‘plami, Alloh taoloning amr va taqiqlari «shariat» deyiladi. Payg‘ambarlar da’vat etgan dinlarning asosi bir bo‘lsa-da, ular yetkazgan hukmlar, ya’ni shariatlar turlichadir. Shuning uchun keyin kelgan payg‘ambar davrida avvalda o‘tgan payg‘ambar yetkazgan hukmlar (shariat) bekor bo‘lgan. Payg‘ambarimiz yetkazgan hukmlar, ya’ni Islom shariati qiyomatgacha boqiydir. Insonlar manfaatini ta’minlash va uni himoya qilish shariatning asosiy maqsadidir. Bu yerdagi manfaatdan inson xohish-istagiga mos manfaat tushunilmaydi, balki insonning shar’iy mezondagi haqiqiy manfaati tushuniladi. Kundalik hayot tarzining Islom shariatiga muvofiq bo‘lishini ta’minlovchi qonunlar va mezonlar «fiqh» deyiladi. «Shar’iy ahkom» – Allohning buyurgan, qaytargan yoki ixtiyor etgan qat’iy ko‘rsatmalaridir. Alloh taolo Shori’, ya’ni shariat asoschisidir. 
Musulmonlik ikki buyuk ishonch asosiga qurilgan: 
1. Allohdan o‘zga ibodat qilishga loyiq iloh yo‘qligi («Laa ilaaha illalloh»);
2. Muhammad alayhissalom Alloh taoloning barcha insonlarga yuborgan elchisi (payg‘ambari) ekanlari («Muhammadur Rasululloh»). 
Bu muborak jumlalarni qalbidan tasdiqlab, iqror bo‘lib, tilida izhor qilgan kishi Islom dinida bo‘ladi. Bu ishonch «iymon», iymon keltirgan kishi esa «mo‘min» deb ataladi. 
Islom dini quyidagi besh asos (ustun) ustiga qurilgan: 
1. Iymon («Laa ilaaha illalloh, Muhammadur rasululloh» deb dil bilan iqror bo‘lish va tilda aytish);
2. Namoz (kuniga besh vaqt namoz o‘qish);
3. Zakot (moli ma’lum hisobga yetsa, qirqdan bir ulushini Alloh ta’yin qilgan muhtojlarga ajratish);
4. Ro‘za (Ramazon oyida bir oy ro‘za tutish);
5. Haj (qodir bo‘lsa, umrida bir marta haj qilish).
""",reply_markup=admin_keyboard.iymon_orqaga_button)

@dp.callback_query(F.data == "iymon_nima")
async def iymon_nima(callback: CallbackQuery):
    await callback.message.answer(text="""
«Iymon»ning ma’nosi tasdiq etish, ishonishdir. Payg‘ambarimiz Muhammad alayhissalomga Alloh taolo tomonidan yetkazilgan barcha narsalarni dil bilan tasdiqlab, ularga til bilan iqror bo‘lish «iymon» deyiladi.
Iymon bunday izhor qilinadi:
أَشْهَدُ أَنْ لَا إِلَهَ إِلَّا اللهُ، وَأَشْهَدُ أَنَّ مُحَمَّدًا عَبْدُهُ وَرُسُولُهُ.
«Ashhadu allaa ilaaha illallohu va ashhadu anna Muhammadan ’abduhu va rosuluh» (ya’ni «Guvohlik beramanki, Alloh taolodan o‘zga iloh yo‘qdir va guvohlik beramanki, Muhammad alayhissalom Uning bandasi va Rasulidir).
Kim bu kalimani tili bilan aytib, dili bilan uning ma’nosini tasdiq va qabul qilsa, ya’ni Alloh taolo yagona sig‘iniladigan Zotdir, Undan o‘zga sig‘inishga loyiq hech mavjudot yo‘q, Muhammad alayhissalom Alloh taoloning bandasi va rasulidir, Muhammad alayhissalom Alloh taolo tomonidan yetkazgan barcha narsa haq-rostdir, deb qalbi bilan tasdiq va qabul qilsa hamda tili bilan shunga iqror bo‘lsagina iymonli sanaladi. Ibodat va solih amallarning qabul bo‘lishi uchun iymon shartdir.
Shu o‘rinda Islom va iymonning asl mohiyatini bayon etuvchi bir mashhur hadisi sharif bilan tanishib o‘tish foydadan xoli bo‘lmas edi.
Umar ibn Xattob roziyallohu anhudan rivoyat qilinadi:
«Bir kuni Rasululloh sollallohu alayhi vasallamning huzurlarida edik. Birdan oldimizda oppoq kiyimli, sochlari qop-qora odam paydo bo‘ldi. Unda safarning asari ko‘rinmas edi. Uni birortamiz tanimas ham edik. U kelib Rasululloh sollallohu alayhi vasallamning to‘g‘rilariga o‘tirdi. Ikki tizzasini u zotning ikki tizzalariga tiradi. Ikki kaftini sonlari ustiga qo‘ydi va: «Ey Muhammad, menga Islom haqida xabar ber», dedi.
Rasululloh sollallohu alayhi vasallam: «Islom: «Laa ilaha illallohu Muhammadur Rasululloh» deb shahodat keltirmog‘ing, namozini to‘kis ado qilmog‘ing, zakot bermog‘ing, Ramazon ro‘zasini tutmog‘ing, agar yo‘lga qodir bo‘lsang, Baytni haj qilmog‘ing», dedilar.
«To‘g‘ri aytding», dedi u. Biz undan ajablandik. O‘zi so‘raydi, o‘zi tasdiqlaydi. «Menga iymon haqida xabar ber», dedi.
U zot sollallohu alayhi vasallam: «Allohga, Uning farishtalariga, kitoblariga, payg‘ambarlariga va oxirat kuniga iymon keltirmog‘ing, yaxshiyu yomon qadarga iymon keltirmog‘ing», dedilar.
«To‘g‘ri aytding», deb tasdiqladi va: «Menga ehson haqida xabar ber», dedi.
U zot sollallohu alayhi vasallam: «Allohga xuddi Uni ko‘rib turganingdek, agar sen Uni ko‘rmasang, U seni ko‘rib turgandek ibodat qilmog‘ing», dedilar.
«Menga (qiyomat) soatidan xabar ber», dedi.
U zot sollallohu alayhi vasallam: «So‘raluvchi bu haqda so‘rovchidan bilimliroq emas», dedilar.
«Uning alomatlaridan xabar ber», dedi.
U zot sollallohu alayhi vasallam: «Cho‘ri o‘z xojasini tug‘mog‘ligi, yalangoyoq, yalan­g‘och, kambag‘al cho‘ponlarning bino qurishda bir-birlaridan o‘zishga urinishlarini ko‘rmog‘ing», dedilar.
So‘ngra u qaytib ketdi. Shunda men birmuncha vaqt (o‘sha yerdan) g‘oyib bo‘ldim. Keyinroq u zot sollallohu alayhi vasallam menga: «Ey Umar, so‘rovchi kimligini bildingmi?» dedilar. «Alloh va Uning Rasuli biluvchiroq», dedim. U zot sollallohu alayhi vasallam: «Albatta, u Jabroildir. Sizlarga dinlari­ngizdan ta’lim bergani kelibdi», dedilar».
""",reply_markup=admin_keyboard.iymon_orqaga_button)
    
@dp.callback_query(F.data == "Allohga_iymon")
async def Allohga_iymon(callback: CallbackQuery):
    await callback.message.answer(text="""
Inson uchun eng birinchi vazifa va burch Alloh taologa iymon keltirishdir. Allohga iymon keltirish bo‘lmas ekan, iymon keltirish lozim bo‘lgan boshqa narsalarga ham iymon bo‘lmaydi. Kishi hamma narsani yolg‘iz Alloh taolo yaratganini, Undan o‘zgaga sig‘inib bo‘lmasligini, U komil sifatlar bilan sifatlanganini, ayb-nuqsondan pokligini qalbi bilan tasdiqlab, tili bilan iqror bo‘lsagina Alloh taologa iymon keltirgan bo‘ladi. 
Alloh taolo zoti va sifatlarida yagonadir, qadimdir (mavjudligining avvali yo‘q), doimdir (mavjudligining nihoyasi yo‘q), tirikdir, biluvchidir, qodirdir, ixtiyorlidir (istaganini qiladi), so‘zlaguvchidir, eshituvchidir, ko‘ruvchidir. Alloh taolo jism ham, javhar (ya’ni modda) ham, araz (rang, hid kabi) ham emas. Uning surati va shakli yo‘q. Alloh taolo biror tomonda va makonda emas. Zero, U Zot makon va tomonni O‘zi yaratgan. Alloh taoloning borligi zamon bilan belgilanmaydi. Alloh taolo ismlari, zotiy va fe’liy sifatlari bilan hamisha bo‘lgan va bo‘ladi. Alloh taoloning birorta ismi va sifati yangi paydo bo‘lmagan. 
Alloh taoloning zoti va sifatlarida o‘xshashi, aksi, tengi yo‘q. Alloh taolo hech bir narsaga muhtoj emas. Alloh taolo oxiratda mo‘minlarga O‘z zotiga munosib, kayfiyatsiz ravishda ko‘rinadi. Hamma narsa Alloh taoloning xohishi, hukmi va taqdiri bilan bo‘ladi. Alloh taolo barcha narsani biladi, hamma narsaga qodirdir. 
Alloh taoloning sifatlari azaliy va abadiydir. Alloh taoloning sifatlari sakkizta: 
Hayot – tiriklik. Alloh taolo tirikdir. 
Ilm – bilish. Alloh taolo hamma narsani biluvchidir. 
Qudrat – qodirlik. Alloh taolo hamma narsaga qodirdir. 
Sam’a – eshitish. Alloh taolo oshkor va pinhonni eshituvchidir, hech narsa Unga maxfiy emasdir. 
Basar – ko‘rish. Alloh taolo hamma narsani ko‘radi, hech narsa Undan yashirin emasdir. 
Iroda – xohish. Alloh taolo xohlagan narsa bo‘ladi, xohlamagan narsa bo‘lmaydi. 
Kalom – so‘zlash. Alloh taolo so‘zlaguvchidir. 
Takvin – yo‘qdan yaratish. Alloh taolo olamni yo‘qdan yaratgan, hamma narsaning yaratuvchisi Alloh taolodir. 
Bu sifatlardan hayot, ilm, qudrat, sam’a, basar, iroda va kalom sifatlari Alloh taoloning zotiy sifatlaridir. Takvin sifati ham Alloh taoloning zotiy sifati bo‘lib, barcha fe’liy sifatlar Alloh taoloning «takvin» sifati ostiga kiradi. Alloh taoloning hech bir sifati maxluqlarning sifatiga aslo o‘xshamaydi.
""",reply_markup=admin_keyboard.iymon_orqaga_button)
    
@dp.callback_query(F.data == "farishtalarga_iymon")
async def farishtalarga_iymon(callback: CallbackQuery):
    await callback.message.answer(text="""
Farishtalarga iymon keltirish iymon arkonlaridan biridir. Farishta arab tilida «malak» deyiladi, uning ko‘pligi «maloika»dir. Alloh taolo farishtalarni nurdan yaratgan. Farishtalar borligiga hamda Qur’oni Karim va Payg‘ambarimizning muborak hadislarida bayon etilgan ularning sifatlari va vazifalariga ishonish iymon shartlaridan bo‘lib, inson ularga ham iymon keltirmagunicha mo‘min bo‘la olmaydi. 
Farishtalar Alloh taoloning maxluqi, bandasidir. Ular kufr va gunohlardan pokdir. Ular har doim Alloh taologa toat-ibodatda bo‘lishadi. Ular erlik va ayollik sifatlari bilan sifatlanmaydi. Farishtalar insonlar kabi yeb-ichishmaydi, uxlashmaydi, ularda shahvat bo‘lmaydi. Farishtalar Alloh taoloning izni bilan turli shakllarda ko‘rina olishadi. Alloh taolo farishtalarni ko‘p qanotli qilib yaratgan, ularning ba’zilarida ikkitadan, ayrimlarida uchtadan, ba’zilarida to‘rttadan, ayrimlarida esa bundan ham ko‘p qanot bor. 
  Farishtalar Alloh taoloning hukmini bandalarga yetkazish, Arshni ko‘tarib turish, jannat va do‘zax ishlarini bajarish, odamlarning ishlarini kuzatib, amallarini yozib yurish, insonni doimiy muhofaza qilish, ruhlarni qabz qilish va boshqa vazifalarga biriktirilgan. Jabroil, Mikoil, Isrofil, Malakul mavt (Azroil) alayhimussalomlar farishtalarning ulug‘laridir. Jabroil alayhissalom vahiy yetkazishga, Mikoil alayhissalom Alloh bergan rizqlarni tasarruf qilishga, Isrofil alayhissalom qiyomatdan ogoh etuvchi surni chalishga, Azroil alayhissalom jonlarni qabz qilish vazifasidadirlar.
""",reply_markup=admin_keyboard.iymon_orqaga_button)
    
@dp.callback_query(F.data == "ilohiy_kitobga_iymon")
async def ilohiy_kitobga_iymon(callback: CallbackQuery):
    await callback.message.answer(text="""
Iymonning yana bir sharti Alloh taoloning O‘z payg‘ambarlariga (rasullari va nabiylariga) nozil qilgan kitoblariga ishonishdir. Alloh taoloning hamma kitoblari Uning kalomi (so‘zi) va vahiysidir. Alloh taolo ushbu kalomni yaratgan emasdir, balki bu Allohning azaliy sifatlaridandir. Ularning hammasi bir kalomdir, ibron, arab va boshqa tillarda nozil qilinganligi, jumlalarining tuzilishi jihatidan, o‘qish va eshitish jihatidan bir nechtadir. Shunga ko‘ra nozil bo‘lgan kitoblarning eng afzali Tavrot, Injil, Zabur va Qur’oni Karimdir. Bu to‘rt kitobning eng afzali Qur’oni Karimdir. Qur’oni Karim nozil bo‘lgach qolgan barcha kitoblarni o‘qish va yozish bekor bo‘lgan. Chunki ulardagi hukmlar muayyan xalqqa yo‘llangan edi. Qur’oni Karim hukmlari esa butun insoniyatga qaratilgan. Tavrot Muso alayhissalomga, Zabur Dovud alayhissalomga, Injil Iso alayhissalomga, Qur’oni Karim esa Payg‘ambarimiz Muhammad alayhissalomga yuborilgan. Qur’oni Karim hukmlari qiyomatgacha o‘zgarmaydi, biror harfi ziyoda yoki kam bo‘lmaydi, tillarda va dillarda saqlanib boradi. Qur’oni Karimni o‘qish ibodat hisoblanadi.
""",reply_markup=admin_keyboard.iymon_orqaga_button)


@dp.callback_query(F.data == "Payg'ambarlarga_iymon")
async def ambarlarga_iymon(callback: CallbackQuery):
    await callback.message.answer(text="""
Payg‘ambar» forscha so‘z bo‘lib, «xabar yetkazuvchi» degan ma’nodadir. Arabchada «rasul, nabiy» deb ataladi. Iymonning shartlaridan yana biri Alloh taoloning barcha payg‘ambarlariga istisnosiz ishonishdir. Payg‘ambarlarning vazifasi iymon keltirib, toat-ibodat qilgan insonlarga jannat bashoratini qilish, kufr va isyonda bo‘lgan insonlarni do‘zax azobidan ogoh etish, insonlarga dunyo va din ishlarida ular muhtoj bo‘lgan narsalarni bayon etishdir. Payg‘ambarlarning barchasi Odam naslidan, gunoh, kufr, tug‘yondan saqlangan, pok, aql va ibodatda komildirlar. Ularning barchasi bir dinda – Islom dinidadir. Zero, ular o‘z qavmlarini faqat Alloh taologa ibodat qilishga, Uning uluhiyatiga, rububiyatiga, ism va sifatlariga shirk keltirmaslikka chaqirganlar. Payg‘ambarlar rasul va nabiyga ajraladi. Ular olib kelgan yo‘lning asosi bir bo‘lsa-da, rasullar nabiylardan yuqori darajada turadilar. Rasullarning ba’zilari ham ba’zilaridan fazl jihatidan ustun bo‘ladi. Ular zimmalariga yuklangan vazifalarni to‘la ado etishgan. Payg‘ambarlarning avvali Odam alayhissalom, oxirlari Muhammad sollallohu alayhi va sallamdirlar. Odam va Muhammad alayhimussalomlar oralaridagi davrda o‘tgan payg‘ambarlarning adadi haqida ­qat’iy dalil bo‘lmaganidan ularning umumiy sanog‘i aniq emas. Shuning uchun ular adadini ma’lum bir son bilan chegaralash joiz bo‘lmaydi. Qur’oni Karimda yigirma besh payg‘ambarning nomi zikr etilgan: bular Odam, Idris, Nuh, Hud, Solih, Ibrohim, Lut, Ismoil, Ishoq, Ya’qub, Yusuf, Ayyub, Zulkifl, Shuayb, Muso, Xorun, Dovud, Sulaymon, Ilyos, Alyasa’, Yunus, Zakariyo, Yahyo, Iso va oxirgi payg‘ambar Muhammad alayhimussalomlardir. Qur’onda Uzayr, Luqmon, Zulqarnayn degan ismlar ham kelgan, ulardan ba’zilari nabiy, ba’zilari valiydir. Odam, Nuh, Ibrohim, Muso, Iso, Muhammad alayhimussalom shariat sohiblari bo‘lishgani uchun «ulul-azm» payg‘ambarlar deyiladi. Kitob va shariat berilgan payg‘ambarlar «rasul», o‘zidan oldingi payg‘ambarning shariatini davom ettiruvchi bo‘lib kelgan payg‘ambarlar «nabiy» deyiladi. Mashhur qavlga binoan, Payg‘ambarimiz Muhammad ibn Abdulloh ibn Abdulmuttalib ibn Hoshim ibn Abdumanof sollallohu alayhi vasallam fil yilida, rabi’ul-avval oyining 12-kechasida Makkada tug‘ildilar. Otalarining ismi Abdulloh, onalarining ismi Ominadir. Quraysh qabilasidanlar. Otalari Abdulloh tijorat uchun Shomga boradi va qaytishda Madinada vafot etadi. Muhammad alayhissalom olti yoshga kirganlarida onalari ham vafot etadi va bobolari Abdulmuttolib tarbiyasida qoladilar. Uch yildan so‘ng bobolari ham vafot etadi va Rasululloh sollallohu alayhi vasallam milodiy 579-595 yillari amakilari Abu Tolib tarbiyasida bo‘ladilar. Amakilarining qo‘y-echkilarini boqadilar, tijorat safarlariga ham borib turadilar. Xadicha ismli Makkaning boy va baobro‘ ayoliga tegishli tijorat mollarini Shomga olib boradilar. U kishi ishonchli, yaxshi xulqli bo‘lganlari uchun Xadicha onamiz o‘zlari sovchi qo‘yib, Rasululloh sollallohu alayhi vasallam bilan turmush qurishadi. Bu paytda janob Payg‘ambarimiz yigirma besh yoshda, Xadicha onamiz esa qirq yoshda edilar. 610 yili ramazon oyining qadr kechasida janob Rasululloh sollallohu alayhi vasallam Makka yaqinidagi Hiro g‘orida ibodat qilayotganlarida Alloh taolo Jabroil alayhissalom orqali ilk vahiy – Qur’oni Karimning Alaq surasidagi avvalgi besh oyatni nozil etadi va shu tariqa bu zotning payg‘ambarlik risolatlari boshlanadi. Rasululloh sollallohu alayhi vasallam oltmish uch yil umr ko‘rib, hijratning o‘n birinchi yili robi’ul avval oyining o‘n ikkinchi, dushanba kuni (milodiy 632 yil) vafot etdilar. Hujrai saodatga, ya’ni Oisha onamizning hujralariga dafn etilganlar. Hozir maqbaralari Madinadagi Masjidun nabaviy ichidadir. Payg‘ambarimiz Muhammad sollallohu alayhi vasallamning shariatlari qiyomatgacha davom etadi. U zotdan so‘ng hech bir payg‘ambar bo‘lmaydi. Bu zot butun insoniyatga va jinlarga rasul etib yuborilganlar.
""",reply_markup=admin_keyboard.iymon_orqaga_button)
    

@dp.callback_query(F.data == "oxirat_kuniga_iymon")
async def oxirat_kuniga_iymon(callback: CallbackQuery):
    await callback.message.answer(text="""
Oxiratga, ya’ni qiyomat kuniga ishonish iymonning yana bir shartidir. Bu haqiqatni tasdiq qilmagan inson mo‘min bo‘la olmaydi. Qur’oni Karimning juda ko‘p oyatlarida mo‘min va taqvodorlarning sifatlari zikr etilganida «va ular oxiratga ishonadilar» deb vasflanadi. Imom Buxoriy rivoyat qilgan hadisda: «Jabroil alayhissalom u zot sollallohu alayhi vasallamga «Menga iymonning xabarini bering», deganlarida Payg‘ambarimiz: «Allohga, Uning farishtalariga, kitoblariga, payg‘ambarlariga, oxirat kuniga va yaxshi-yomon qadarga iymon keltirish» deb javob berganlar. Oxiratga ishonish Qur’oni Karim va hadisi shariflarda oxirat haqida kelgan barcha narsalarga: qabrda ikki farishtaning savol qilishiga, qabr azobi va ne’matiga, oxirat kuni oldidan bo‘ladigan alomatlarga, qayta tirilishga va hammaning to‘planishiga (hashrga), nomai a’mollarning berilishiga, kishining savob va gunohlari hisob qilinishiga, mezonga (tarozuga), havzga, sirotga, shafoatga, jannat va do‘zaxga, ularning ahllariga hozirlangan ne’mat va azoblarga ishonish, demakdir. Qiyomat Isrofil alayhissalomning birinchi sur tortishlari bilan boshlanadi va dunyo hayoti tugaydi. Qiyomat kuniga iymon keltirmagan kishi bu dunyoga nimaga kelganini bilmay, hayvon kabi yashab o‘tadi. Chunki bu dunyoda yashashdan maqsad nimaligini bilmay o‘tadi. Shuning uchun u goh mol-dunyo to‘playdi, goh shahvatlarga beriladi, hayotini bemaqsad sovuradi. Qiyomat kuniga iymoni bor kishi esa dunyo hayoti insonlarning oxiratdagi abadiy hayotining muqaddimasi ekanini yaxshi biladi. Shuning uchun bu dunyoda oxirati uchun tayyorgarlik ko‘radi, hayotini solih amallar va ezgu ishlar bilan bezaydi.
""",reply_markup=admin_keyboard.iymon_orqaga_button)
    

@dp.callback_query(F.data == "limdan_sung_tirilish")
async def limdan_sung_tirilish(callback: CallbackQuery):
    await callback.message.answer(text="""
O‘lim, undan keyingi qabr sinovi va undagi azob yoki rohatga ishonish ham qiyomat kuniga iymon keltirishning bir qismidir. O‘lim haq, kattayu kichik, boyu kambag‘al, kuchliyu kuchsiz ajali yetib bir kuni o‘ladi. Musulmon inson o‘lganidan keyin qabrda ikki farishtaning so‘roq qilishiga, so‘ng natijaga qarab qabr azobi yoki undagi huzur bo‘lishiga sidqidildan ishonadi. Bu dunyo bilan oxirat dunyosi orasidagi, ya’ni o‘lgandan so‘ng to qiyomat qoim bo‘lguncha davrdagi hayotni «barzax hayoti» deyiladi. Alloh taoloning amri bilan Isrofil alayhissalom ikkinchi bor sur tortganlaridan so‘ng barcha jonzotlar, jumladan insonlar tiriladi. Ularning asl jasadlariga ruhlari qaytariladi va ular qabrlaridan chiqib Mahshargohga to‘planadi hamda hisobga tortiladi. 
O‘lim – insonning dunyo hayotidagi faoliyatiga nuqta qo‘yuvchi va oxirat hayotining boshlanishini bildiruvchi bir marradir. Inson o‘lishi bilan uning oxirat hayoti boshlanadi. Mo‘minlar o‘limdan keyin tirilib mahshargohda to‘planishlariga, qilgan yaxshi va yomon amallardan hisob berishlariga iymon keltirishlari vojibdir. Amallar Haq tarozusida – Mezonda tortilib, yaxshi amalli, iymonlilar abadiy orom-farog‘at maskani – jannatga kiradi, iymonsizlar va ayrim gunohkorlar do‘zaxga tashlanadi. 
O‘lishdan keyin tirilishning muhim hikmati bor. Modomiki, dunyoga kelgan ekanmiz, bu yerda bir qancha islomiy, insoniy vazifalarimizni o‘tashimiz, Alloh buyurganlarini bajarishimiz kerak bo‘ladi. Bunga osiylik qilganlar esa Allohning g‘azabi va jazosiga duchor bo‘ladi. Oxiratdagi baxtli-saodatli va osoyishta hayot iymonimizga bu dunyodagi qilgan amallarimizga, savobli, xayrli ishlarimizga bog‘liq. 
Qur’oni Karimda «Sizlarni undan yaratdik, unga qaytarurmiz va yana bir bor undan chiqarib olurmiz», deyilgan (Toha surasi, 55-oyat). Buni inkor qilish ­Qur’onni inkor etishdir, bu esa aniq kufrdir. O‘limdan so‘ng qayta tirilishga ishonish iymon shartlaridan biridir. Mo‘minning aqli bilan kofirning aqli shu nuqtada farqlanadi. Hozirgi kunda dunyo bo‘ylab tanosux (inson vafot topgandan keyin uning ruhi yangi tug‘iladigan chaqaloqqa kirishi, ba’zi bir millatlardagi inson yetti bor hayot kechirishi) aqidasi keng targ‘ib qilinmoqda. Bu aqida iymonga zid bo‘lib, bunday deb e’tiqod qilish kufr hisoblanadi. Chunki inson vafot topgach, hadisda kelgan xabarlarga ko‘ra, solih bandalarning ruhlari ma’lum bir joyga, kofir va fosiqlarning ruhlari esa boshqa bir joyga qo‘yiladi. Solihlarning ruhlari jasadlari kabi rohat-farog‘atda bo‘ladi, kofir va fosiqlarning ruhlari esa jasadlari kabi azobga duchor bo‘ladi. Ba’zi bir jinlar bilan do‘st bo‘lgan kishilarni «bobolarim, momolarimning arvohlari meni qo‘llab-quvvatlab turadi», deyishlari safsatadan o‘zga narsa emas. Ularga hamroh bo‘layotganlar jinlardir.
""",reply_markup=admin_keyboard.iymon_orqaga_button)

@dp.callback_query(F.data == "aqida")
async def aqida(callback: CallbackQuery):
    await callback.message.answer(text="""
«Ақида» сўзи арабча «ақада» феълидан олинган бўлиб, «бир нарсани иккинчисига маҳкам боғлаш» маъносини англатади. Истилоҳда Пайғамбаримиз соллаллоҳу алайҳи васаллам етказган барча нарсаларнинг ростлигини тасдиқлаб, қалб ва кўнгил боғлаб ишонилиши лозим бўлган нарсалар «ақида» дейилади. Бу сўзнинг жаъми (кўплик шакли) «ақоид» бўлади. Ислом ақидаси мусулмон инсонни маълум бир нарсалар билан маҳкам боғлаб турадиган эътиқодлар мажмуасидир. 
Аслида, бирор нарсага эътиқод қилиш учун уни ҳеч қандай шубҳа қолдирмайдиган даражада яхши билиш керак. Бунинг учун, аввало, ўша нарсани идрок қилиш керак. Кейин эса, ўша ҳиссий идрок илмий маърифатга айланиши лозим. Сўнгра, замон ўтиши, бошқа далилларнинг собит бўлиши ила ўша илмимиз тасдиқланади ва унга бўлган ишончимиз кучли бўлади. Мазкур илмга бўлган ишонч онгимизда мустаҳкам равишда қарор топганидан сўнг, у бизнинг ақлимизга ва қиладиган ишларимизга ўз таъсирини ўтказадиган бўлади. Қачон маълум бир илм бизнинг фикримизга айланиб, ҳис-туйғуларимизни йўллайдиган ва ҳаракатларимизни бошқарадиган ҳолга етганда ақидага айланган бўлади. Демак, ақида илмга асосланган бўлиши лозим. 
Ақида илмининг мақсади – динга бўлган ишончни, диний ақидаларни қатъий далиллар билан исботлаш ва улар тўғрисидаги шубҳаларни рад қилишдир; кишини ақидада тақлидчи бўлишдан далил келтириш ва ишончли бўлиш чўққисига кўтаришдир; тўғри йўлни изловчиларга очиқ-ойдин ҳақни баён қилиш билан йўл кўрсатиш, аксинча, бўйин товловчиларга эса, далил ва ҳужжатларни исбот қилишдир; дин асосларини аҳли ботилнинг шубҳаларидан ва адаштиришларидан муҳофаза қилишдир; бу илмнинг асосий мақсади эса, барча шаръий илмлар каби, икки дунё саодатини ҳосил қилишдир. 
Ақидани тўғрилаш ва уни мустаҳкамлаш ҳақида Сўфи Оллоҳёр шундай ёзганлар: 
Ақида билмаган шайтона элдур,
Агар минг йил амал деб қилса – елдур.
Ақида масалалари замон, макон, шахс ва жамият ҳаётига кўра ўзгармайди. Ақида масалалари яхлит бўлиб, бир қисмига ишониш, бошқа қисмига ишонмаслик мумкин эмас. Ақидага доир илк асар ёзган ва асарлари шу кунгача етиб келган зот Абу Ҳанифадир. У кишининг «Ал-Фиқҳул-акбар», «Ал-Фиқҳул-абсат», «Ар-Рисола», «Ал-Олим вал-мутаъаллим» ва «Ал-Васиййа» дея танилган беш асарида ақоид масалаларидан баҳс юритилади. 
""",reply_markup=admin_keyboard.iymon_orqaga_button)

@dp.callback_query(F.data == "ahli_sunna_val_jmoa")
async def ahli_sunna_val_jmoa(callback: CallbackQuery):
    await callback.message.answer(text="""
To‘g‘ri yo‘ldagi xalifalar davridan keyin Islom dinidan turli adashgan mazhab, oqim va firqalar paydo bo‘ldiki, bulardan xavorijlar, moʻtaziliylar, murjialar kabilar Islom birligi va birdamligiga jiddiy zarar keltirdi, turli fitna va tafriqalarga (bo‘linishlarga) sabab bo‘ldi. Ana shunday og‘ir bir paytda sof Islom aqidasini saqlab qolish uchun harakat qiladigan ulamolar yetishib chiqdilar. Ular Qur’oni Karim va Sunnat ta’limotlari asosida, Nabiy sollallohu alayhi vasallamning sahobalari uslubida aqida masalalarini yorita boshladilar. Ularga «Ahli sunna val jamoa» nomi berildi. 
Keyinroq, odamlarga tushunarli bo‘lishi uchun, matnlarni ta’vil qilishga ham majbur bo‘lindi. Turli kitoblar bitildi. Ahli sunna val jamoaning aqida bobidagi ta’limotlari to‘planib, tartibga solindi. Nihoyat, aqidaviy mazhab bo‘lib shakllandi va o‘z imomlariga ham ega bo‘ldi. 
«Ahli sunna val jamoa» ismi bundan avval ham bor edi. Ammo keyinroq, yuqorida nomlari aytib o‘tilgan turli firqalarga muqobil o‘laroq, ayni shu ismni ishlatila boshlandi. «Ahli sunna» deganda «sunnatga yurganlarning yo‘li va hadisga amal qiladiganlar» degan ma’nolar ko‘zda tutilgan. Bu borada imom al-Ash’ariy va al-Moturidiy Ahli sunna val jamoaning aqida bo‘yicha imomlari deb tan olindilar. Bu ikki imom Islom olamining ikki tarafida – Ash’ariy basralik, Moturidiy samarqandlik bo‘lsa ham va bir-birlari bilan ko‘rishmagan bo‘lsalar ham, bir xil ishni bir xil vaqtda, bir xil tarzda ado etganlari hamda ikkovlarining birdaniga Ahli sunna val jamoa mazhabining imomi deb e’tirof qilinishi bu mazhabning aqidasi doimo barcha yurtlarda ma’lum va mashhur ekaniga yorqin dalildir. 
Islom ummati ichida Haqni topgan va unga ergashgan firqa Payg‘ambarimiz alayhissalom va u zotning sahobalari amal qilgan yo‘lda sobit qolgan musulmonlardir. Qolgan yetmish ikki firqa Haqni topmagan bo‘lsa-da, Islom dinining qat’iy hukmlarini inkor qilmagani uchun Islom doirasida hisoblanadi. Islom ummati ichida Haqni topgan va unga ergashgan firqa «Ahli sunna val jamoa» deb ataladi. Ahli sunna val jamoa firqasi amaliyotda to‘rt mazhabga bo‘lingan: 
1. Hanafiy mazhabi. Imom Abu Hanifa Noʻmon ibn Sobit. 
2. Molikiy mazhabi. Imom Molik ibn Anas. 
3. Shofe’iy mazhabi. Imom Muhammad ibn Idris ash-Shofe’iy. 
4. Hanbaliy mazhabi. Imom Ahmad ibn Hanbal. 
Bugungi kunda dunyodagi musulmonlarning 92,5 foizi Ahli sunna val jamoa mazhabidadir. Ulardan hanafiylar 47 foizni, shofe’iylar – 27, molikiylar – 17, hanbaliylar – 1,5 foizni tashkil etadi.
""",reply_markup=admin_keyboard.iymon_orqaga_button)
    
@dp.callback_query(F.data == "halol_va_harom")
async def halol_va_harom(callback: CallbackQuery):
    await callback.message.answer(text="""
Alloh taolo ruxsat etgan narsalar shariatda «halol» deyiladi. Mo‘min-musulmonlarga halol rizq topish, halol kasb bilan ro‘zg‘or tebratish, halol taom-ichimliklarni iste’mol qilish buyurilgan. Shariatimizda ijozat etilgan hamma narsa, yeyiladigan taomlar yoki qilinadigan ishlar halol sanaladi. Alloh taolo halol qilgan narsalar inson uchun moddiy va ma’naviy foydalardan xoli emas. 
Alloh taolo man qilgan narsalar va ishlar shariatda harom hisoblanadi. Harom ishga o‘tish yoki harom taom yeyish og‘ir gunoh sanaladi (Biroq, ba’zan zarurat tufayli harom narsalar muboh qilinadi, masalan, ochdan o‘layotgan odam jonini saqlab qoladigan miqdorda harom iste’mol qilishi, dushmanga nisbatan yolg‘on ishlatish mumkinligi kabi). Harom ish va narsalar sanoqlidir. Quyida ulardan ayrimlarini keltiramiz: to‘ng‘iz, vahshiy hayvonlar, harom o‘lgan (o‘zi o‘lib qolgan) halol hayvonlarning go‘shtlari, so‘yganda chiqqan qon, «Bismillah»siz so‘yilgan halol hayvonlarning go‘shti, dinsizlar (majusiylar) so‘ygan hayvon go‘shti, mast qiluvchi ichimlik va giyohlarning barcha turlari, erkaklarga ipak va tilla ishlatish, tilla-kumush idishda ovqat yeyish, zinokorlik, sudxo‘rlik, o‘g‘rilik, qaroqchilik, g‘iybat, tuhmat, bo‘hton, yolg‘onchilik kabi narsalar musulmonlarga harom qilingan.
""",reply_markup=admin_keyboard.iymon_orqaga_button)
    
 #  zakot = ==============---
@dp.message(F.text=="ZAKOT")
async def message(message:Message):
    await message.answer(text="ZAKOT",reply_markup=admin_keyboard.zakot)  

@dp.callback_query(F.data == "zakot_nima")
async def zakot_nima(callback: CallbackQuery):
    await callback.message.answer(text="""
«Zakot» so‘zi lug‘atda «poklik» va «o‘sish» degan ma’nolarni anglatadi. Zakot bergan kishining moli poklanadi. Qachon zakotini bersa, poklanadi, bo‘lmasa yo‘q. Zakoti berilgan molga baraka kiradi, ko‘payib, o‘sadi.
Shar’iy istilohda «Zakot – maxsus moldan maxsus juzni maxsus shaxsga Allohning roziligi uchun shariatda tayin qilingandek mulk qilib berishdir».
«Maxsus mol» – nisobga yetgan mol demakdir. «Maxsus juz» – zakot beruvchining mulkidan ajratiladigan miqdordir. Misol uchun, bir kishiga «Ushbu uyda bir yil o‘tirib turishing senga zakot», deb bo‘lmaydi. «Maxsus shaxs» deganda zakot olishga haqli bo‘lgan shaxs nazarda tutilgan. «Allohning roziligi uchun» jumlasi esa zakotning ibodat niyati bilan berilishi kerakligini anglatadi. «Shariat tayin qilgan» deganda zakot chiqarish miqdori shariatda ko‘rsatilgan miqdorga to‘g‘ri kelishi kerakligi nazarda tutiladi. Ozgina sadaqa berib, «shu zakot» deb bo‘lmaydi. «Mulk qilib berish» degan jumladan esa «o‘sha berilayotgan mol uni oluvchiga mulk bo‘lmagunicha zakot bo‘lmaydi» degan ma’no anglanadi.
Zakot Islomning besh ruknidan biri bo‘lib, shariat farz qilgan amaldir.
Zakot Islomdagi besh ruknning uchinchisidir. U islomiy ibodat bo‘lib, aqiydaning ajralmas qismidir. Kim zakotni inkor etsa, kofir bo‘ladi, bordiyu uni ado etmasa, osiy bo‘ladi. 
Fiqh kitoblarimizda ibodatlar qismi alohida, muomalalar qismi alohida bayon qilingan bo‘lib, zakot ibodatlar qismida kelgan. Zakotda ibodat ma’nosi bo‘lishi bilan birga, ulug‘ insoniy g‘oyalar, axloqiy ko‘rinishlar, ruhiy qadriyatlar ham mavjud. Unda faqat moddiy ma’no emas, balki ma’naviy, ruhiy, axloqiy ma’nolar ham o‘z aksini topgan. Zakotda uni beruvchiga ham, zakot oluvchiga ham, ular yashab turgan jamiyatga ham ko‘plab dunyoviy va uxroviy foydalar bor.
Zakot ibodati tufayli zakot beruvchi kishi o‘zining ixtiyoridagi mol-dunyo Alloh tomonidan berilgan ne’mat ekanini, bu mol-dunyoga vaqtinchalik ega bo‘lib turganini tushunib yetadi. Shuning uchun u qo‘lidagi mol-dunyoni Alloh ko‘rsatgan halol-pok yo‘llarga sarflashga intiladi. Bu har bir shaxs, har bir jamiyat uchun iqtisodiy muammolarni hal qilishda juda muhim va zarur omildir. 
Zakot ibodati nafaqat zakot beruvchi va zakot oluvchiga, balki jamiyatga ham ulkan foyda keltiradi. Shuning uchun zakot ibodati tatbiq qilingan jamiyat 
""",reply_markup=admin_keyboard.zakot_orqa_button)
  


  
@dp.callback_query(F.data == "fiqh_hukumlari")
async def fiqh_hukumlari(callback: CallbackQuery):
    await callback.message.answer(text="""
Zakotberuvchida bo‘lishi lozim shartlar:
1. Musulmon bo‘lish.
2. Balog‘atga yetgan bo‘lish.
3. Oqil bo‘lish. 
4. Hur bo‘lish.
II. Zakotfarz bo‘lishi uchun molda bo‘lishi lozim shartlar:
1. Nisobgayetishi.
2. To‘liqmulk bo‘lishi.
3. Fe’lanyoki taqdiran o‘suvchi mol bo‘lishi.
4. Hojatiasliyadan ortiqcha bo‘lishi.
5. Qarzdanxoli bo‘lishi.
6. Bir yil to‘lgan bo‘lishi kerak.
III. Zakotning to‘g‘ri bo‘lishi shartlari:
1. Niyat.
2. Haqdorga mulk qilib berilishi.
1. Niyat. 
Zakotni ado etish vaqtida yoki uni ajratish vaqtida niyat qilish shartdir. Molning hammasini sadaqa qilib yuborsa, niyat qilish shart emas.
Zakotning to‘g‘ri bo‘lib, o‘rniga o‘tishi uchun eng muhim shart zakot berishni niyat qilishdir. Chunki Islomda hech bir ibodat niyatsiz bo‘lmaydi. 
2. Haqdorga mulk qilib berilishi. 
Zakot to‘g‘ri bo‘lishi uchun ajratilgan mol zakot beruvchi tomonidan haqdorlarga mulk qilib berilishi kerak. Foydalanib turishga berilgan buyumlar zakot bo‘lmaydi, shuningdek, kishilarni taomlantirib, «mana shu mening zakotim» deyish ham joiz emas. Lekin taom sotib olib, zakot deb niyat qilib bersa bo‘ladi.
Hanafiy mazhabi bo‘yicha, aqli zaif yoki yosh bolaga zakot berib bo‘lmaydi. 
«Sadaqa qilindi» degani «birovga bir narsa mulk qilib berildi» deganidir. «Faqirlargadir» deganda ham arab tili qoidasida ularga mulk qilib berish tushuniladi.
""",reply_markup=admin_keyboard.zakot_orqa_button)
  
 
@dp.callback_query(F.data == "chorvaning_zakoti")
async def chorvaning_zakoti(callback: CallbackQuery):
    await callback.message.answer(text="""
Chorva hayvonlari zakotining shartlari:
1. Yaylovdao‘tlaydigan bo‘lishi.
2. Ishchi hayvonbo‘lmasligi.
Yaylovda o‘tlaydigan bo‘lishi, ya’ni yilningko‘p qismida ommaviy yaylovda o‘tlab, semirib, bolalabyurishi. Yilning ba’zi vaqtida qo‘ldan yem yesa ham bo‘laveradi. Yilning ko‘p qismidaqo‘lda boqilgan hayvonlardan zakot berilmaydi. Chunki ularniboqishga shaxsiy mehnat va sarf-xarajat ko‘p ketganbo‘ladi.
Yilning ko‘p qismida yaylovda boqilgan hayvonlarga esa mehnat ham, sarf-xarajatham juda oz ketadi. Asosan ko‘pchilikning haqqi bo‘lmish yaylovdan foydalaniladi. Shuning uchun ko‘pchilik ichidagi kambag‘al-miskinlarga zakotberish kerak bo‘ladi.
Ishchi hayvon bo‘lmasligi. Chorvahayvonlarining ishchisidan, ya’ni aravaga, omochga qo‘shiladigan, yuk tashishgaishlatiladigan, miniladigan, juvozda, suv chiqarishda yoki shunga o‘xshash ishlarda foydalanib turiladiganidan zakot olinmaydi, chunki bundayhayvonlar hojati asliya va ish vositasi hisoblanadi, o‘suvchi mol emas. Qolaversa, ularni ishga solibtopilgan narsalardan zakot chiqariladi. Ana o‘sha zakotyo‘lida xizmat qilganlari uchun ham ularning o‘zlaridan zakot olinmaydi.
Tuyadan olinadigan zakot miqdori
Tuyaning nisobi beshtadir. To‘rtta tuyasi bor kishiga zakot farz bo‘lmaydi. Lekin egasi o‘zi xohlab, bersa, ixtiyoriga havola. 
Hanafiy mazhabida tuyaning soni bir yuz yigirma bitta bo‘lgandan boshlab buning zakotiga tuyaga zakot berish boshlangan vaqtdagi zakot qo‘shilib, xuddi avvalgidek ortib boraveradi. Tuyalar ikki yuzga yetganda qo‘shimcha qo‘shish yana qaytadan boshlanadi.
Qoramolning zakoti
Qoramoldan zakot berish tartibi:
O‘ttizta qoramoldan bir yoshli erkak yoki urg‘ochi buzoq; 
Qirqta qoramoldan ikki yoshli erkak yoki urg‘ochi buzoq, 
Qirqtadan oshganda to oltmishtagacha ikki yoshli erkak yoki urg‘ochi buzoq hamda qirqtadan oshgan har bir bosh uchun ana shunday sifatli buzoq qiymatining qirqdan biri berib boriladi. 
Oltmishtadan oshganda har o‘ttizta qoramol uchun bir yoshli erkak buzoq, har qirqta qoramol uchun ikki yoshli urg‘ochi buzoq zakot qilib beriladi.
Masalan, qoramollar soni 41 ta bo‘lganda ikki yoshli erkak yoki urg‘ochi buzoq hamda shunday buzoq qiymatining qirqdan biri beriladi. 42 ta bo‘lsa, ikki yoshli erkak yoki urg‘ochi buzoq hamda shunday buzoq qiymatining qirqdan ikkisi beriladi va hokazo.
Qo‘y-echkilarning zakoti
40 ta qo‘y yoki echkidan bitta, 121 dan ikkita, 201 tadan uchta, 400 tadan to‘rtta, so‘ng har yuztadan bitta qo‘y zakot beriladi.
Qo‘ylarning soni qirqtaga yetganda nisobga yetgan bo‘ladi va ulardan bir dona qo‘y zakotga chiqariladi. Qo‘ylarning umumiy soni o‘ttiz to‘qqizta bo‘lsa ham, zakot farz bo‘lmaydi. Bunda zakot berish-bermaslikni egasining o‘zi biladi. Beraman desa, beradi, bermasa, gunohkor bo‘lmaydi. 
Qirqtadan to bir yuz o‘n to‘qqiztagacha bo‘lgan qo‘ylardan bir dona qo‘y zakotga beriladi. Bir yuz yigirmataga yetgandan so‘ng to ikki yuzga yetguncha ikkita qo‘y berilaveradi. Ikki yuzdan o‘tganidan keyin esa uchta qo‘y beriladi. 
Uch yuzdan oshgandan keyin esa har yuztasidan bitta qo‘y zakotga chiqariladi. Bunda qo‘y boqishni ko‘paytirish maqsadida ular qancha ko‘p bo‘lsa, shuncha oz zakot olish yo‘lga qo‘yilgan.
Echki ham qo‘y hisobida bo‘lishini unutmaslik kerak.
Otning zakoti
Quyidagi otlardan zakot olinmaydi:
1. Miniladigan, ishlatiladigan va harbiy xizmatga tayyorlangan otlar.
2. Yem berib boqiladigan otlar.
Demak, tijorat uchun boqiladigan ot, xachir va eshaklardan zakot olinadi.
""",reply_markup=admin_keyboard.zakot_orqa_button)
 

@dp.callback_query(F.data == "naqtdan_olinadigan_zakot")
async def naqtdan_olinadigan_zakot(callback: CallbackQuery):
    await callback.message.answer(text="""
Naqd puldan qanday qilib zakot chiqariladi? Uning shartlari qanday?
Naqd puldan zakot chiqarish farz bo‘lishi uchun unda quyidagi shartlar mavjud bo‘lishi lozim:
1. Pul nisobga yetgan bo‘lishi.
2. Bir yil to‘lishi.
3. Qarzdan xoli bo‘lishi.
4. Hojati asliyadan ortiq bo‘lishi.
Pul nisobga yetgan bo‘lishi. Tilla pul bo‘lsa, yigirma dinor, kumush pul bo‘lsa, ikki yuz dirham nisob ekanini yaxshi bilib oldik. Ammo hozir tilla ham, kumush ham pul sifatida ishlatilmaydi. Qog‘oz puldan qanday qilib zakot chiqariladi? Uning nisobi qancha?
Kumush xalqaro miqyosda pul o‘rnida umuman qabul qilinmay qo‘ydi. Tilla esa pul o‘lchovi sifatida dunyo bo‘yicha maqbul bo‘lib turibdi. Shuning uchun ulamolar qog‘oz pulni tillaning qiymati bilan o‘lchash kerak, degan fikrga kelganlar. Payg‘ambar sollallohu alayhi vasallamning vaqtlarida yigirma dinor pulning og‘irligi yigirma misqol bo‘lardi. Yigirma misqol esa sakson besh grammga teng.
Demak, 85 gramm tillaning bahosi qog‘oz pulning nisobi bo‘ladi. Kimda 85 gramm tillaning qiymatiga teng yoki undan ko‘p qog‘oz pul bo‘lsa, zakot berishi farz bo‘ladi. U odam pulini hisoblab turib, ikki yarim foizini, ya’ni qirqdan bir bo‘lagini zakotga berishi kerak.
Bir yil to‘lishi kerak. Naqd pullardan yoki ularning o‘rniga o‘tadigan narsalardan zakot farz bo‘lishi uchun lozim bo‘lgan shartlardan biri – o‘sha pul nisobga yetgan holida to‘liq bir yil turishi kerak. Hanafiy mazhabi bo‘yicha, yilning o‘rtasida pul nisobdan kam bo‘lsa ham, yilning boshida va oxirida to‘liq bo‘lsa, zakot farz bo‘laveradi.
Foydaga kelgan mollardan: oylik maosh, ish haqqi, mukofotlar, hunar qilib topilgan pullar, ijaraga qo‘yilgan imoratlar, mehmonxona, zavod yoki fabrika va mashinalardan tushgan foydalarni ham asl sarmoyaga qo‘shib turib zakot chiqariladi.
Qarzdan xoli bo‘lishi kerak. Puldan zakot farz bo‘lishi uchun u qaytarib berilishi zarur bo‘lgan qarz bo‘lmasligi kerak. Aytaylik, birovning qo‘lida nisobga yetgan puli bor. Shu bilan birga, qarzi ham bor. U avval qarzini berishi kerak. Uni berganidan keyin puli nisobdan kam bo‘lib qolsa, unga zakot farz bo‘lmaydi.
Hojati asliyadan ortiq bo‘lishi kerak.  Deylik, bir kishining qo‘lida nisobga yetgan puli bor. Ammo u o‘ziga va qaramog‘idagi kishilarga qishlik yoki yozlik kiyim olishi kerak. Yoki bir yillik oziq-ovqatining sarf-xarajati ham bor. Uy sotib olishi, uyiga kerakli anjomlar, kasb-hunari uchun asboblar, mingani, zarurat uchun ulov yoki o‘qigani kitob olishi kerak. Ushbu narsalarni yoki ulardan ba’zilarini sotib olganidan keyin puli nisobdan kam bo‘lib qolsa, unga zakot farz bo‘lmaydi. Sotib olishidan oldin esa puli nisobga yetgan bo‘lsa, farz bo‘ladi. Chunki zakot o‘ziga to‘q, o‘z ehtiyojlaridan ortiqcha puli bor boy odamlarga farzdir.
""",reply_markup=admin_keyboard.zakot_orqa_button)
 

@dp.callback_query(F.data == "tijorat_moli")
async def tijorat_moli(callback: CallbackQuery):
    await callback.message.answer(text="""
Sotib olingan har bir narsa ham tijorat moli bo‘lavermaydi, chunki ularning orasida shaxsiy va oilaviy foydalanish uchun narsalar ham bo‘ladi. Faqatgina sotish, foyda olish niyatida xarid qilingan narsagina tijorat moli hisoblanadi.
Ulamolarimiz: «Tijoratda ikkita asosiy unsur: niyat va amal bor», deyishadi. Niyat – foyda ko‘rish maqsadi bo‘lsa, amal – oldi-sotdidir. Ushbu ikki unsur bir bo‘lgandagina, tijorat bo‘ladi. Biri bo‘lib, ikkinchisi bo‘lmasa, tijorat bo‘lmaydi.
Shunga ko‘ra, birov o‘zi uchun biror narsa olib, uni ishlatib yursa-yu, yaxshiroq foyda chiqsa sotib ham yuborish maqsadi bo‘lsa, u narsa tijorat moli bo‘lmaydi. Chunki uni aslida o‘zi uchun olgan. Aksincha, sotib, foyda ko‘rish niyatida olgan narsasidan o‘zi vaqtincha, yaxshiroq xaridor chiqquncha foydalanib tursa ham, u narsa tijorat moli hisoblanadi. Ammo ushbu narsani «Sotmayman, o‘zim foydalanaman», deb niyat qilsa-yu, foydalanib yursa, o‘sha mol tijorat moli bo‘lmaydi va undan zakot ham bermaydi.
Tijorat mollaridan zakot farz bo‘lishining shartlari ham xuddi puldagi shartlarga o‘xshaydi, ya’ni buning uchun mol nisobga yetishi, bir yil to‘lishi, qarzdan xoli bo‘lishi va hojati asliyadan ortiq bo‘lishi lozim.
Zakot berish vaqti kelganda tojir qo‘lidagi va hisob raqamidagi pullarini, savdoga qo‘yilgan mollaridan bir yil to‘lganini va odamlarga bergan qarzlaridan qaytib kelishiga ko‘zi yetganlarini jamlab hisoblaydi, so‘ngra buning ikki yarim foizini zakotga chiqaradi.
Hisoblash vaqtida tijorat do‘koni binolari, binoning asbob-anjomlari, tijorat mollari qo‘yiladigan joylar, peshtaxta va shunga o‘xshash sotuvga qo‘yilmagan narsalar hisobga olinmaydi. Tijorat mollarining qiymati zakot chiqarilayotgan kundagi bahosida o‘lchanadi. Zakotni tijorat mollarining o‘zidan yoki qiymatidan chiqarsa ham bo‘ladi. Ammo kambag‘allarga foydaliroq bo‘lgani uchun qiymatidan chiqarilsa, yaxshi bo‘ladi.
Zakot, sadaqai fitr, kafforat, ushr va nazrlarda ularning qiymatini berish ham joiz. Bir yil to‘lgandan keyin kamaysa, zakotning o‘sha kamaygan miqdordagi ulushi soqit bo‘ladi. Zakot nisobdadir, afv qilingan narsada emas. 
Agar qirqta tuyaga bir yil to‘lgandan keyin o‘n beshtasi halok bo‘lsa, binti maxoz berish vojib bo‘ladi.
Yilning o‘rtasida ko‘rilgan foyda o‘z jinsidan bo‘lgan nisobga qo‘shiladi. 
Nisobni mukammal qilish uchun tilla kumushga va tijorat mollari qiymati ila ikkisiga qo‘shiladi. 
Nisobning yil davomida noqis bo‘lgani (kamaygani) hisob emas. Zakotni bir yil va undan ham avvalroq berish joiz.
Shuningdek, bir nisobga sohib bo‘lgan kishi bir necha nisobning zakotini oldindan bersa bo‘ladi («Kifoya»dan).
Bu yerda zakotga oid bir necha masala muolaja qilinmoqda. Avvalo, zakot va unga o‘xshash moliyaviy ibodatda beriladigan narsalarning o‘zini bermay, qiymatini bersa ham bo‘lishi haqida so‘z bormoqda.
Zakot, sadaqai fitr, kafforat, ushr va nazrlarning qiymatini berish ham joizligi haqida hanafiy mazhabining ulamolari: «Qiymatini chiqarsa yaxshi bo‘ladi, ba’zi vaqtlarda qiymatini berish miskin va faqirlar uchun manfaatliroq bo‘ladi», deyishadi. Zamondosh ulamolarimiz bu boradagi barcha ma’lumotlarni to‘liq va atroflicha o‘rganib chiqib, hanafiy mazhabining tutgan yo‘li hozirgi zamon uchun munosib, degan fikrga kelishgan.
Zakotga beriladigan hayvon o‘rniga uning qiymatini bersa bo‘ladimi? Hanafiy mazhabida: «Zakotga beriladigan hayvon o‘rniga uning qiymati berilsa bo‘ladi», deyiladi. Qiymat har yurtning o‘z narxida va zakot berilayotgan kunning bahosiga qarab bo‘ladi.
""",reply_markup=admin_keyboard.zakot_orqa_button)
 

@dp.callback_query(F.data == "taqinchoqlar_zakoti")
async def taqinchoqlar_zakoti(callback: CallbackQuery):
    await callback.message.answer(text="""
Ushbu masalada fiqhiy mazhablar ikkiga bo‘linishgan:
1. Hanafiy mazhabi: «Ayollarning taqinchoqlaridan zakot chiqariladi», degan.
2. Molikiy, shofe’iy va hanbaliy mazhablari: «Ayollarning odatdagi tilla va kumush taqinchoqlaridan zakot chiqarish farz emas», degan.
Hanafiy ulamolarimiz tilla-kumush buyumlar, idishlar va taqinchoqlardan zakot berish borasida quyidagi fikrlarni aytishgan:
1. Tilla va kumushdan yasalgan turli buyumlar, idishlar uchun zakot berish farzdir. Avvalo, Islom bu narsalarni isrofgarchilik, manmanlik hamda kambag‘allarning ko‘ngli cho‘kishiga sabab bo‘lgani uchun harom qilgan. Musulmon odam mazkur narsalarni uyida saqlamagani ma’qul. Ammo kim ushbu qoidaga rioya qilmay, ularni o‘ziga mulk qilib olgan bo‘lsa, o‘sha narsalarning o‘zi yoki boshqa mulk bilan qo‘shilganda nisobga yetsa, zakot berishi farz bo‘ladi.
Ulamolarimizdan ba’zilari: «Bunday idish va buyumlarning nisobga yetganini aniqlash uchun ularning og‘irligi e’tiborga olinadi, agar 85 grammga yetsa, nisobga yetgan bo‘ladi», deganlar. Ba’zilari esa: «Qiymati e’tiborga olinadi, chunki bu narsalar san’at asari sifatida bahosi yana ham ortgan bo‘ladi», deyishadi.
2. Erkak kishilarning tilla va kumush taqinchoqlaridan ham zakot olinadi. Erkak kishiga shariatimizda bitta kumush uzuk taqishga ruxsat berilgan. Lekin shunday bo‘lsa ham, o‘sha narsalardan taqinchog‘i bo‘lsa, uni taqish yoki taqmasligidan qat’i nazar, o‘ziga mulk bo‘lib turgani uchun zakot beradi. Uni boshqa mulklarga qo‘shib nisob hisobiga kiritadi. Bu narsalarning hammasi o‘sishi kerak bo‘lgan molni o‘lik mol qilib qo‘yish hisoblanadi va Islomda qoralanadi. Zarurat uchun, kishining sog‘lig‘i uchun qilingan tilla va kumush narsalar, masalan, tish, burun va shunga o‘xshashlardan zakot berilmaydi.
3. Marjon, la’l, zumrad, olmos, yoqut kabi narsalardan zakot berilmaydi. Chunki bu narsalar o‘smaydigan mol hisoblanadi. Faqat ayollarning zebu-ziynati shaklida ishlatiladi.
4. Tilla va kumush taqinchoqlar taqish uchun emas, pulni band qilish uchun, jamg‘arma qilish uchun, sotib-foyda ko‘rish uchun olib qo‘yilgan bo‘lsa, ulardan zakot berish vojib bo‘ladi. Agar shunday qilinmasa, odamlar zakot berishdan qochib, puliga tilla va kumush taqinchoqlar olib qo‘yishga o‘tadi. Qolaversa, bunday taqinchoqlar ayollarning hojati uchun emas, pulni ushlab va uning foydasini olish uchun jamg‘arilgan bo‘ladi.
""",reply_markup=admin_keyboard.zakot_orqa_button)
 

@dp.callback_query(F.data == "toshlar_zakoti")
async def toshlar_zakoti(callback: CallbackQuery):
    await callback.message.answer(text="""
Tog‘dan topilgan feruzadan zakot berilmaydi, chunki bunga o‘xshash narsalar tuz kabi yerning bir bo‘lagi hisoblanadi.
Shuningdek, marvarid, la’l, zumrad, olmos, yoqut kabi narsalardan zakot berilmaydi, chunki bu narsalar o‘smaydigan mol hisoblanib, faqat ayollarning zebu ziynati sifatida ishlatiladi.
Odamlar tomonidan yerga ko‘milgan narsa topilsa va unda kalimai shahodat yoki shunga o‘xshash islomiy alomatlar bo‘lsa, uning hukmi tushib qolgandan keyin topib olingan narsaning hukmi kabi bo‘ladi. Albatta, bu kabi narsalar musulmonlarning mulki hisoblanadi. Bu holda xuddi topib olingan narsa kabi mazkur dafinaning ham egasini topib, unga qaytarib berish uchun shariatda qabul qilingan choralar ko‘riladi. Egasi topilmasa, topilmaning hukmida bo‘ladi.
Hanafiy, molikiy va hanbaliy mazhabi ulamolari: «Dafinaning zakoti davlat mulkiga qo‘shiladi», deyishgan. Shofe’iy mazhabida esa: «Dafinaning zakoti boshqa zakotlar beriladigan haqdorlarga beriladi», deyilgan. Nima bo‘lganda ham, dafinaning zakotini berish kerak.
""",reply_markup=admin_keyboard.zakot_orqa_button)

@dp.callback_query(F.data == "olishi_mumkinlar")
async def olishi_mumkinlar(callback: CallbackQuery):
    await callback.message.answer(text="""
Zakot olishi harom bo‘lganlar quyidagilardir:
Orasida tug‘ishganlik va er-xotinlik aloqasi borlar.
Bu toifaga kishining tuqqanlari, ya’ni ota-onasi, bobo-momolari necha pog‘ona yuqori bo‘lsa ham kiradi. Mazkur kishi ana o‘shalarga zakotini berishi mumkin emas.
O‘zining quliga, bir qismini ozod qilgan quliga zakot berilmaydi.
Qul xojaning mulki bo‘ladi. O‘zining mulkiga zakot berish durust emas.
Zimmiyga emas. Unga (zimmiyga) zakotdan boshqasini bersa bo‘ladi.
Zimmiyga zakotdan boshqasini bersa bo‘ladi. Islom davlati soyasida yashayotgan «ahli zimma» deb ataluvchi boshqa din vakillariga zakotdan berib bo‘lmaydi. Chunki zakot musulmonlardan olinib, musulmonlarga berilishi shart. Ammo ahli zimmaga nafl sadaqalardan, sadaqai fitrdan bersa bo‘ladi. Chunki avval aytilganidek, zakot moliyaviy ibodat bo‘lib, uni berish uchun ham, olish uchun ham musulmon bo‘lish kerak.
Fosiq kishiga zakot bersa bo‘ladimi?
«Fosiq» deb ba’zi gunoh ishlarni qilib nomi chiqqan odamga aytiladi. O‘zi musulmon odam-u, lekin gunoh ishlar ham qilgan bo‘ladi. Qadimgi ulamolarimiz bunday odamlarga zakot berish mumkin, deyishgan va zakotni olgandan keyin uni fisq va gunoh ishlarga sarflamasligi aniq bo‘lishi kerak, degan shartni qo‘yishgan.
Kuch-quvvati yetarli, biror kasbga qodir kishilarga zakotdan berilmaydi.
Kasb-korga qodir bo‘lgan, sog‘lom kishiga zakotdan ulush berilmasligi uchun unda quyidagi shartlar mavjud bo‘lishi kerak:
1) O‘z kasbiga yarasha ishi mavjud bo‘lishi;
2) Bu ish halol ish bo‘lishi;
3) Mazkur ish toqatidan tashqari, chidab bo‘lmaydigan darajada bo‘lmasligi;
4) Bu ish unga munosib, o‘ziga o‘xshash kishilarning obro‘sini to‘kmaydigan ish bo‘lishi;
5) O‘zida va qaramog‘idagilarda yetarli kasb qilish imkoni bo‘lishi.
Tarkidunyo qilib, ibodatga berilgan odamga zakotdan ulush berilmaydi.
""",reply_markup=admin_keyboard.zakot_orqa_button) 
    
@dp.callback_query(F.data == "zakot_beruvchi")
async def zakot_beruvchi(callback: CallbackQuery):
    await callback.message.answer(text="""
Zakotni ado qiluvchi bandaning zimmasida bajarishi lozim bo‘lgan quyidagi vazifalar bor:
1. Zakotdan murod nimaligini fahmlashi kerak. U uch narsadan iborat: Alloh taoloning muhabbatini da’vo qiluvchini o‘zi muhabbat qo‘ygan narsasini chiqarishi bilan sinash; halokatga olib boruvchi baxillik sifatidan poklanish; mol-mulk ne’matiga shukr qilish.
2. Riyokorlikdan xoli bo‘lish uchun zakotni sir tutish. Uni izhor qilishda faqirni xorlash bor. Agar «zakotni bermadi» degan tuhmatdan qo‘rqsa, faqirlarga jamoat ichida ochiqchasiga beradi. Boshqalarga pinhona ravishda beradi.
3. Zakotini minnat va ozor bilan buzmaydi. Inson faqirga ehson qilayotganida  minnat hosil bo‘lishi mumkin. Aslida esa, uning zakotini olgan faqir kishi Alloh taoloning unga buyurgan haqqini qabul qilib, unga yaxshilik qilayotgan, uning molini birovning haqqidan poklayotgan bo‘ladi. Zakot beruvchi yaxshiroq o‘ylab ko‘rsa, uning zakot chiqarishi u bilan faqir o‘rtasidagi muomala emas, balki mol ne’matiga shukrdir. Shuning uchun faqir odam faqirligi uchun haqoratlanmasligi kerak, chunki fazl mol-mulkning borligi yoki yo‘qligida emas.
4. Berayotgan narsasini kichik sanashi lozim, chunki ishni katta sanagan odam u bilan faxrlanadi. Yaxshi ish uch narsa bilan: uni kichik sanash, tezlatish va sir tutish ila tugal bo‘ladi.
5. Zakot beruvchi molidan eng halolini, eng yaxshisini va o‘ziga eng mahbubini chiqarsin.
6. Sadaqasini berishga loyiq odam topish. Ularda quyidagi sifatlar bo‘lishi kerak:
Birinchi sifat: taqvo.
Ikkinchi sifat: ilmli bo‘lish.
Uchinchi sifat: «Ne’mat berish yolg‘iz Alloh taoloning O‘zidan bo‘ladi», deb e’tiqoddagi odam bo‘lishi.
To‘rtinchi sifat: faqirligini yashiradigan, hojatmandligini bekitadigan va oshkora shikoyat qilmaydigan bo‘lish.
Beshinchi sifat: ayolmand, qarzga duchor bo‘lgan, og‘ir kasallikka chalingan kishilar bo‘lsin.
Oltinchi sifat: qarindosh-urug‘lardan bo‘lsin, chunki ularga qilingan sadaqa – ham sadaqa, ham silai rahmdir. Kimda ushbu sifatlardan ikkitasi yoki ko‘prog‘i jam bo‘lsa, zakotni ana shunday odamga berish afzaldir.
Zakot oluvchining vazifalari
Zakotni oluvchi Qur’onda zikr qilingan sakkiz toifadan biri bo‘lishi lozim. Uning zimmasida bir necha vazifa bor:
1. Alloh taolo uni g‘amga solgan narsani bartaraf qilish uchun zakotni unga berishni buyurganini fahmlasin va barcha g‘amini yig‘ib, bitta g‘amga – Alloh taoloning roziligini topishga aylantirsin.
2. Beruvchiga tashakkur aytib, uning haqqiga duo qilsin. Lekin bu duosi sababning shukri miqdorida bo‘lsin.
3. O‘ziga berilgan narsaga e’tibor bersin, halol bo‘lmagan narsani mutlaqo olmasin, chunki bir kishi birovning molidan zakot chiqarsa, bu narsa zakot bo‘lmaydi. Agar shubhali narsa bo‘lsa, o‘zini olib qochsin. Ilojsiz qolgandagina hojatiga yarashasini olsin.
4. O‘ziga muboh bo‘lgan miqdorda olsin, hojatidan ko‘pini olmasin. Agar qarzdor bo‘lsa, qarzidan ortig‘ini olmasin.
""",reply_markup=admin_keyboard.zakot_orqa_button) 
    


#Ro'za   ===-------------------==
@dp.message(F.text=="Ro'za")
async def message(message:Message):
    await message.answer(text="Ro'za",reply_markup=admin_keyboard.ruza)  


@dp.callback_query(F.data == "ruza_button_orqga")
async def ruza_button_orqga(callback: CallbackQuery):
    await callback.message.answer(text="""Ro'za""",reply_markup=admin_keyboard.ruza) 


@dp.callback_query(F.data == "zuza_qanday_ibodat")
async def zuza_qanday_ibodat(callback: CallbackQuery):
    await callback.message.answer(text="""
Shar’iy istilohda esa Ramazon oyida tong otganidan to quyosh botguncha niyat bilan ovqat yemaslik, ichimlik ichmaslik, jinsiy yaqinlik qilmaslik «ro‘za» deyiladi. Ro‘za tutish Islom dinining besh rukni, besh asosidan biridir, Qur’on va Sunnat bilan sobit bo‘lgan.
Ro‘za aqli raso, sog‘lig‘i yaxshi bo‘lgan har bir musulmon erkakka hamda hayz va nifosdan pok bo‘lgan musulmon ayolga farz qilingan. Hayz va nifos ko‘rgan ayollar ro‘za tutishmaydi, keyin qoldirgan kunlarining qazosini tutib berishadi. Yangi oyni ko‘rib, ro‘zaga niyat qilish Ramazon ro‘zasining asosiy shartlaridandir. Ramazon oyida noshar’iy amallar qilmaslik, tilni g‘iybat, yolg‘on so‘zlardan tiyish, o‘zgaga ozor bermaslik, yaxshi xulqli va rahm-shafqatli bo‘lish ro‘zaning odoblaridandir.
Ramazon kechasida turib saharlik qilishning o‘zi ro‘zaning niyatiga o‘tadi, chunki saharlik qilayotgan odamning ko‘ngliga ro‘za tutish niyati o‘z-o‘zidan keladi. Hanafiy mazhabida Ramazon tugagunicha har kuni niyat yangilab turiladi.
Hanafiy mazhabiga ko‘ra, Ramazon ro‘zasini tutishda har kungi niyatni quyosh oqqunigacha yangilab olsa ham bo‘laveradi, ya’ni kishi tongdan choshgohgacha ro‘zaga zid ish qilmay tursa, quyosh tikkaga kelishidan ozgina oldin o‘sha kunning ro‘zasi uchun niyat qilsa ham, ro‘za hisobiga o‘tadi. Lekin tongdan keyin yeb-ichib qo‘ygan bo‘lsa, keyin niyat qilsa durust bo‘lmaydi.
Ro‘zador kishiga yana ushbular sunnatdir: nafsni yomon niyatlardan to‘xtatish; foydasiz hamda uyatsiz so‘zlarni gapirishdan va eshitishdan o‘zini saqlash; birov bilan urishishdan, har qanday gunoh ishlardan o‘zni tortish; mumkin qadar istig‘for, zikr va tasbeh bilan band bo‘lish; Qur’on o‘qish; quyosh botgan vaqtda shom namozini o‘qishdan oldin bir qultum suv bilan bo‘lsa ham og‘iz ochish; Ramazon oyida har kuni xufton namozidan so‘ng yigirma rakat taroveh namozi o‘qish; taroveh namozida Qur’oni Karimni o‘qib yoki eshitib xatm qilish; Ramazonda xuftonni jamoat bilan o‘qigan kishining vitr namozini ham jamoat bilan o‘qishi.
Nafsni poklash va axloqni sayqallashda namoz va zakotdan keyin ro‘za ibodati keladi. Insonni yo‘ldan uradigan narsalar ichida qorin va jinsiy shahvatlar eng kuchlilaridan ekani hech kimga sir emas. Ro‘zaning foydalaridan biri xuddi o‘sha ikki shahvatni jilovlashga xizmat qilishidir.
""",reply_markup=admin_keyboard.ruza_button) 

@dp.callback_query(F.data == "ruzaning_darajalari")
async def ruzaning_darajalari(callback: CallbackQuery):
    await callback.message.answer(text="""
Ahli haqning nazdida ro‘zaning darajasi uchtadir:
Birinchi daraja ommaning ro‘zasi bo‘lib, u qorin va farjning istak-xohishlaridan tiyilishdir.
Ikkinchi daraja xoslarning ro‘zasi bo‘lib, u birinchi darajaga ziyoda o‘laroq ko‘z, quloq, tilni, oyoq, qo‘l va boshqa a’zolarni ham gunohlardan tiyishdir.
Uchinchi daraja xoslardan ham xoslarning ro‘zasi bo‘lib, u avvalgi ikki darajaga ziyoda o‘laroq qalbni behuda qiziqishlardan, dunyoviy fikrlardan va Alloh taolodan boshqa narsalardan tiyishdan iboratdir.
Xoslarning ro‘zasi «solihlar ro‘zasi» deb ham nomlanadi. Bu darajadagi ro‘zaning mukammal bo‘lishi quyidagi omillar bilan ro‘yobga chiqadi:
1. Barcha yoqimsiz va yomon narsalardan ko‘zni tiyish hamda qalbni Alloh taoloning zikridan to‘sadigan narsalarga mashg‘ul qilmaslik.
2. Tilni yolg‘on, g‘iybat, chaqimchilik, fahsh-uyat gaplar, jafo, xusumat, maqtanchoqlikka o‘xshash narsalardan tiyib, sukutni lozim tutish. Uni Alloh taoloning zikri va Qur’on tilovati bilan mashg‘ul qilish. Bu, tilning ro‘zasidir.
3. Quloqni eshitish makruh bo‘lgan barcha narsalardan, boshqacha qilib aytganda, yuqorida sanab o‘tilgan narsalarning hammasidan saqlash. Chunki gapirish mumkin bo‘lmagan barcha narsani eshitish ham mumkin emas.
4. Qo‘l, oyoq va boshqa a’zolarni gunohlardan saqlash hamda iftordan keyin qorinni shubhali taomlardan saqlash. Zotan, qorinni halol narsadan saqlab ro‘za tutib, keyin halol bo‘lmagan narsa bilan iftor qilishning ma’nosi ham yo‘q. Harom narsalar dinni halok qiluvchi zahardir. Halol esa dori kabi ozi foydali, ko‘pi zararlidir.
5. Iftorda haddan tashqari ko‘p yeb, qorinni to‘ydirib yuborishdan saqlanish. Bunday qilish bilan ro‘zadan ko‘zlangan maqsad amalga oshmaydi. Chunki ro‘zadan ko‘zlangan maqsadlardan biri ochlikning mashaqqatini his qilishdir. Mazkur maqsadga erishish esa, ro‘zadan boshqa vaqtlarda nonushtada tanovul qiladigan taomni saharlikda va kechki ovqatda tanovul qiladiganini iftorda iste’mol qilish bilan bo‘ladi.
Iftordan so‘ng qalb xavf va rajo orasida bo‘lishi lozim, chunki ro‘zasi qabul bo‘lib, muqarrab bandalar qatoriga qo‘shildimi yoki qabul bo‘lmay, g‘azabga uchraganlardan bo‘ldimi, aniq emas. Har bir ibodatdan forig‘ bo‘lgandan so‘ng shu holatda bo‘lish lozim.
Ramazon taqvo oyidir. Bu oyda xulqimiz yanada yuksalib, harom va shubhalardan har qachongidan ham ko‘proq tiyilishimiz zarur. Shunday tabarruk oyda qiz-kelinlarimizni milliyligimizga yot bo‘lgan holatda kiyinib yurishdan, erkaklarimizni nomahramlarga ko‘z tikishdan qaytarishimiz lozim. Vaholanki, hadisda «Ko‘ngilning taqvosi haromga qaramaslikdir», deyilgan.
Ramazon ibodatlarni ko‘paytirish, gunohlarga mag‘firat so‘rash, Qur’on bilan oshno bo‘lish, Allohga bandalikni yuksak darajaga ko‘tarish oyidir. Shunday bo‘lgach, Ramazonni taqvo, halollik, husni xulq va yaxshiliklar oyiga aylantirish har bir musulmonning burchidir.
""",reply_markup=admin_keyboard.ruza_button) 
    
@dp.callback_query(F.data == "ruzaning_shartlari")
async def ruzaning_shartlari(callback: CallbackQuery):
    await callback.message.answer(text="""
Ro‘za durust bo‘lishi uchun uch xil shart topilishi lozim.
Birinchi shart – zimmaga lozim bo‘lish shartlari.
Bu shartlar to‘rttadir:
1. Islom. Musulmon bo‘lmagan odamga ro‘za farz bo‘lmaydi. Unday odam ro‘za tutsa ham, ro‘zasi ibodat o‘rniga o‘tmaydi. Kofir odam Ramazonda Islomga kirsa, o‘sha kundan boshlab ro‘za tutadi.
2. Aql. Aqli yo‘q odamga ro‘za farz bo‘lmaydi, chunki u mukallaf emas.
3. Balog‘at. Balog‘atga yetmagan yosh bolalarga ro‘za farz bo‘lmaydi. Ramazon oyida balog‘atga yetganlar o‘sha kundan boshlab ro‘za tutishni boshlaydilar.
Ikkinchi shart – ro‘zani ado etish uchun lozim shartlar:
Bu shartlar ikkitadir:
1) Sog‘lom bo‘lish. Bemor kishiga ro‘za tutish vojib emas.
2) Muqim bo‘lish. Musofirga ro‘za tutish farz emas. U safardan qaytganda qazosini tutib beradi.
Uchinchi shart – ro‘zaning to‘g‘ri bo‘lishi shartlari.
Bu shartlar uchtadir:
1) Niyat. Niyatsiz ro‘za durust bo‘lmaydi.
2) Nifos va hayzdan xoli bo‘lish. Nifos va hayzli bo‘laturib tutilgan ro‘za durust bo‘lmaydi.
Ramazon ro‘zasining adosi va qazosi shar’iy kunduzning yarmidan avval niyat qilish bilan to‘g‘ri bo‘ladi.
Ma’lumki, qilinishi lozim bo‘lgan amalni shariatda belgilangan vaqtda qilish «ado» deyiladi. Qilinishi lozim bo‘lgan amalni belgilangan vaqtidan keyin bajarish «qazo» deyiladi.
Ramazon ro‘zasini vaqtida tutish farz. Agar u vaqtida ado qilinmagan bo‘lsa, qazosini tutish farz.
Shuningdek, kafforat ro‘zalari ham vojibdir. Birovni xato, ehtiyotsizlik sababli o‘ldirib qo‘ygan yoki ayolini zihor qilgan odam boshqa kafforatlarni bajara olmasa, ketma-ket ikki oy ro‘za tutishi vojib bo‘ladi.
Shar’iy kunduz tong otgandan (subhi sodiqdan) boshlanib, quyosh botguncha davom etadi. Shar’iy bo‘lmagan kunduz esa «lug‘aviy kunduz» deb ataladi va u quyosh chiqqandan boshlab botguncha davom etadi. Demak, ro‘za tutmoqchi bo‘lgan kishi tong otgandan boshlab kunduzning yarmigacha niyat qilib olsa, ro‘zasi to‘g‘ri bo‘ladi.
""",reply_markup=admin_keyboard.ruza_button) 
    


@dp.callback_query(F.data == "ruzaning_turlari")
async def ruzaning_turlari(callback: CallbackQuery):
    await callback.message.answer(text="""
Ro‘zaning turlari to‘rttadir:
Lozim ro‘za.
Lozim ro‘za ikkiga: farz va vojibga bo‘linadi.
Farz ro‘za. U ham ikkiga: tayin qilingan va tayin qilinmagan farz ro‘zaga bo‘linadi.
Tayin qilingan farz ro‘za – Ramazon ro‘zasini ado etishdir. Bu Qur’on, sunnat va ulamolar ijmo’i bilan sobit bo‘lgan.
Tayin qilinmagan farz ro‘za – Ramazonning qazosi va kafforatining ro‘zasidir.
Shuningdek, hayz va nifosli ayollar, homilador va emizikli ayollar ham imkon topganlarida Ramazonning qazo ro‘zasini tutadilar.
Vojib ro‘za ham ikkiga: tayin qilingan va tayin qilinmagan vojib ro‘zaga bo‘linadi.
Tayin qilingan vojib ro‘za – muayyan nazr (tayinli kun) ro‘za va Ramazon oyining hilolini ko‘rib, shahodati qabul qilinmagan kishining ro‘zasidir.
Tayin qilinmagan vojib ro‘za:
a) Nazr ro‘za (mutlaq ro‘za ham deyiladi). Bu kunini tayin qilmasdan, bir kun ro‘za tutishni nazr qilgan kishining ro‘zasidir. Masalan, «Falon ishim amalga oshsa, bir kun ro‘za tutishni nazr qildim» deyilgani kabi.
b) Muayyan kunda ro‘za tutishni nazr qilib, tuta olmagan kishining qazo ro‘zasi.
v) Ro‘za tutishga qasam ichib, zimmasiga ro‘zani vojib qilib olgan kishining ro‘zasi.
g) Nafl ro‘zani tutishni boshlab, oxiriga yetkazmay, ochib yuborgan kishining o‘sha kun uchun tutadigan qazo ro‘zasi.
d) Kafforat ro‘zalari: zihor, qatl, Ramazonning ro‘zasini qasddan ochib yuborish va qasamni buzganligining kafforati uchun tutiladigan ro‘zalar.
ye) Tamattu’ va qiron uchun ehromga kirib, qurbonlik qila olmagan kishining o‘n kunlik ro‘zasi.
j) Ehromdalik chog‘ida, vaqti kirmasidan oldin soch oldirgan kishining kafforat uchun tutadigan uch kunlik ro‘zasi.
z) Haramda ov qilishning jazosi uchun tutiladigan ro‘za.
i) E’tikofini buzib qo‘ygan kishining qazo ro‘zasi.
""",reply_markup=admin_keyboard.ruza_button)

@dp.callback_query(F.data == "ruza_tutishga_harom_kunlar")
async def ruza_tutishga_harom_kunlar(callback: CallbackQuery):
    await callback.message.answer(text="""
Ro‘za tutish harom bo‘lgan kunlar quyidagilardir:
1. Iydul-fitr kuni, Iydul-azho kuni va undan keyingi uch kun. Bu kunlarda ro‘za tutish haromdir, chunki bu kunlar xursandchilik kunlaridir.
2. Shak kuni, ya’ni Ramazon kirishidan oldingi kunda ro‘za tutish.
3. Ro‘za tutsa halok bo‘lishini bila turib ro‘za tutgan odamning ro‘zasi.
4. Ayollarning hayz va nifos ko‘rgan kunlari. Bu kunlarda ro‘za tutish mumkin emas.
""",reply_markup=admin_keyboard.ruza_button) 
    
@dp.callback_query(F.data == "ruza_tutishga_makruh_kunlar")
async def ruza_tutishga_makruh_kunlar(callback: CallbackQuery):
    await callback.message.answer(text="""
Quyidagi kunlarda ro‘za tutish makruhdir:
1. Ayol kishining erining iznisiz yoki roziligini bilmay turib nafl ro‘za tutishi (agar er yaqinlikka ojizlik qiladigan darajada bemor bo‘lsa, yoki ro‘zador bo‘lsa, yoxud haj yo umraga ehrom bog‘lagan bo‘lsa, makruh emas).
2. Ashuro kunining yolg‘iz o‘zida ro‘za tutish.
3. Juma kunini xoslab ro‘za tutish.
4. Shanba kunini ulug‘lab ro‘za tutish.
5. Yakshanba kunini ulug‘lab ro‘za tutish.
6. Navro‘z kuni ro‘za tutish.
7. Mehrjon kuni ro‘za tutish.
8. Uzluksiz har kuni ro‘za tutish.
9. Gapirmasdan ro‘za tutish.
10. Ulab (saharlik qilmay) ro‘za tutish.
11. Musofirning qiynalib ro‘za tutishi.
""",reply_markup=admin_keyboard.ruza_button) 


@dp.callback_query(F.data == "ruzaning_niyati")
async def ruzaning_niyati(callback: CallbackQuery):
    await callback.message.answer(text="""
«Niyat» so‘zi lug‘atda «qasd qilish» ma’nosini anglatadi. Shar’iy istilohda esa niyat deb qalbning bir ishni qilishga azmu qaror ila, ikkilanishsiz e’tiqod qilishiga aytiladi. Demak, kishi qalbida ertaga Ramazonning kunlaridan biri ekanini bilsa va ro‘za tutishni ko‘nglidan o‘tkazsa, niyat qilgan bo‘ladi.
Niyat masalasida ro‘zalar ikkiga bo‘linadi:
1. Kechasi niyat qilish va tayin qilish shart bo‘lgan ro‘zalar. Bunday ro‘zalar «zimmada sobit bo‘lgan ro‘zalar» ham deyiladi. Ular Ramazonning qazosi, buzib yuborilgan nafl ro‘zalarning qazosi, kafforat uchun tutiladigan ro‘zalar va mutlaq nazr qilingan ro‘zalardir.
2. Kechasi niyat qilish va tayin qilish shart bo‘lmagan ro‘zalar. Bunday ro‘zalar «muayyan zamonga bog‘liq ro‘zalar» ham deyiladi. Ular Ramazon ro‘zasi va barcha nafl ro‘zalar bo‘lib, shar’iy kunduzning yarmidan oldin qilingan niyat bilan to‘g‘ri bo‘laveradi.
Ramazon ro‘zasini nafl niyati bilan yoki mutlaq niyat yoxud boshqa vojib ro‘za niyati bilan ado qilsa ham bo‘ladi. Faqat safarda va bemorlikda bo‘lmaydi.
Ramazon ro‘zasi kabi nafl va muayyan nazr ro‘zani ham shar’iy kunduzning yarmidan avvalgi niyat bilan tutsa bo‘ladi. Faqat nafl va muayyan nazr ro‘zani boshqa vojib ro‘za niyati bilan tutib bo‘lmaydi, chunki ro‘za tutuvchi o‘ziga vojib bo‘lgan narsani o‘zi bekor qila olmaydi.
Qazo, kafforat va mutlaq nazr ro‘zalar uchun ularni kechasi tayin qilib, niyat qilish shart qilingan, chunki bunday ro‘zalar uchun muayyan vaqt tayin qilinmagan. Shuning uchun ularning boshlanish vaqtini tayin qilish vojib bo‘ladi.
Sha’bon oyining yigirma to‘qqizinchi kuni kechqurun quyosh botayotganda Ramazonning hiloli ko‘rinmasa va havo bulutli bo‘lsa, o‘ttizinchi kun shak kuni bo‘ladi, chunki o‘sha kun sha’bonning o‘ttizinchi kunimi yoki Ramazonning birinchi kunimi degan shak, ikkilanish bo‘ladi. Agar havo ochiq bo‘lsa ham oy ko‘rinmasa, shak bo‘lmaydi.
Niyat qilishning eng afzal vaqti iftor qilish paytida ertangi kunning ro‘zasini niyat qilishdir. Ramazon oyida ro‘za kunlari ekanini bilsa-da, ro‘za tutishni ham, tutmaslikni ham niyat qilmay tong ottirsa, ro‘zador bo‘lib qolmaydi. Zero, ro‘za kunlari ekanini bilishning o‘zi bilan ro‘zador bo‘lib qolinmaydi. «Inshaalloh, ertaga ro‘za tutaman» deyish bilan ham niyat durust bo‘laveradi, chunki ro‘zada bu kalimalar Alloh taolodan tavfiq, madad umidini ifoda qiladi.
Bir kishi har kuni ro‘za tutmoqchi bo‘lib saharlik qilsa, tili bilan ham, dili bilan ham ro‘zani niyat qilmasa ham, saharlik qilgani niyat o‘rniga o‘tadi. Lekin saharlik qilayotgan vaqtda ro‘za tutmaslikni niyat qilsa yoki odati har kuni o‘sha vaqtda taomlanish bo‘lsa yoxud hamma qatori saharlikka tursayu, o‘zi ro‘za tutmaydigan kishi bo‘lsa, uning saharlik qilgani niyat o‘rniga o‘tmaydi. Saharlik niyatning o‘rniga o‘tishi Ramazonning ro‘zasida, tayin qilingan nazrda va nafl ro‘zalardadir. Bundan boshqalarda esa saharlik qilish bilan birgalikda qaysi ro‘zani tutayotganini dil bilan niyat qilishi zarur. Kechaning avvalida «saharlikka turaman» deb niyat qilish ro‘za niyatining o‘rniga o‘tmaydi.
Quyosh botishi bilan ertangi kunning ro‘zasini niyat qilsa, niyati durust bo‘ladi. Masalan, bir kishi shunday niyat qilib, behush bo‘lib qolsayu, behushligi ertasi kunning quyoshi botgunicha davom etsa ham, u o‘sha kuni ro‘zador bo‘lgan hisoblanadi. Quyosh botishidan avval yoki botayotganda ertangi kunning ro‘zasini niyat qilishning o‘zi kifoya qilmaydi, balki quyosh botgandan so‘ng qayta niyat qilish zarur.
""",reply_markup=admin_keyboard.ruza_button) 

@dp.callback_query(F.data == "saharlik_va_iftorlik")
async def saharlik_va_iftorlik(callback: CallbackQuery):
    await callback.message.answer(text="""
Alloh taoloning har bir amri hikmatlarga boydir. «Allohning rahmati bahona qidirur» degan mashhur maqol bor. Alloh bu ummatga rahmatini yog‘dirishni iroda qilib, O‘z Payg‘ambari orqali saharlik va iftorlik qilishni sunnat qildi.
Musulmon kishi qorni to‘q bo‘lsa ham, taomga ehtiyoji bo‘lmasa ham saharlikda birorta xurmo yoki bir-ikki qultum suv ichib olsa, Payg‘ambarimiz alayhissalomning sunnatlariga ergashgan bo‘ladi. Zero, Anas ibn Molik roziyallohu anhu u zotning «Saharlik qilinglar, saharlikda baraka bor», deganlarini aytgan.
Tobe’inlardan Abu Atiyya va Masruqlar Oishaning huzuriga kirib, «Ey mo‘minlarning onasi, Muhammad sollallohu alayhi vasallamning sahobalaridan ikki kishi yaxshilikda musobaqalashishadi. Biri iftor bilan (shom) namozni tezlatadi. Boshqasi esa iftor bilan (shom) namozni ortga suradi», deyishdi. Oisha: «Qay biri iftorni va namozni tezlatadi?», deb so‘radi. «Abdulloh ibn Mas’ud», deyishdi. Oisha: «Rasululloh sollallohu alayhi vasallam shunday qilar edilar», dedilar. Iftor va namozni ortga surgan Abu Muso edi».
Abdulloh ibn Amr roziyallohu anhumodan rivoyat qilinadi:
«Rasululloh sollallohu alayhi vasallamning shunday deganlarini eshitdim: «Iftor paytida ro‘zadorning mustajob duosi bor».
Sahl ibn Sa’d roziyallohu anhudan rivoyat qilinadi:
«Rasululloh sollallohu alayhi vasallam: «Modomiki iftorni tez qilishar ekan, kishilar yaxshilikda bo‘lurlar», dedilar».
""",reply_markup=admin_keyboard.ruza_button) 
    
@dp.callback_query(F.data == "ruzaning_mustahablari")
async def ruzaning_mustahablari(callback: CallbackQuery):
    await callback.message.answer(text="""
uyidagi amallar ro‘zaning mustahablaridir:
1. Biror narsa bilan, bir qultum suv bilan bo‘lsa ham saharlik qilish, saharlikni kechaning oxirigacha surish.
2. Quyosh botishi bilan shom namozini o‘qishdan oldin darhol og‘izni ochish. Shirin va ho‘l narsa bilan og‘iz ochish afzal.
3. Og‘izni ochishda rivoyat qilingan lafzlar bilan duo qilish.
4. Ro‘zadorlarga iftor qilib berish.
5. Junublik, hayz va nifosdan qilinadigan g‘uslni kechga qo‘ymay, tong otishidan oldin qilib olish.
6. Til hamda a’zolarni ortiqcha gap-so‘z va amallardan tiyish.
7. Ro‘zani buzmaydigan, ammo huzurbaxsh narsalarni tark qilish.
8. Oila a’zolari va qarindoshlarga kengchilik qilish. Beva-bechora va kambag‘allarga xayr-ehsonni ko‘paytirish.
9. Qur’on qiroati, ilm suhbatlari, zikr va salavotlarni ko‘paytirish.
""",reply_markup=admin_keyboard.ruza_button) 
    
@dp.callback_query(F.data == "ro'zani_buzadigan_amal")
async def ruzani_buzadigan_amal(callback: CallbackQuery):
    await callback.message.answer(text="""
o‘zaning buzilishi ikki xil bo‘ladi.
Birinchisi – qazo va kafforatni vojib qiladigan holatlar.
Ikkinchisi – faqat qazoni vojib qiladigan holatlar.
Qazo va kafforat vojib bo‘ladigan holatlar. Kafforat Ramazonning hurmatini oyoqosti qilingani uchun vojib bo‘ladi. Ramazonning farz ro‘zasini ado qilishni niyat qilib ro‘za tutgan odam uni o‘z ixtiyori bilan, majburlashsiz va shar’iy uzrsiz qasddan ochib yuborsa, ham qazosini tutadi, ham kafforatni ado etadi. Lekin Ramazonning qazosini yoki boshqa ro‘zalarni qasddan buzsa kafforat vojib bo‘lmaydi.
Kafforat quyidagi holatlarda vojib bo‘ladi:
1. Gʻizo yoki shu kabi narsani shar’iy uzrsiz yeyish. Odatda ozuqa sifatida tanovul qilinadigan barcha narsalar g‘izoga kiradi. Dori, papiros, sigara, afyun, nasha va shunga o‘xshash narsalar ham g‘izo toifasiga kiradi. Ushbu holatlarda ro‘zasini ochgan odam ham qazosini tutadi, ham qul ozod qilish yoki oltmish kun ketma-ket ro‘za tutish, unga qodir bo‘lmasa, oltmish miskinga taom berish bilan kafforatni ado qiladi.
2. Birovni g‘iybat qilgani, qon oldirgani, shahvat bilan ushlagani yoki o‘pgani, quchoqlashib yotgani, mo‘ylabini moylagani sababli «ro‘zam ochilib ketdi» deb o‘y lab, qasddan yeb-ichib yuborgan odam ham qazo tutadi, ham kafforatni ado qiladi (Lekin faqih kishi «ro‘zang ochilibdi» deb fatvo bersa, bundan mustasno. Unda faqat qazo tutadi, kafforat vojib bo‘lmaydi).
3. Og‘ziga kirgan yomg‘ir suvini, xotinining tupugini lazzat uchun ichiga yutsa, kesakxo‘r odam kesakni yutib yuborsa, ham qazo tutib, ham kafforat ado qiladi.
4. Farj shahvatini to‘la ravishda qondirish. Bunda maniy to‘kilmasa ham qazo va kafforat vojib bo‘ladi. Jumhur ulamolar: «Jimo’da qatnashgani uchun ayol kishi ham kafforat beradi», deyishgan.
5. Ayol kishi yosh bolaning yoki majnunning o‘ziga yaqinlik qilishiga imkon bersa, unga ham qazo, ham kafforat vojib bo‘ladi.
Qazo tutish lozim bo‘ladigan, kafforat lozim bo‘lmaydigan holatlar:
1. Gʻizo sanalmagan va g‘izo toifasiga kirmaydigan narsani tanovul qilish. Bunda odatda g‘izo sanalmaydigan va inson ta’bi yeyishga moyil bo‘lmaydigan narsalar ko‘zda tutilgan. Misol uchun, ro‘zadorning xom guruch, xamir, biror narsa aralashtirilmagan un kabi narsalarni yeyishi.
2. Pishmagan mevani yeyish.
3. Tishlari orasida qolgan no‘xatdan katta narsani yutib yuborish.
4. Danak, paxta, qog‘oz, teri yeyish.
5. Tosh, temir parchasi, tuproq, tangaga o‘xshash narsalarni yutib yuborish.
6. Qasddan ichiga isiriqning tutuni kabi tutun kiritish.
7. Erkak kishining orqasidan, burnidan, tomog‘idan va ayol kishining oldidan suv yoki dori kiritilishi.
8. Quloqqa moy tomizilsa ham ro‘za ochiladi. Suv tomizilsa ochilmaydi.
9. Qasddan og‘zi to‘lib qayt qilsa ham qazo tutiladi. Agar beixtiyor, og‘zi to‘lmay qayt qilsa yoki taom emas, balg‘am qayt qilsa, ro‘za ochilmaydi.
10. Gʻizo va dorinini bemorlik, safar, majburlash, adashish, beparvolik yoki shubha kabi shar’iy uzrlar bilan tanovul qilsa, ro‘za ochilib, qazosi tutiladi.
""")
    await callback.message.answer(text="""
11. Og‘iz chayilayotganda beixtiyor ichiga suv ketib qolsa, ro‘za ochiladi va qazo tutiladi.
12. Boshdagi yoki qorindagi jarohatga qo‘yilgan dori ichiga yoki dimog‘iga ketib qolishi.
13. Uxlab yotgan odamning qorniga suv kiritib yuborilsa, ro‘zasi ochiladi.
14. Ayol kishi xizmatga yaramay qolaman deb taom yesa ham ro‘zasi ochilib, qazosini tutadi.
15. Ro‘zadorligini unutgan holda taom yesa yoki jimo’ qilsa, ro‘zasi ochilmaydi. Ammo buning hukmini bilmay, «bo‘lar ish bo‘ldi» deb, yana taom yesa yoki jimo’ qilsa, qazo ro‘za tutib berish lozim bo‘ladi.
16. Ro‘za tutishga kechasi emas, kunduzi niyat qilib, keyin «bu niyatim to‘g‘ri bo‘lmasa kerak» degan shubha bilan taom yeyilsa, ro‘za ochiladi va qazo tutish vojib bo‘ladi.
17. «Hali tong otmagan bo‘lsa kerak» deb, yeb-ichgan yoki jimo’ qilgan odam tong otib bo‘lganini bilib qolsa, ro‘zasining qazosini tutadi.
18. «Quyosh botgan bo‘lsa kerak» deb, yeb-ichgan yoki jimo’ qilgan odam quyosh botmaganini bilib qolsa, ro‘zasining qazosini tutadi.
19. Shahvatini to‘liq bo‘lmagan holda qondirsa ham faqat qazo tutadi.
20. Quchoqlash, o‘pish va shunga o‘xshashishlar tufayli maniy to‘kilsa, ro‘zaning qazosi tutiladi.
21. Uxlab yotgan ayolga jinsiy yaqinlik qilinsa, o‘sha ayol ham qazo tutadi.
22. Ro‘zador kishi orqasiga paxta, latta va shunga o‘xshash narsalarni kiritsa ham ro‘zasi ochilib, qazosini tutadi.                                  
23. Ramazon ro‘zasidan boshqa ro‘zasini ochib yuborgan kishiga faqat qazo tutish vojib bo‘ladi, kafforat vojib bo‘lmaydi.

""",reply_markup=admin_keyboard.ruza_button)
    
    
# Bot ishga tushishi va o‘chishi haqida xabar yuborish
@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin), text="Bot ishga tushdi")
        except Exception as err:
            logging.exception(err)

@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin), text="Bot ishdan to'xtadi!")
        except Exception as err:
            logging.exception(err)

def setup_middlewares(dispatcher: Dispatcher, bot: Bot) -> None:
    """MIDDLEWARE"""
    from middlewares.throttling import ThrottlingMiddleware
    dispatcher.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))

async def main() -> None:
    global bot, db
    bot = Bot(TOKEN,parse_mode=ParseMode.HTML)
    db = Database(path_to_db="main.db")
    db.create_table_users()
    await set_default_commands(bot)
    await dp.start_polling(bot)
    setup_middlewares(dispatcher=dp, bot=bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main()) 