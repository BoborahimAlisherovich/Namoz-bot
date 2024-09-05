from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Admin uchun klaviatura
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


start_buttonnew = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="NAMOZ"),
        KeyboardButton(text="⌛️NAMOZ VAQTLARI⌛️") ],
        [KeyboardButton(text="TAHORAT"),
        KeyboardButton(text="G'USL") ],
       [KeyboardButton(text="SURALAR"),
        KeyboardButton(text="DUOLAR")],
        [KeyboardButton(text="QURON"),
        KeyboardButton(text="99 TA ISMLAR")],
         [KeyboardButton(text="40 FARZ"),
        KeyboardButton(text="IBODATI ISLOMIYA")],
        [KeyboardButton(text="SHAHODAT"),
        KeyboardButton(text="MAKKA ONLINE")],
         [KeyboardButton(text="IYMON"),
        KeyboardButton(text="HAJ")],
         [KeyboardButton(text="ZAKOT"),
        KeyboardButton(text="Ro'za")]

    ],
    resize_keyboard=True,
    one_time_keyboard=True
    
)


makka = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Efirga utish",url="https://www.youtube.com/watch?v=wkmIFbf_R_s")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="qaytish")],
    ]
)


# Tahorat bo'limi klaviaturasi
tahorati = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Ta'rif", callback_data="tarif")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="qaytish")],
    ]
)



# Qo'shimcha suralar va duolar
iymon = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Din va shariat nima?", callback_data="shariat"),
         InlineKeyboardButton(text="iymon nima?", callback_data="iymon_nima"),],
          [InlineKeyboardButton(text="Alloh taolaga iymon", callback_data="Allohga_iymon"),
         InlineKeyboardButton(text="Farishtalarga Iymon", callback_data="farishtalarga_iymon"),],
          [InlineKeyboardButton(text="Ilohiy kitoblarga iymon", callback_data="ilohiy_kitobga_iymon"),
         InlineKeyboardButton(text="Payg'ambarlarga iymon", callback_data="Payg'ambarlarga_iymon"),],
         [InlineKeyboardButton(text="Oxirat kuniga iymon", callback_data="oxirat_kuniga_iymon"),
         InlineKeyboardButton(text="O'limdan so'ng qayta tirilishga iymon", callback_data="O'limdan_sung_tirilish"),],
                  [InlineKeyboardButton(text="Aqida", callback_data="aqida"),
         InlineKeyboardButton(text="Ahli sunna val jamoa", callback_data="ahli_sunna_val_jmoa"),],
         [InlineKeyboardButton(text="Halol va harom",callback_data="halol_va_harom")] 
        ]
        )

iymon_orqaga_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="orqaga",callback_data="orqaga_button")]
    ]
)

ehromga_kirish_davomi = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Davomini uqish",callback_data="davomini_uqish_button")]
    ]
)



# Qo'shimcha suralar va duolar
qushimcha = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Fotiha surasi", callback_data="fotiha"),
        InlineKeyboardButton(text="Oyatal kursi", callback_data="oyat"),],
        [InlineKeyboardButton(text="Fil surasi", callback_data="fil_sura"),
         InlineKeyboardButton(text="Quraysh surasi", callback_data="quraysh_")],
         [InlineKeyboardButton(text="Ma'un surasi", callback_data="maun_surasi"),
         InlineKeyboardButton(text="Kavsar surasi", callback_data="kavsar_")],
          [InlineKeyboardButton(text="Kofirun surasi", callback_data="kofirun"),
         InlineKeyboardButton(text="Nasr surasi", callback_data="nasr_")],
           [InlineKeyboardButton(text="Masad surasi", callback_data="masad_surasi"),
         InlineKeyboardButton(text="Ixlos surasi", callback_data="ixlos")],
          [InlineKeyboardButton(text="Falaq", callback_data="falaq_"),
         InlineKeyboardButton(text="Nas surasi", callback_data="nas")],
         
    ])



