from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from newspaper import Article
from selenium import webdriver
import time

app = Flask(__name__)

# client = MongoClient('mongodb://test:test@localhost',27017)
client = MongoClient('localhost', 27017)
db = client.dbSpaProject_test

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/init', methods=['GET'])
def show_init_data():
    init_dates = db.datetimes.find_one({}, {'_id': False})
    return jsonify({'result': 'success', 'datetime': init_dates})


@app.route('/list', methods=['POST'])
def get_archives():
    db.myarchives.drop()

    sec_receive = request.form['sec_give']
    subsec_receive = request.form['subsec_give']
    year_receive = request.form['year_give']
    month_receive = request.form['month_give']

    arcs = list(db.archives.find({"section": sec_receive, "sub_section": subsec_receive, "year": year_receive, "month": month_receive}, {'_id': False}))

    for arc in arcs:
        db.myarchives.insert_one(arc)

    return jsonify({'result': 'success'})

@app.route('/list', methods=['GET'])
def show_archives():
    my_archives = list(db.myarchives.find({}, {'_id': False}))
    return jsonify({'result': 'success', 'archives': my_archives})


@app.route('/news', methods=['POST'])
def get_news():
    db.mynews.drop()

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

@app.route('/news', methods=['GET'])
def show_news():
    mynews = db.mynews.find_one({}, {'_id': False})

    return jsonify({'result': 'success', 'news': mynews})

@app.route('/newsedit')
def news_edit():
    return render_template("edit.html")


@app.route('/translate', methods=["POST"])
def get_translate():
    db.mytrans.drop()

    title = db.mynews.find_one({}, {"title": 1})
    des = db.mynews.find_one({}, {"description": 1})
    txts = db.mynews.find_one({}, {"text": 1})

    title = title['title']
    des = des['description']
    txts = list(txts['text'])

    kakao = kakao_translate(title, des, txts)

    db.mytrans.insert_one(kakao)

    k = db.mytrans.find_one({"translator": "kakao"}, {'_id': False})

    return jsonify({'result': 'success', 'kakao': k})

def kakao_translate(title, des, txts):
    url = "https://translate.kakao.com/translator/translate.json"

    headers = {
        "Referer": "https://translate.kakao.com/",
        "User-Agent": "Mozilla/5.0"
    }

    langs = ["ko", "en"]
    k_title = [title]
    k_des = [des]
    k_txts = []

    # title
    for lang in langs:
        data = {
            "queryLanguage": "it",
            "resultLanguage": lang,
            "q": title
        }

        resp = requests.post(url, headers=headers, data=data)
        data = resp.json()

        output = data['result']['output'][0]
        k_title.append(" ".join(output))

    # description
    for lang in langs:
        data = {
            "queryLanguage": "it",
            "resultLanguage": lang,
            "q": des
        }

        resp = requests.post(url, headers=headers, data=data)
        data = resp.json()

        output = data['result']['output'][0]
        k_des.append(" ".join(output))

    # texts
    for txt in txts:
        a = [txt]
        for lang in langs:
            data = {
                "queryLanguage": "it",
                "resultLanguage": lang,
                "q": txt
            }

            resp = requests.post(url, headers=headers, data=data)
            data = resp.json()

            output = data['result']['output'][0]
            a.append(" ".join(output))
        k_txts.append(a)

    result = {
        'translator': 'kakao',
        'title': k_title,
        'description': k_des,
        'texts': k_txts
    }

    return result

@app.route('/translate', methods=["GET"])
def show_translate():
    k = db.mytrans.find_one({"translator": "kakao"}, {'_id': False})
    return jsonify({'result': 'success', 'kakao': k})

@app.route('/translatetexts', methods=["POST"])
def get_and_show_trans_texts():
    index_receive = request.form['index_give']

    index = int(index_receive)

    k = db.mytrans.find_one({"translator": "kakao"}, {'_id': False})
    k_text = {
        'text': k["texts"][index]
    }

    db.mytranstxt.drop()
    db.mytranstxt.insert_one(k_text)

    result = db.mytranstxt.find_one({}, {'_id': False})

    return jsonify({'result': 'success', 'kakao_text': result})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
