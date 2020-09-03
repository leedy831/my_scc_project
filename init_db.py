import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

from selenium import webdriver
import time

client = MongoClient('mongodb://test:test@localhost',27017)
db = client.dbSpaProject

def insert_init_datetime():
    db.datetimes.drop()
    year = str(datetime.today().year)
    month = str(datetime.today().month)
    year_list = []
    anno = datetime.today().year - 4
    for i in range(5):
        year_list.append(str(anno))
        anno += 1
    month_list = []
    mese = 1
    for i in range(12):
        month_list.append(str(mese))
        mese += 1

    datetimes = {
        "cur_year": year,
        "year_list": year_list,
        "cur_month": month,
        "month_list": month_list
    }

    db.datetimes.insert_one(datetimes)


def insert_init_archives(sections, year_list, month_list):
    db.archives.drop()
    for section in sections:
        sub_secs = sections[section]
        for sub_sec in sub_secs:
            for year in year_list:
                for month in month_list:
                    my_sec = section
                    my_subsec = sub_sec
                    my_year = year
                    my_month = month
                    create_archives(my_sec, my_subsec, my_year, my_month)


def create_archives(sec, sub_sec, yr, mth):
    section = sec
    sub_section = sub_sec
    year = yr
    month = mth

    url_fixed = 'https://www.avvenire.it/Archivio/'
    url_var = section + '/' + sub_section + '/' + year + '/' + month
    archive_url = url_fixed + url_var

    url_receive = archive_url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    archives = soup.select('#bodyBlock_bodyColumn > div.archivio > div > div > div')

    for archive in archives:
        news_title = str(archive.select_one('h1'))[4:-5]
        news_author = archive.select_one('p.author').text
        news_date = archive.select_one('p.rDate').text.strip()
        news_type = archive.select_one('div')['class'][2]
        news_href = archive.select_one('a')['href']
        news_url = "https://www.avvenire.it/" + news_href

        archive_contents = {
            "section": section,
            "sub_section": sub_section,
            "year": year,
            "month": month,
            "title_html": news_title,
            "author": news_author,
            "date": news_date,
            "type": news_type,
            "url": news_url
        }
        db.archives.insert_one(archive_contents)


insert_init_datetime()

sections = {
    "agora": ["arte", "cultura", "scienza-e-tecnologia", "spettacoli", "sport"],
    "attualita": ["azzardo", "caporalato", "carceri", "caritas", "infortuni-sul-lavoro", "legalita", "migranti", "politica", "scuola", "terra-dei-fuochi"],
    "chiesa": ["benedetto-xvi", "cei", "documenti-cei", "ecumenismo", "giovani", "giubileo", "gmg", "lotta-agli-abusi", "santi-e-beati"],
    "economia": ["bes", "lavoro", "motori", "risparmio", "sviluppo-felice", "terzo-settore"],
    "europa": [""],
    "famiglia-e-vita": ["aborto", "fecondazione-assistita", "fine-vita", "gender", "unioni-civili", "utero-in-affitto"],
    "mondo": ["africa", "america-latina", "asia", "asia-bibi", "cristiani-perseguitati", "iraq-e-siria", "terrorismo"],
    "papa": ["commenti", "le-parole", "santa-marta", "viaggi"]
}

my_date = db.datetimes.find_one({}, {'_id': False})
year_list = my_date["year_list"]
month_list = my_date["month_list"]

insert_init_archives(sections, year_list, month_list)





