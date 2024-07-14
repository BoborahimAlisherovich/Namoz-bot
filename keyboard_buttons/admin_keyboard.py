from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# from aiogram.utils.keyboard import ReplyKeyboardBuilder
# from aiogram.fsm.state import State, StatesGroup

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton


admin_button = ReplyKeyboardMarkup(
    keyboard=[



        [
            KeyboardButton(text="Foydalanuvchilar soni"),
            KeyboardButton(text="Reklama yuborish"),
        ]
        
    ],
   resize_keyboard=True,
   input_field_placeholder="Menudan birini tanlang"
)


start_button = ReplyKeyboardMarkup(
    keyboard=[

         [KeyboardButton(text="TAHORAT"), ],
            [KeyboardButton(text="G'USL"), ],
            [KeyboardButton(text="Tayammum"), ],
        [KeyboardButton(text="🕋NOMOZ O'QISHNI O'RGANISH🤲"), ],
        [KeyboardButton(text="⌛️NAMOZ VAQTLARI⌛️"), ],
         [KeyboardButton(text="QO'SHIMCHA SURALAR VA DUOLAR"), ],
         [KeyboardButton(text="JAMOAT NAMOZLARI"), ],



       
        
           

    ],
 resize_keyboard=True, 
    input_field_placeholder="o'zingizga keraklisini tanlang"
)



tahorati = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Ta'rif", callback_data="tarif")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu",callback_data="qaytish")],
        
            
    ]
        
)

qushimcha = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Oyatal kursi", callback_data="oyat"),
        InlineKeyboardButton(text="Qunut duasi", callback_data="qunut")],
         [InlineKeyboardButton(text="Namozdan kiyingi dualar", callback_data="duo"),
        InlineKeyboardButton(text="Ya'siyn surasi", callback_data="yasin")],
         [InlineKeyboardButton(text="Voqea surasi", callback_data="voqea"),
        InlineKeyboardButton(text="Mulk(Taborak)", callback_data="mulk")],
         [InlineKeyboardButton(text="Sano", callback_data="sano"),
        InlineKeyboardButton(text="Fotiha surasi", callback_data="fotiha")],
         [InlineKeyboardButton(text="Fil surasi", callback_data="fil"),
        InlineKeyboardButton(text="Quraysh surasi", callback_data="quraysh")],
        [InlineKeyboardButton(text="Kavsar surasi", callback_data="kavsar"),
        InlineKeyboardButton(text="Kofirun surasi", callback_data="kofirun")],
         [InlineKeyboardButton(text="Ixlos surasi", callback_data="ixlos"),
        InlineKeyboardButton(text="falaq surasi", callback_data="falaq")],
         [InlineKeyboardButton(text="Nas surasi", callback_data="nas"),
        InlineKeyboardButton(text="Nasr surasi", callback_data="nasr")],
        
            
    ]
        
)


tanlash_ = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="ERKAKLAR UCHUN NAMOZ", callback_data="erkak_namozi")],
        [InlineKeyboardButton(text="AYOLLAR UCHUN NAMOZ", callback_data="ayol_namoz")]
        
            
    ]
        
)

hudud =ReplyKeyboardMarkup(
    keyboard = [
        
        [KeyboardButton(text = "Toshkеnt"),
          KeyboardButton(text="Andijon"),
         KeyboardButton(text = "Buxoro")],
         [
          KeyboardButton(text = "Guliston"),
       KeyboardButton(text = "Samarqand")   , 
         KeyboardButton(text = "Namangan")],
         
         [
             KeyboardButton(text = "Navoiy"),
         KeyboardButton(text = "Jizzax"),   
       KeyboardButton(text = "Nukus")  ],
     [
        KeyboardButton(text = "Qarshi"),   
       KeyboardButton(text = "Qoʻqon"),
         KeyboardButton(text = "Xiva")],  
         [KeyboardButton(text="Margʻilon")],
         [KeyboardButton(text="🏠 Bosh Menyu")]
      
       
   ],
    resize_keyboard=True, 
    input_field_placeholder="Hududingizni tanlang"
)



    
Admin = InlineKeyboardMarkup(
    inline_keyboard=[
    [InlineKeyboardButton(text="🏠 Bosh Menyu",callback_data="qaytish")],
    ]
)        

erkak_namoz = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Azon",callback_data="azon")],
        [InlineKeyboardButton(text="Bomdod nomozi",callback_data="bomdod")],
        [InlineKeyboardButton(text="Peshin nomozi",callback_data="peshin")],
        [InlineKeyboardButton(text="Asr nomozi",callback_data="asr")],
        [InlineKeyboardButton(text="Shom nomozi",callback_data="shom")],
        [InlineKeyboardButton(text="Xufton nomozi",callback_data="xufton")],
    ]
)

ayol_namoz = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Ayollarga xos xolatlar",callback_data="xolat")],
        [InlineKeyboardButton(text="Bomdod nomozi",callback_data="bomdod2")],
        [InlineKeyboardButton(text="Peshin nomozi",callback_data="peshin2")],
        [InlineKeyboardButton(text="Asr nomozi",callback_data="asr2")],
        [InlineKeyboardButton(text="Shom nomozi",callback_data="shom2")],
        [InlineKeyboardButton(text="Xufton nomozi",callback_data="xufton2")],
    ]
)


jamoat = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="JUMA NAMOZI",callback_data="juma"),
        InlineKeyboardButton(text="QURBON HAYIT NAMOZI",callback_data="ied")],
         [InlineKeyboardButton(text="JANOZA NAMOZI",callback_data="janoza"),
         InlineKeyboardButton(text="TAROVIH NAMOZI",callback_data="tarovih")],

       
    ]
)