duolar = InlineKeyboardMarkup(
    inline_keyboard=[
         [InlineKeyboardButton(text="Azondan keyin", callback_data="azondan_kiyinduo"),
          InlineKeyboardButton(text="Sano", callback_data="sano_duosi"),],
          [InlineKeyboardButton(text="Ruku'da turganda", callback_data="rukudan_turkanda"),
          InlineKeyboardButton(text="Ruku'dan qaytayotganda", callback_data="rukudan_qaytayotganda"),],
          [InlineKeyboardButton(text="Ruku'dan qaytib tik turganda", callback_data="rukudan_qaytib_turganda"),
          InlineKeyboardButton(text="Sajdada", callback_data="sajdada"),],
        [InlineKeyboardButton(text="Tashahhud", callback_data="tashahhud"),
          InlineKeyboardButton(text="Salovatlar", callback_data="salovatlar"),],
         [InlineKeyboardButton(text="Namozdan kiyin", callback_data="namozdan_kiyin"),
          InlineKeyboardButton(text="Qunut duosi", callback_data="qunut"),],
          [InlineKeyboardButton(text="Istixora namozi duosi", callback_data="istihora_namozi_duosi"),
          InlineKeyboardButton(text="Hojat namozi duosi", callback_data="hojat_namozi_duosi"),],
    ]
)

duolar_orqa_button = InlineKeyboardMarkup(
    inline_keyboard=[
       [ InlineKeyboardButton(text="Orqaga",callback_data="orqa_button_duolar"),]
    ]
)



# Tanlash bo'limi klaviaturasi
tanlash_ = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="ERKAKLAR UCHUN NAMOZ", callback_data="erkak_namozi")],
        [InlineKeyboardButton(text="AYOLLAR UCHUN NAMOZ", callback_data="ayol_namoz")],
        [InlineKeyboardButton(text="JAMOAT NAMOZLARI", callback_data="JAMOAT_namoz")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="qaytish")],
        
        
    ]
)



