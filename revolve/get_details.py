#!/usr/bin/env python
# coding=utf-8

import requests
import time
import json
from bs4 import BeautifulSoup
from multiprocessing import Pool
from db_conn import CollectionQueue, CollectionHistory, Goods, session, headers, create_session, \
    request_strong, GoodsFilter, Filter, FilterGroup
    # from sqlalchemy import create_engine, or_, and_, not_, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import Table, Column, Integer, String, Float, MetaData, ForeignKey, Text
from aladin.helpers import get_count, toint
from aladin.utils.date import format_timestamp
from decimal import Decimal
from down_img import download_local
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from aladin.helpers import toint

filter_group_dic = {'color': 4,
                    'category': 11, 'secondary_category': 12, 'sub_category': 13,
                    'occasions': 18, 'silhouette': 19, 'decoration': 20, 'neckline': 21, 'sleeve': 22, 'patterns': 24,
                    'material': 25, 'length_info': 26
                    }

s = requests.session()
queue_info = 0
url_list = []

def get_queue():
    cq_list = session.query(CollectionQueue).filter(CollectionQueue.is_collected == 0).filter(CollectionQueue.goods_id == 0) \
       .filter(CollectionQueue.site_name == "Revolve").limit(20000).all()

    for cq in cq_list:
        dic = {
            'url': cq.url,
            'img_url': cq.img_url,
            'rank': cq.rank,
            'site_name': cq.site_name,
            'category': cq.category,
            'secondary_category': cq.secondary_category,
            'cq_id': cq.cq_id
        }
        # print cq
        url_list.append(dic)
        # print url_list
    session.close()

def get_url(url_dic):
    url = url_dic.get('url')
    # print url
    img_url = url_dic.get('img_url')
    goods_id = url_dic.get('goods_id', 0)
    rank = url_dic.get('rank', 0)
    site_name = url_dic.get('site_name', '')
    cq_id = url_dic.get('cq_id', '')

    try:
        r = requests.get(url, headers=headers)
    except Exception, e:
        print e
        print("[Get Details Error] url%s" % url)
        return
    if r.status_code == 200:
        html_text = r.text
        # print html_text
        soup = BeautifulSoup(html_text,"html.parser")
        # print url

        price = 0.0
        try:
            price = soup.find("div",{"class":"prices prices--md block block--lg"}).find("span",{"class":"prices__retail"}).text
            price = price.replace("$", '').strip()
            # print price
        except (AttributeError):
            pass
        color = soup.find("span",{"class":"u-font-primary u-uppercase u-margin-l--md selectedColor"}).text
        # print color

        img_url = []
        img = soup.find("div",{"id":"js-primary-slideshow__pager"}).findAll("a",{"class":"js-primary-slideshow__pager-thumb slideshow__pager-thumb"})
        for index, p in enumerate(img):
            img = p.attrs["data-zoom-image"]
            img_url.append(img)
        img1 = img_url[0]
        img2 = img_url[1]
        img3 = img_url[2]
        # img4 = img_url[3]
        print img1
        # print img_url

        name = soup.find("div",{"class":"product-titles"}).find("h1",{"class":"product-titles__name product-titles__name--long u-margin-b--none u-margin-t--lg"}).text.strip()
        print name

        down_img_url = download_local(img1, 'go')



        goods = Goods()
        goods.goods_name = name
        goods.add_time = int(time.time())
        goods.goods_name = name
        goods.brands_name = site_name
        goods.rank = rank
        goods.goods_url = url_dic.get('url', '')
        goods.goods_price = price
        goods.details_img1 = img1
        goods.details_img2 = img2
        goods.details_img3 = img3
        # goods.details_img4 = img4
        goods.category = url_dic.get('category', '')
        goods.secondary_category = url_dic.get('secondary_category', '')
        goods.img_url_down = down_img_url
        session.add(goods)
        session.commit()

        curr_time = int(time.time())
        cq_info = session.query(CollectionQueue).filter(CollectionQueue.cq_id == cq_id).first()
        if cq_info:
            cq_info.goods_id = goods.goods_id
            cq_info.is_collected = 1
            cq_info.collected_time = curr_time

        ch = CollectionHistory()
        ch.goods_id = goods.goods_id
        ch.goods_price = price
        ch.rank = rank
        ch.collected_time = curr_time
        session.add(ch)

        session.commit()
        session.close()


if __name__== '__main__':
    get_queue()
    for i in url_list:
        get_url(i)

