import requests
from bs4 import BeautifulSoup

mintaqalar = { "Toshkеnt":27, "Andijon":1, "Buxoro":4, "Guliston":5, "Samarqand":18, "Namangan":15, "Navoiy":14, "Jizzax":9, "Nukus":16, "Qarshi":25, "Qoʻqon":26, "Xiva":21, "Margʻilon":13 }

oylar = ["Yanvar", "Fevral", "Mart","Aprel" , "May" , "Iyun" , "Iyul" , "Avgust" ,"Sentyabr" ,"Oktyabr" ,"Noyabr" ,"Dekabr"]



import datetime

def vaqti(mintaqa):
    try:
        oy = datetime.date.today().month
        URL=f'https://islom.uz/vaqtlar/{mintaqa}/{oy}'
        page=requests.get(URL)
        soup=BeautifulSoup(page.content,'html.parser')
        contents = soup.find_all('tr',class_='p_day bugun')[0]
        content = list(contents.find_all('td'))
        bugungi_vaqt = [x.text for x in content]
        bugungi_vaqt.append(oylar[oy-1])

        return bugungi_vaqt
    except:
        pass
    
        

# a(vaqti(mintaqalar.get("Toshkеnt")))