SURAH_NAMES = [
    ("Fotiha", "fotiha_quron"), ("Baqara", "baqara"), ("Oli Imron", "oli_imron"),
    ("Niso", "niso"), ("Moida", "moida"), ("An'om", "anom"), ("A'rof", "arof"),
    ("Anfol", "anfol"), ("Tavba", "tavba"), ("Yunus", "yunus"), ("Hud", "hud"),
    ("Yusuf", "yusuf"), ("Ro'd", "rod"), ("Ibrohim", "ibrohim"), ("Hijr", "hijr"),
    ("Nahl", "nahl"), ("Isro", "isro"), ("Kahf", "kahf"), ("Maryam", "maryam"),
    ("Toha", "toha"), ("Anbiyo", "anbiyo"), ("Haj", "haj"), ("Mu'minum", "muminum"),
    ("Nur", "Nur"), ("Furqon", "furqon"), ("Shuaro", "shuaro"), ("Naml", "naml"),
    ("Qasos", "qosos"), ("Ankabut", "ankobut"), ("Rum", "rum"), ("Luqmon", "luqmon"),
    ("Sajda", "sajda"), ("Ahzob", "ahzob"), ("Saba'", "saba"), ("Fotir", "fotir"),
    ("Yaasiyn", "yaasiyn"), ("Soffaat", "soffaat"), ("Sod", "sod"), ("Zumar", "zumar"),
    ("G'ofir", "gofir"), ("Fussilat", "fusilat"), ("Shuaro", "shuuro"), ("Zuxruf", "zuxrof"),
    ("Duxon", "duxon"), ("Josiya", "josiya"), ("Ahqof", "ahqof"), ("Muhammad", "Muhammad"),
    ("Fatx", "fatx"), ("hujurot", "hujurot"), ("Qof", "qof"), ("Zoriyat", "zoriyat"),
    ("Tur", "tur"), ("Najm", "najm"), ("Qamar", "qamar"), ("Ar-Rohman", "Ar_Rohman"),
    ("Voqi'a", "voqi'a"), ("Hadid", "hadid"), ("Mujodala", "mujodala"), ("Hashr", "hashr"),
    ("Mumtahana", "mumtahana"), ("Soof", "soof"), ("Juma", "juma_quron"),
    ("Munofiqun", "munofiqun"), ("Tag'abun", "tagabun"), ("Taloq", "taloq"),
    ("Tahrim", "tahrim"), ("Mulk", "mulk"), ("Qalam", "qalam"), ("Haaqqo", "haaqqo"),
    ("Ma'orij", "maorij"), ("Nuh", "nuh"), ("Jin", "jin"), ("Muzzammil", "muzzammil"),
    ("Muddassir", "muddassir"), ("Qiyaama", "qiyaama"), ("Inson", "inson"),
    ("Mursalaat", "mursalaat"), ("Naba'", "Naba'"), ("Nazi'aat", "naziaat"),
    ("Abasa", "abasa"), ("Takvir", "takvir"), ("Infitor", "infitor"),
    ("Mutoffiful", "mutoffiful"), ("Inshiqoq", "inshiqoq"), ("Buruj", "buruj"),
    ("Toriq", "toriq"), ("A'laa", "alaa"), ("G'oshiya", "goshiya"), ("Fajr", "fajr"),
    ("Balad", "balad"), ("Shams", "shams"), ("Layl", "layl"), ("Zuho", "zuho"),
    ("Sharh", "sharh"), ("Tiyn", "tiyn"), ("Alaq", "alaq"), ("Qadr", "qadr"),
    ("Bayyina", "bayyina"), ("Zalzala", "zalzala"), ("A'diyat", "adiyat"),
    ("Qori'a", "qoria"), ("Takaasur", "takaasur"), ("Asr", "asr_quron"),
    ("Humaza", "humaza"), ("Fiyl", "fiyl"), ("Quraysh", "quraysh"), ("Maa'uun", "maauun"),
    ("Kavsar", "kavsar"), ("Kaafirun", "kaafirun"), ("Nasr", "nasr"),
    ("Masad", "masad"), ("Ixlos", "ixlos"), ("Falaq", "falaq"), ("Nos", "nos_quron")
]

# Hudud tanlash klaviaturasi
hudud = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Toshkent"),
         KeyboardButton(text="Andijon"),
         KeyboardButton(text="Buxoro")],
        [KeyboardButton(text="Guliston"),
         KeyboardButton(text="Samarqand"),
         KeyboardButton(text="Namangan")],
        [KeyboardButton(text="Navoiy"),
         KeyboardButton(text="Jizzax"),
         KeyboardButton(text="Nukus")],
        [KeyboardButton(text="Qarshi"),
         KeyboardButton(text="Qoʻqon"),
         KeyboardButton(text="Xiva")],
        [KeyboardButton(text="Margʻilon")],
        [KeyboardButton(text="🏠 Bosh Menyu")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Hududingizni tanlang"
)

# Admin uchun oddiy klaviatura
Admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="qaytish")],
    ]
)

# Erkaklar uchun namoz bo'limi klaviaturasi
erkak_namoz = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Azon", callback_data="azon")],
        [InlineKeyboardButton(text="Bomdod nomozi", callback_data="bomdod")],
        [InlineKeyboardButton(text="Peshin nomozi", callback_data="peshin")],
        [InlineKeyboardButton(text="Asr nomozi", callback_data="asr")],
        [InlineKeyboardButton(text="Shom nomozi", callback_data="shom")],
        [InlineKeyboardButton(text="Xufton nomozi", callback_data="xufton")],
        [InlineKeyboardButton(text="Istixora nomozi", callback_data="istixora")],
        [InlineKeyboardButton(text="Hojat nomozi", callback_data="hojat")],
        [InlineKeyboardButton(text="Orqaga qaytish", callback_data="orqa_qaytish")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="qaytish")],
        
    ]
)

orqaga_qayt = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Orqaga",callback_data="orqaga_qaytamiz")]
    ]
)


