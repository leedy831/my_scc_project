from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from newspaper import Article
from datetime import datetime


app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbSpaProject

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/date', methods=['GET'])
def show_datetime():
    datetimes = db.datetimes.find_one({}, {'_id': False})
    return jsonify({'result': 'success', 'datetime': datetimes})


@app.route('/list', methods=['POST'])
def get_archives():
    db.archives.drop()

    section_receive = request.form['section_give']
    subsec_receive = request.form['subsec_give']
    year_receive = request.form['year_give']
    month_receive = request.form['month_give']

    url_fixed = 'https://www.avvenire.it/Archivio/'
    url_var = section_receive + '/' + subsec_receive + '/' + year_receive + '/' + month_receive
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

    return jsonify({'result': 'success'})


@app.route('/list', methods=['GET'])
def show_archives():
    archives = list(db.archives.find({}, {'_id': False}))
    return jsonify({'result': 'success', 'archives': archives})


@app.route('/edit', methods=['POST'])
def get_news():
    url_receive = request.form['url_give']
    type_receive = request.form['type_give']
    author_receive = request.form['author_give']
    date_receive = request.form['date_give']

    news = Article(url_receive)
    news.download()
    news.parse()

    news_title = news.title
    news_image = news.top_image
    news_description = news.meta_description

    if type_receive == "editorial":
        news_text = textifyNews(news.text)
    else:
        news_text = textifyNews(news.text)
        news_text = news_text[2:]

    news_contents = {
        "title": news_title,
        "author": author_receive,
        "date": date_receive,
        "description": news_description,
        "image": news_image,
        "text": news_text
    }

    db.mynews.insert_one(news_contents)

    return jsonify({'result': 'success'})


def textifyNews(text):
    news_text = []
    text_list = text.split("\n")
    for i in text_list:
        if i != '':
            news_text.append(i)
    return news_text


@app.route('/edit', methods=['GET'])
def show_news():
    mynews = db.mynews.find_one({}, {'_id': 0})

    return jsonify({'result': 'success', 'news': mynews})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
