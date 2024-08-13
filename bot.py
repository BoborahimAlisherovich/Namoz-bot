from aiogram.types import Message, InlineKeyboardButton
from filterss.check_sub_channel import IsCheckSubChannels
from states.reklama import Adverts
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time 
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram import F
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
from aiogram.client.bot import DefaultBotProperties

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
            reply_markup=admin_keyboard.start_button
        )
    except:
        await message.answer(
            text="Assalomu alaykum, botimizga xush kelibsiz. Bu bot orqali siz namoz o'qishni o'rganishingiz mumkin.",
            reply_markup=admin_keyboard.start_button
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
    await message.answer(text="Hududingizni tanlang", reply_markup=admin_keyboard.hudud)

# Bosh menyu
@dp.message(F.text == "🏠 Bosh Menyu")
async def orqa(message: Message):
    await message.answer(text="Menyulardan birini tanlang", reply_markup=admin_keyboard.start_button)
    await message.delete()

# Diqqatni jamlash haqida ma'lumot
@dp.message(F.text == "DIQQATNI JAMLASH")
async def namoz_vaqti(message: Message):
    await message.answer(
        text="""
Diqqatni pul deya qabul qiling.
Tasavvur qiling, diqqatingiz bu – pul. Bu valyuta sizda cheklangan miqdorda. 
Kun davomida uni “qimmat” va “qimmat bo‘lmagan” vazifalar uchun sarflashingiz mumkin. 
Jiddiy ish, mutolaa, siz uchun ahamiyatli vazifalar ko‘proq diqqat birligini talab etadi, biroq arzon turadi. 
Kam ahamiyatli masalan, ijtimoiy tarmoqlarni varaqlash kamroq diqqatni talab qiladi. 
Biroq u qimmat turadi. Diqqatning qarama-qarshi jihati ham shundan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/62'>Bizning kanal</a>  
"""
    )

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

# Tayammum haqida ma'lumot
@dp.message(F.text == "TAYAMMUM")
async def massaeg(messaga: Message):
    await messaga.answer(
        text="""
"Tayammum” lug‘atda “maqsad qilish” ma’nosini anglatadi. Istilohda esa poklanish maqsadida 
pok yer jinsi bilan yuzga va ikki qo‘lga tirsaklari bilan qo‘shib mash tortish “” deb ataladi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/40'>Bizning kanal</a>   
""", 
        reply_markup=admin_keyboard.Admin
    )

# Erkaklar uchun Namoz o'qishni o'rganish bo'limi

#-----------------------------------------------------------------------------------------------------------


# "🕋NOMOZ O'QISHNI O'RGANISH🤲" tugmasi uchun handler
@dp.message(F.text == "🕋NOMOZ O'QISHNI O'RGANISH🤲")
async def massaeg(messaga: Message):
    await messaga.answer("Tanlang", reply_markup=admin_keyboard.tanlash_)

# Erkaklar namozi uchun callback query
@dp.callback_query(F.data == "erkak_namozi")
async def erkak_namoz(callback: CallbackQuery):
    await callback.message.answer(text="Tanlang", reply_markup=admin_keyboard.erkak_namoz)

# Azon matnini ko'rsatish uchun callback query
@dp.callback_query(F.data == "azon")
async def azon(callback: CallbackQuery):
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
""")

# Bomdod namozi haqida ma'lumot
@dp.callback_query(F.data == "bomdod")
async def bomdod(callback: CallbackQuery):
    await callback.message.answer(text="Bomdod (fors.) — erta tong payti, sahar va shu paytda oʻqiladigan namoz. Bomdod namozi kun chiqish taraf yorishganidan boshlab to kun chiqqunga qadar oʻqiladi. Bamdod namozi ikki rakat sunnat va ikki rakat farzdan iborat. Erta tongda oʻqilgan namozning savobi qolgan namozlarga qaraganda kattaroq boʻladi. Namoz oʻqish musulmonlarning farzi hisoblanadi. <a href='https://t.me/namoz_uqishni_urganish_Kanal/14'>.</a>")

# Peshin namozi haqida ma'lumot
@dp.callback_query(F.data == "peshin")
async def peshin(callback: CallbackQuery):
    await callback.message.answer(text="""
Peshin (fors.) — kunning yarmi oʻtgan payti va shu paytda oʻqiladigan namoz. Peshin namozi toʻrt rakat sunnat, toʻrt rakat farz va ikki rakat sunnatdan iborat. Peshin namozi Quyosh qiyomdan ogʻa boshlashidan to asr namozining vaqti kirguncha ado etiladi. <a href='https://t.me/namoz_uqishni_urganish_Kanal/9'>.</a>""")

# Asr namozi haqida ma'lumot
@dp.callback_query(F.data == "asr")
async def asr(callback: CallbackQuery):
    await callback.message.answer(text="""
Asr namozi - Alloh taolo tomonidan farz qilingan namozlardan biri. Bu namozni musulmon kishi har kuni oʻqiydi. Ushbu namoz 4 rakat boʻlib faqat farzdan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/10'>Bizning kanal📢</a>""")

# Shom namozi haqida ma'lumot
@dp.callback_query(F.data == "shom")
async def shom(callback: CallbackQuery):
    await callback.message.answer(text="""
Shom — Quyosh botib, qorongʻulik boshlangan payt va shu vaqtda oʻqiladigan namoz. Shom namozi Quyosh botgandan boshlab, magʻrib ufqidagi qizil shafaqning koʻrinmay ketadigan vaqtigacha ado etiladi, uch rakat farz va ikki rakat sunnatdan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/11'>Bizning kanal📢</a>""")

# Xufton namozi haqida ma'lumot
@dp.callback_query(F.data == "xufton")
async def xufton(callback: CallbackQuery):
    await callback.message.answer(text="""
Xufton (fors. uxlash) — Quyosh botib ufqdagi qizillik yo'qolganidan keyin oʻqiladigan kechki namoz; bomdod namozi vaqti kirgungacha davom etadi. Xufton namozi to'rt rakat farz, ikki rakat sunnatdan iborat. Xufton namozining to'rt rakat farzi asr namozining farzi kabi o'qilib, faqat niyatda farq bo'ladi. Xuftonning ikki rakat sunnati ham yuqorida o'rganganimiz bomdod va shom namozlarining ikki rakat sunnatlari kabi bir xil tartibda o'qiladi. Bundan tashqari xufton namozi ōz ichiga 3 rakat vitr vojib namozini ham oladi. Ushbu vitr namozining 3-rakatida Fotiha va zam suralarni o'qigandan keyin "Qunut" duosi ōqiladi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/12'>Bizning kanal📢</a>""")

# Istixora namozi haqida ma'lumot
@dp.callback_query(F.data == "istixora")
async def istixora(callback: CallbackQuery):
    await callback.message.answer(text="""
Istixora (baʼzan istihora ham deyiladi; arabcha: الاستخارة) — ikki rakaatdan iborat namoz. Ushbu namozdan so'ng musulmon kishi Allohdan maʼlum bir masala boʻyicha toʻgʻri qaror qabul qilishda yordam berishini soʻraydi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/59'>Bizning kanal📢</a>""")

# Hojat namozi haqida ma'lumot
@dp.callback_query(F.data == "hojat")
async def hojat(callback: CallbackQuery):
    await callback.message.answer(text="""
Hojat namozining rakatlari borasida ixtilof qilingan. Molikiy va hanbaliylar nazdida, hojat namozi ikki rakatdir. Hanafiy ulamolar nazdida, hojat namozi to‘rt rakat o‘qiladi. Hanafiy mazhabimizdagi bir qavlda ikki rakat ham deyilgan. Bunga sabab shuki, hojat namozi haqida turli xil rivoyatlar kelgan. Ba’zi kitoblarimizda o‘n ikki rak’at ham deyilgan. Bizningcha, hojat namozining ikki rak’at ekanligi dalil jihatidan kuchlirog‘i bo‘lsa ajabmas. Vallohu a’lam!
Zero, hojat namozini ikki rakat o‘qish va unda qanday duo qilish haqidagi rivoyat Abdulloh ibn Abu Avvo va Anas ibn Molik roziyallohu anhumodan naql qilingan. Uni Imom Termiziy o‘zlarining mashhur hadis to‘plamlarida rivoyat qilib keltirganlar. Boshqa rivoyatlarning esa ayrim fiqhiy kitoblarda mazmuni zikr qilingan bo‘lsada, ammo roviysi va qaysi hadis to‘plamida keltirilganligiga ishora qilinmagan.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/60'>Bizning kanal📢</a>""")


#--------------------------------------------------------------------------------------------------------
# Ayollar uchun Namoz o'qishni o'rganish bo'limi

#-----------------------------------------------------------------------------------------------------------
""" Ayollar uchun Namoz o'qishni o'rganish """
#-----------------------------------------------------------------------------------------------------------

# "ayol_namoz" tugmasi uchun handler
@dp.callback_query(F.data == "ayol_namoz")
async def ayol_namoz(callback: CallbackQuery):
    await callback.message.answer("Tanlang", reply_markup=admin_keyboard.ayol_namoz)

# Ayollar bomdod namozi haqida ma'lumot
@dp.callback_query(F.data == "bomdod2")
async def ayol_namoz(callback: CallbackQuery):
    await callback.message.answer(text="""
Bomdod (fors.) — erta tong payti, sahar va shu paytda oʻqiladigan namoz. Bomdod namozi kun chiqish taraf yorishganidan boshlab to kun chiqqunga qadar oʻqiladi. Bamdod namozi ikki rakat sunnat va ikki rakat farzdan iborat. Erta tongda oʻqilgan namozning savobi qolgan namozlarga qaraganda kattaroq boʻladi. Namoz oʻqish musulmonlarning farzi hisoblanadi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/2'>Bizning kanal📢</a>
""")

# Ayollar peshin namozi haqida ma'lumot
@dp.callback_query(F.data == "peshin2")
async def peshin(callback: CallbackQuery):
    await callback.message.answer(text="""
Peshin (fors.) — kunning yarmi oʻtgan payti va shu paytda oʻqiladigan namoz. Peshin namozi toʻrt rakat sunnat, toʻrt rakat farz va ikki rakat sunnatdan iborat. Peshin namozi Quyosh qiyomdan ogʻa boshlashidan to asr namozining vaqti kirguncha ado etiladi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/3'>Bizning kanal📢</a>
""")

# Ayollar asr namozi haqida ma'lumot
@dp.callback_query(F.data == "asr2")
async def asr(callback: CallbackQuery):
    await callback.message.answer(text="""
Asr namozi - Alloh taolo tomonidan farz qilingan namozlardan biri. Bu namozni musulmon kishi har kuni oʻqiydi. Ushbu namoz 4 rakat boʻlib faqat farzdan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/4'>Bizning kanal📢</a>
""")

# Ayollar shom namozi haqida ma'lumot
@dp.callback_query(F.data == "shom2")
async def shom(callback: CallbackQuery):
    await callback.message.answer(text="""
Shom — Quyosh botib, qorongʻulik boshlangan payt va shu vaqtda oʻqiladigan namoz. Shom namozi Quyosh botgandan boshlab, magʻrib ufqidagi qizil shafaqning koʻrinmay ketadigan vaqtigacha ado etiladi, uch rakat farz va ikki rakat sunnatdan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/6'>Bizning kanal📢</a>
""")

# Ayollar xufton namozi haqida ma'lumot
@dp.callback_query(F.data == "xufton2")
async def xufton(callback: CallbackQuery):
    await callback.message.answer(text="""
Xufton (fors. uxlash) — Quyosh botib ufqdagi qizillik yo'qolganidan keyin oʻqiladigan kechki namoz; bomdod namozi vaqti kirgungacha davom etadi. Xufton namozi to'rt rakat farz, ikki rakat sunnatdan iborat. Xufton namozining to'rt rakat farzi asr namozining farzi kabi o'qilib, faqat niyatda farq bo'ladi. Xuftonning ikki rakat sunnati ham yuqorida o'rganganimiz bomdod va shom namozlarining ikki rakat sunnatlari kabi bir xil tartibda o'qiladi. Bundan tashqari xufton namozi ōz ichiga 3 rakat vitr vojib namozini ham oladi. Ushbu vitr namozining 3-rakatida Fotiha va zam suralarni o'qigandan keyin "Qunut" duosi ōqiladi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/5'>Bizning kanal📢</a>
""")

# Ayollar bomdod namozi videosi haqida ma'lumot
@dp.callback_query(F.data == "videosi2")
async def videosi2(callback: CallbackQuery):
    await callback.message.answer(text="""
Bomdod namozi ikki rakat sunnat, ikki rakat farz – jami to'rt rakatdan iborat.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/2'>Bizning kanal📢</a>
""")

# Ayollar islomdagi o'rni haqida ma'lumot
@dp.callback_query(F.data == 'xolat')
async def xolat(callback: CallbackQuery):
    await callback.message.answer(text="""
Islom dini ayolning jamiyatdagi o'rni va ta'sirini juda katta baholaydi. Chunki ayollar islom ummatining tarbiyachilari hisoblanadi. Shu sababli ularning bilim olishi, ma'naviyati va ilm tarqatishi birinchi o'rindagi masalalardandir. Ayniqsa, ayollar uchun birinchi navbatda o'rganishi farz bo'lgan ilmlar - ularning o'zlariga xos bo'lgan masalalardir.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/7'>Bizning kanal📢</a>
""")

# Ayollar istixora namozi haqida ma'lumot
@dp.callback_query(F.data == "istixora2")
async def istixora(callback: CallbackQuery):
    await callback.message.answer(text="""
Istixora (baʼzan istihora ham deyiladi; arabcha: الاستخارة) — ikki rakaatdan iborat namoz. Ushbu namozdan so'ng musulmon kishi Allohdan maʼlum bir masala boʻyicha toʻgʻri qaror qabul qilishda yordam berishini soʻraydi.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/59'>Bizning kanal📢</a>
""")

# Ayollar hojat namozi haqida ma'lumot
@dp.callback_query(F.data == "hojat2")
async def hojat(callback: CallbackQuery):
    await callback.message.answer(text="""
Hojat namozining rakatlari borasida ixtilof qilingan. Molikiy va hanbaliylar nazdida, hojat namozi ikki rakatdir. Hanafiy ulamolar nazdida, hojat namozi to‘rt rakat o‘qiladi. Hanafiy mazhabimizdagi bir qavlda ikki rakat ham deyilgan. Bunga sabab shuki, hojat namozi haqida turli xil rivoyatlar kelgan. Ba’zi kitoblarimizda o‘n ikki rak’at ham deyilgan. Bizningcha, hojat namozining ikki rak’at ekanligi dalil jihatidan kuchlirog‘i bo‘lsa ajabmas. Vallohu a’lam!
Zero, hojat namozini ikki rakat o‘qish va unda qanday duo qilish haqidagi rivoyat Abdulloh ibn Abu Avfo va Anas ibn Molik roziyallohu anhumodan naql qilingan. Uni Imom Termiziy o‘zlarining mashhur hadis to‘plamlarida rivoyat qilib keltirganlar. Boshqa rivoyatlarning esa ayrim fiqhiy kitoblarda mazmuni zikr qilingan bo‘lsada, ammo roviysi va qaysi hadis to‘plamida keltirilganligiga ishora qilinmagan.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/61'>Bizning kanal📢</a>
""")

  
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

<a href='https://t.me/namoz_uqishni_urganish_Kanal/58'>Bizning kanal📢</a>
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

# Qo'shimcha suralar va duolar haqida ma'lumot berish
@dp.message(F.text == "QO'SHIMCHA SURALAR VA DUOLAR")
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

@dp.callback_query(F.data == 'duo')
async def valyuta_back(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
OYATAL KURSI

A'uzu billahi minash-shaytonir rojiym. Bismillahir rohmanir rohiym. Allohu la ilaha illa huval hayyul qoyyum...

<a href='https://t.me/namoz_uqishni_urganish_Kanal/23'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.qushimcha)

# Yasin surasi haqida
@dp.callback_query(F.data == 'yasin')
async def valyuta_back(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Yosin surasi fazilatlari to‘g‘risida ko‘p hadisi shariflar rivoyat qilingan. Ularda aytilishicha, kimda-kim bu surani ixlos bilan o‘qisa, hojati ravo bo‘ladi...

<a href='https://t.me/namoz_uqishni_urganish_Kanal/26'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.qushimcha)

# Mulk surasi haqida
@dp.callback_query(F.data == 'mulk')
async def valyuta_back(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Taborak (Mulk) surasi haqida hadislar: Abu Hurayra roziyallohu anhudan rivoyat qilingan. Nabiy sollallohu alayhi vasallam: “Qur’onda o‘ttiz oyatdan iborat bir sura bor. Kim uni o‘qisa, gunohlari kechirilgunicha shafoat qiladi...

<a href='https://t.me/namoz_uqishni_urganish_Kanal/27'>Bizning kanal📢</a>
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
Suraning oʻnga yaqin nomlari boʻlib, ulardan eng mashhuri „Fotiha“, yaʼni, „ochuvchi“...

<a href='https://t.me/namoz_uqishni_urganish_Kanal/50'>Bizning kanal📢</a>
""", reply_markup=admin_keyboard.qushimcha)


# Callbacklar uchun handlerlar
@dp.callback_query(F.data == 'kofirun')
async def kofirun_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Kofirun surasi (arabcha: سورة الكافرون, nomining maʼnosi — Kofirlar) — Qurʼonning 109-surasi. Makkiy suralardan biri, 6 oyatdan iborat. Bu sura Qurʼonning 603-sahifasida va 30-juzida joylashgan. 18-boʻlib nozil boʻlgan.                               
<a href='https://t.me/namoz_uqishni_urganish_Kanal/34'>Bizning kanal📢</a> 
""")
    await callback.message.answer(text="audio <a href='https://t.me/namoz_uqishni_urganish_Kanal/45'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'ixlos')
async def ixlos_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
“Ixlos” so‘zi aslida, arabcha so‘z bo‘lib, u “xolos bo‘lish”, “muxlis”, “xolis” degan ma’nolarni anglatadi. Bu haqda “O‘zbek tilining izohli lug‘ati”da: “Ixlos (arabcha) – samimiylik, ko‘ngli ochiqlik, berilganlik, muxlislik, e’tiqod, chin yurakdan, ishonch bilan berilish; astoydil muhabbat” deb izohlanadi.                         
<a href='https://t.me/namoz_uqishni_urganish_Kanal/35'>Bizning kanal📢</a> 
""")
    await callback.message.answer(text="audio <a href='https://t.me/namoz_uqishni_urganish_Kanal/44'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'falaq')
async def falaq_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
FALAQ SURASI:
Qul a’`uzu birobbil falaq. Min
sharri m`a xolaq. Va min sharri
g‘`osiqin iz`a vaqob.
Va min sharrin-naff`as`ati fil
‘uqod. Va min sharri h`asidin iz`a
hasad.                       
<a href='https://t.me/namoz_uqishni_urganish_Kanal/36'>Bizning kanal📢</a> 
""")
    await callback.message.answer(text=". <a href='https://t.me/namoz_uqishni_urganish_Kanal/43'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'nas')
async def nas_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Nos surasi (arabcha: سورة الناس, Odamlar) — Qurʼoni Karimning 114-chi surasi. Makkada nozil boʻlgan, 6 oyatdan iborat. 
<a href='https://t.me/namoz_uqishni_urganish_Kanal/37'>Bizning kanal📢</a> 
""")
    await callback.message.answer(text=". <a href='https://t.me/namoz_uqishni_urganish_Kanal/42'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

@dp.callback_query(F.data == 'nasr')
async def nasr_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="""
Nasr surasi (arabcha: سورة النصر, nomining maʼnosi — Yordam) — Qurʼonning 110-surasi. Madaniy suralardan biri, 3 oyatdan iborat. Bu sura Qurʼonning 603-sahifasida va 30-juzida joylashgan. 114-boʻlib nozil boʻlgan.
<a href='https://t.me/namoz_uqishni_urganish_Kanal/38'>Bizning kanal📢</a> 
""")
    await callback.message.answer(text=". <a href='https://t.me/namoz_uqishni_urganish_Kanal/41'>Bizning kanal📢</a>", reply_markup=admin_keyboard.qushimcha)

# Jamoat namozlari uchun handlerlar
@dp.message(F.text == "JAMOAT NAMOZLARI")
async def jamoat_namozlari_handler(message: Message):
    await message.answer("Jamoat namozi – savobi ulug‘ ibodat. Ibn Umar roziyallohu anhumodan rivoyat qilinadi. Rasululloh sollallohu alayhi vasallam: “Jamoat namozi yolg‘iz o‘qilgan namozdan yigirma yetti daraja afzaldir”, dedilar (Imom Buxoriy, Imom Muslim rivoyati)", reply_markup=admin_keyboard.jamoat)

@dp.callback_query(F.data == 'juma')
async def juma_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="<a href='https://t.me/namoz_uqishni_urganish_Kanal/57'>Bizning kanal 📢</a>")
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
    await callback.message.answer(text="Menyulardan birini tanlang", reply_markup=admin_keyboard.start_button)
    await callback.message.delete()

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
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    db = Database(path_to_db="main.db")
    db.create_table_users()
    # db.create_table_audios()
    await set_default_commands(bot)
    await dp.start_polling(bot)
    setup_middlewares(dispatcher=dp, bot=bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())