# Ayollar uchun namoz bo'limi klaviaturasi
ayol_namoz = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Ayollarga xos xolatlar", callback_data="xolat")],
        [InlineKeyboardButton(text="Bomdod nomozi", callback_data="bomdod2")],
        [InlineKeyboardButton(text="Peshin nomozi", callback_data="peshin2")],
        [InlineKeyboardButton(text="Asr nomozi", callback_data="asr2")],
        [InlineKeyboardButton(text="Shom nomozi", callback_data="shom2")],
        [InlineKeyboardButton(text="Xufton nomozi", callback_data="xufton2")],
        [InlineKeyboardButton(text="Istixora nomozi", callback_data="istixora2")],
        [InlineKeyboardButton(text="Hojat nomozi", callback_data="hojat2")],
        [InlineKeyboardButton(text="Orqaga qaytish", callback_data="orqa_qaytish")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="qaytish")],
    ]
)

qiriq_farz  = InlineKeyboardMarkup(
    inline_keyboard=[
      [InlineKeyboardButton(text="Islomdagi 5 farz", callback_data="besh_farz")],  
      [InlineKeyboardButton(text="Iymondagi 7 farz", callback_data="yetti_farz")],
      [InlineKeyboardButton(text="Namozdagi 12 farz", callback_data="on_ikki_farz")],
      [InlineKeyboardButton(text="Tahoratdagi 4 farz", callback_data="tort_farz")],
      [InlineKeyboardButton(text="Tayammumning 4 farzi", callback_data="tayammum_turt_farz")],
      [InlineKeyboardButton(text="G'usldagi 3 farz", callback_data="uch_farz")],
      [InlineKeyboardButton(text="Amru-ma'ruf va naxiy-munkarda 2 farz", callback_data="amru_maruf")],
      [InlineKeyboardButton(text="Xayz va nifosda 2 farz", callback_data="ikki_farz")],
      [InlineKeyboardButton(text="Ilm izlshda 1 farz", callback_data="ikki_farz")],
      [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="qaytish")],
    ]
)


bu_uchun_orqaga  = InlineKeyboardMarkup(
    inline_keyboard=[
      [InlineKeyboardButton(text="orqaga", callback_data="orqaga_uchun_farz")],  
    ])
# Jamoat namozlari bo'limi klaviaturasi
jamoat = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="JUMA NAMOZI", callback_data="juma"),
         InlineKeyboardButton(text="QURBON HAYIT NAMOZI", callback_data="ied")],
        [InlineKeyboardButton(text="JANOZA NAMOZI", callback_data="janoza"),
         InlineKeyboardButton(text="TAROVIH NAMOZI", callback_data="tarovih")],
        [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="qaytish")],
    ]
)


qayt = InlineKeyboardMarkup(
    inline_keyboard=[
         [InlineKeyboardButton(text="🏠 Bosh Menyu", callback_data="qaytish")],
    ]
)



# Qo'shimcha suralar va duolar
haj = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Haj qanday ibodat", callback_data="qanday_ibodat"),
         InlineKeyboardButton(text="Hajning odoblari", callback_data="haj_odoblari")],
        [InlineKeyboardButton(text="Hajning nozik sirlari", callback_data="hajning_nozik_sirlari"),
         InlineKeyboardButton(text="haj safariga chiquvchiga tavsiyalar", callback_data="haj_tavsiya")],
        [InlineKeyboardButton(text="Haj ibodati turlari", callback_data="haj_ibodat_turlari"),
         InlineKeyboardButton(text="Hajning farz, vojib va sunnatlari", callback_data="hajning_farzi")],
        [InlineKeyboardButton(text="Ehromga kirish", callback_data="ehromga_kirish"),
         InlineKeyboardButton(text="Ehromdagi amallar va ularning kafforatlari", callback_data="ehromdagi_amallar")],
        [InlineKeyboardButton(text="Talbiya aytish", callback_data="talbiya_aytish"),
         InlineKeyboardButton(text="Harami sharifiga kirish", callback_data="harami_sharif")],
        [InlineKeyboardButton(text="Tavofni boshlash", callback_data="tavofni_boshlash"),
         InlineKeyboardButton(text="Safo va marva orasida sa'y qilish", callback_data="safo_va_marva")],
        [InlineKeyboardButton(text="Minoda turish", callback_data="minoda_turish"),
         InlineKeyboardButton(text="Arafoda turish", callback_data="arafoda_turish")],
        [InlineKeyboardButton(text="Muzdalifada bo'lish", callback_data="muzdalifada_bulish"),
         InlineKeyboardButton(text="Shaytonga tosh otish", callback_data="shaytonga_tosh_otish")],
        [InlineKeyboardButton(text="Tavofning turlari", callback_data="tavohning_turlari"),
         InlineKeyboardButton(text="Hajning besh kuni", callback_data="hajning_besh_kuni")],
         [InlineKeyboardButton(text="Badal haji", callback_data="badal_haji")],
    ]
)

