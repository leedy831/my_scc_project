import requests
from bs4 import BeautifulSoup
from newspaper import Article
from pymongo import MongoClient
from datetime import datetime

client = MongoClient('localhost', 27017)
db = client.dbSpaProject


def insert_init_archive():
    db.archives.drop()
    section = "agora"
    sub_sec = "arte"
    year = str(datetime.today().year)
    month = str(datetime.today().month)

    url_fixed = 'https://www.avvenire.it/Archivio/'
    url_var = section + '/' + sub_sec + '/' + year + '/' + month
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
            "title_html": news_title,
            "author": news_author,
            "date": news_date,
            "type": news_type,
            "url": news_url
        }
        db.archives.insert_one(archive_contents)


def insert_init_datetime():
    db.datetimes.drop()
    year = str(datetime.today().year)
    month = str(datetime.today().month)
    year_list = []
    num = datetime.today().year - 9
    for i in range(10):
        year_list.append(str(num))
        num += 1

    datetimes = {
        "cur_year": year,
        "year_list": year_list,
        "cur_month": month,
    }

    db.datetimes.insert_one(datetimes)

insert_init_archive()
insert_init_datetime()


