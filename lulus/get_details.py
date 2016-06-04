#!/usr/bin/env python
# coding=utf-8

import requests
import time
import json
from bs4 import BeautifulSoup
from multiprocessing import Pool
from db_conn import CollectionQueue, CollectionHistory, Goods, session, headers, create_session, \
    request_strong, GoodsFilter, Filter, FilterGroup
from sqlalchemy import create_engine, or_, and_, not_, distinct
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
       .filter(CollectionQueue.site_name == "Lulus").limit(20000).all()

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
        soup = BeautifulSoup(html_text)
        price = soup.select("div.price")[0].text
        # print price
        price = price.replace("$", '').strip()
        # print price
        price = decimal_price(price)
        print price
        img_1 = soup.find('div', id='product-slider').find('ul', id='product-images-slider').find('img')['src']
        # img_1= soup.find('div', id='product-slider').find('ul', id='product-images-slider').findAll('img')
        print img_1
        # img_1= img_1.attrs['src']
        # print type(img_list_1)
        # img_list_2 = img_list_1[0]
        # print img_list_2
        # img_list = soup.findAll('ul', id='product-images-slider')
        # img_list_aa = img_list[0].findall('li')
        # print img_list_aa
        # img_list = soup.select("ul")
        # print img_list
        img_src = []
        # for p in img_list:
        #     f = p.findall('src')
        #     print f

        #     # p = p.attrs.get('src')
        #     # print p
        #     for ik in p:
        #         print("ik ==> %s" %ik)
        #         src = ik.attrs.get('src')
        #         img_src.append(src)
        #         print img_src


            # ig = p.attrs.get('src')
            # print ig
        # img1 = img_list.attrs.get('src')
        # print img1
        # print img_list
        # print price
        name = soup.select("h1.product-title")[0].text  # print name
        # print name
        # print url
        color = None
        try:
            color = soup.select("li.color-name")[0].text
            color = color.replace("Color:", '').strip().lower()
            print color
        except (IndexError):
            pass
        # material_content = ''
        # des = soup.select("div.description")
        # material = soup.select("ul.bullets")
        # # print material
        # for m in material:
        #     material_content += m.text.strip()
        #     material_content_arr = material_content.lower().split()
        # for k, content in enumerate(material_content_arr):
        #     if '%' in content:
        #         if len(material_content_arr) >= k + 1:
        #             need_str = material_content_arr[k + 1].strip('.')
        #             print need_str     # get the material

        #
        # img1 = img_src[0]  # first pic to show
        # print img1
        # img2 = img_src[11]
        # img3 = img_src[12]
        # img4 = img_src[13]
        if color:
            color = get_color(color)
            print color
        else:
            pass
        down_img_url = download_local(img_1, 'go')

        goods = Goods()
        goods.goods_name = name
        goods.goods_price = price
        goods.add_time = int(time.time())
        goods.brands_name = site_name
        goods.img_url = down_img_url
        goods.rank = rank
        goods.status = 1
        goods.goods_url = url_dic.get('url', '')
        goods.details_img1 = img_1
        # goods.details_img2 = img2
        # goods.details_img3 = img3
        # goods.details_img4 = img4

        session.add(goods)
        session.commit()

        filter_color = None
        if color:
            filter_color = session.query(Filter).filter(Filter.name == color) \
                .filter(Filter.fg_id == filter_group_dic.get('color')).first()
        print filter_color

        if filter_color:
            color_goods_filter = GoodsFilter()
            color_goods_filter.goods_id = goods.goods_id
            color_goods_filter.filter_id = filter_color.filter_id
            color_goods_filter.filter_name = filter_color.name
            color_goods_filter.fg_id = filter_color.fg_id
            color_goods_filter.filter_group_name = 'color'
            session.add(color_goods_filter)

        curr_time = int(time.time())
        cq_info = session.query(CollectionQueue).filter(CollectionQueue.cq_id == cq_id).first()
        if cq_info:
            cq_info.goods_id = goods.goods_id
            cq_info.is_collected = 1
            cq_info.collected_time = curr_time

        ch = CollectionHistory()
        ch.goods_id =goods.goods_id
        ch.goods_price = price
        ch.rank = rank
        ch.collected_time = curr_time
        session.add(ch)

        session.commit()
        session.close()

def get_color(color_str):
    color_list = ['dusty blue', 'gold', 'camel', 'sangria', 'deep taupe', 'sage', 'yellow',
                  'azalea', 'light yellow', 'rose', 'black', 'matte gold', 'orange', 'flamingo pink',
                  'brown', 'turquoise', 'aubergine', 'seafoam', 'safari', 'silver', 'stone blue',
                  'nude', 'miami pink', 'teal', 'antique silver', 'antique gold', 'neon pink',
                  'peony', 'mauve', 'jade', 'lavender', 'bubble gum', 'violet', 'navy', 'orchid',
                  'blue', 'light brown', 'purple', 'antic gold', 'light rose', 'daquiri', 'burgundy',
                  'champagne', 'red', 'pink pearl', 'fuchsia purple', 'matte black', 'b.silver',
                  'rose gold', 'baby pink', 'bronze', 'gunmetal', 'fiery red', 'coral', 'hot pink',
                  'aqua', 'oatmeal', 'beige', 'cherry', 'blush', 'copper', 'fuchsia', 'matte silver',
                  'island mango', 'tigerlily', 'seashell', 'light pink', 'b.gold', 'periwinkle',
                  'baby blue', 'white', 'coral pink', 'ivory', 'tangerine', 'brick', 'multi',
                  'peachy cheeks', 'apricot', 'light grey', 'grey', 'crystal', 'light green',
                  'plum', 'rust', 'taupe', 'neon yellow', 'antic silver', 'berry sorbet',
                  'sophisticate', 'light blue', 'mint', 'tan', 'cream', 'pink', 'rainbow',
                  'peach', 'neon orange', 'berry', 'mustard', 'blue print', 'salmon',
                  'hunter green', 'dark grey', 'tomato', 'natural', 'antic.g', 'pink chiffon',
                  'clear', 'green', 'dusty pink', 'wine']

    for color in color_list:
        if color in color_str:
            return color
    return ''

def decimal_price(price_info):
    price = 0.0
    try:
        price = Decimal(price_info)
    except:
        pass
    return price

if __name__ == '__main__':
    get_queue()
    for i in url_list:
        get_url(i)