haj_davom =InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="davomini uqish",callback_data="davomi_shaytonga_tosh_ot")]
    ]
)



# Qo'shimcha suralar va duolar
haj_ortga = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Orqaga", callback_data="haj_orqaga")]])

haj_davomi = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Davoni ko'rish",callback_data="davomi_haj")]
    ]
)

zakot = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Zakot nima",callback_data="zakot_nima"),],
         [InlineKeyboardButton(text="Zakotning fiqhiy hukmlari",callback_data="fiqh_hukumlari")],
          [InlineKeyboardButton(text="Chorva hayvonlaring zakoti",callback_data="chorvaning_zakoti"),],
        [InlineKeyboardButton(text="Naqt puldan olinadigan zakot",callback_data="naqtdan_olinadigan_zakot")],
                   [InlineKeyboardButton(text="Tijorat molidan qiymatini zakotga chiqarish",callback_data="tijorat_moli")],
         [InlineKeyboardButton(text="Tilla kumush buyimlaridan, idishlar va taqinchoqlar zakoti",callback_data="taqinchoqlar_zakoti")],
        [InlineKeyboardButton(text="Qimmatbaho toshlarning zakoti",callback_data="toshlar_zakoti"),],
         [InlineKeyboardButton(text="zakot olish mumkin bo'lganlar",callback_data="olishi_mumkinlar")],
          [InlineKeyboardButton(text="Zakot beruvchining vazifalari",callback_data="zakot_beruvchi")],
    ]
)

zakot_orqa_button = InlineKeyboardMarkup(
     inline_keyboard=[
         [InlineKeyboardButton(text="orqaga",callback_data="zakot_orqa_button")]
     ]
)

ruza = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Ro'za qanday ibodat?",callback_data="zuza_qanday_ibodat"),],
         [InlineKeyboardButton(text="Ro'zaning darajalari",callback_data="ruzaning_darajalari")],
          [InlineKeyboardButton(text="Ro'zaning shartlari",callback_data="ruzaning_shartlari"),],
        [InlineKeyboardButton(text="Ro'zaning turlari",callback_data="ruzaning_turlari")],
                   [InlineKeyboardButton(text="Ro'za tutishga harom bo'lgan kunlar",callback_data="ruza_tutishga_harom_kunlar")],
         [InlineKeyboardButton(text="Ro'za tutishga makruh bo'lgan kunlar",callback_data="ruza_tutishga_makruh_kunlar")],
        [InlineKeyboardButton(text="Ruzaning niyati",callback_data="ruzaning_niyati"),],
         [InlineKeyboardButton(text="Saharik va iftorlik",callback_data="saharlik_va_iftorlik")],
          [InlineKeyboardButton(text="Ro'zaning mustahablari",callback_data="ruzaning_mustahablari")],
           [InlineKeyboardButton(text="Ro'zani buzadigan narsalar",callback_data="ro'zani_buzadigan_amal")],
    ]
)


ruza_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="orqaga",callback_data="ruza_button_orqga"),],])