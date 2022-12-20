from flask import Flask, render_template, url_for, request, redirect, json
from datetime import datetime
import os
import multiprocessing
import time
import requests
from more_itertools import chunked
import random
from tqdm import tqdm
import wordVec as wv
from functools import partial
import numpy as np

# 自身の名称を app という名前でインスタンス化する
app = Flask(__name__)

OPENBD_ENDPOINT = 'https://api.openbd.jp/v1/'
book = []

bookNum = 10000
count = 0


def get_coverage():
    isbnList = requests.get(OPENBD_ENDPOINT + 'coverage').json()
    ranList = random.sample(isbnList, bookNum)
    return ranList


def get_bibs(items) -> dict:
    return requests.post(OPENBD_ENDPOINT + 'get', data={'isbn': ','.join(items)}).json()

def make_list():
    book.clear()
    chunked_coverage = chunked(get_coverage(), 5000)
    p = multiprocessing.Pool(4)
    results = p.imap_unordered(get_bibs, chunked_coverage)
    
    for result in results:
        for bib in result:
            if bib is None:
                continue
            try:
                a = bib["onix"]["DescriptiveDetail"]["Audience"][0]["AudienceCodeValue"]
                b = bib["onix"]["DescriptiveDetail"]["Audience"][0]["AudienceCodeType"]
                if b == "22" and (a == "01" or a == "02" or a == "03"):
                    continue
                else:
                    book.append(bib['summary']['title'])
                if bib['summary']['cover']:
                    book.append(bib['summary']['cover'])
                else:
                    book.append(bib['summary']['isbn'])
            except KeyError:
                book.append(bib['summary']['title'])
                if bib['summary']['cover']:
                    book.append(bib['summary']['cover'])
                else:
                    book.append(bib['summary']['isbn'])

def run(text, n):
    v1 = wv.get_vector(book[n])
    v2 = wv.get_vector(text)
    v12 = wv.cos_sim(v1, v2)
    return v12

       

# index にアクセスされた場合の処理
@app.route('/', methods=['GET','POST'] )
def index():
    make_list()
    return render_template('index.html',
                            title = book, num = len(book)/2)

# /post にアクセスされ、GETもしくはPOSTメソッドでデータが送信された場合の処理
# @app.route('/reset', methods=['POST'])
# def re_index():
#     make_list()
#     return render_template(url_for('index'),
#                            title = book, num = len(book)/2)




@app.route('/input', methods=['POST'])
def input():
    text = request.form['text']

    with multiprocessing.Pool(processes=4) as pool:
       d = pool.map(partial(run, text), range(0,len(book),2))
    # for n in range(0,len(book),2):
    #     book[n]
    #     v1 = wv.get_vector(book[n])
    #     v2 = wv.get_vector(text)
    #     v12 = wv.cos_sim(v1, v2)
    #     data.append(v12)
        
    #     if max < data[len(data) - 1]:
    #         max = data[len(data) - 1]
    #         maxW = book[n]

    # print(max)
    # print(maxW)
    
    return json.dumps(d)



if __name__ == "__main__":
    app.debug = True  # デバッグモード有効化
    app.run(host="127.0.0.1", port=3000)