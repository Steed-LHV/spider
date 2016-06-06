#!/usr/bin/env python
# coding=utf-8

import requests
import time
import httplib
httplib._MAXHEADERS = 1000
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
        print url

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
        material = soup.find("div", {"class": "product-details__content"}) \
            .find("ul", {"class": "product-details__list u-margin-l--none"}).findAll("li")[0].text.split()
        # js-tabs__content js-tabs__content-active product-details__description
        print material
        # print material
        count = []
        for index1, p in enumerate(material):
            # print index1
            for index2, q in enumerate(p):
                if q == '%':
                    count.append(index1)
                    # print count
        if len(count) == 0:
            if "blend" in material:
                material = material[0]
            material == material
            print material
        else:
            material = material[count[0] + 1]
            material1 = []
            i = 0
            for index, p in enumerate(material):
                i = i + 1
                material1.append(p)
                # material= "".join(material1)
                if "L" in material1:
                    material1 = material1[0:i - 1]
                    material = "".join(material1)
                    print material
                if "C" in material1:
                    material1 = material1[0:i - 1]
                    material = "".join(material1).lower()
                    # print material
            print material

        color = get_color(color)
        material = get_material(material)

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
        goods.img_url = down_img_url
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
        # session.close()

# add filter
    filter_color = None
    if color:
        filter_color = session.query(Filter).filter(Filter.name == color)\
                .filter(Filter.fg_id == filter_group_dic.get('color')).first()
    print filter_color

    filter_material = None
    if material:
        filter_material = session.query(Filter).filter(Filter.name == material). \
            filter(Filter.fg_id == filter_group_dic.get('material')).first()
    print filter_material

    if filter_color:
        color_goods_filter = GoodsFilter()
        color_goods_filter.goods_id = goods.goods_id
        color_goods_filter.filter_id = filter_color.filter_id
        color_goods_filter.filter_name = filter_color.name
        color_goods_filter.fg_id = filter_color.fg_id
        color_goods_filter.filter_group_name = 'color'
        session.add(color_goods_filter)

    if filter_material:
        material_goods_filter = GoodsFilter()
        material_goods_filter.goods_id = goods.goods_id
        material_goods_filter.filter_id = filter_material.filter_id
        material_goods_filter.fg_id = filter_material.fg_id
        material_goods_filter.filter_name = filter_material.name
        material_goods_filter.filter_group_name = 'material'
        session.add(material_goods_filter)

    curr_time = int(time.time())
    cq_info = session.query(CollectionQueue).filter(CollectionQueue.cq_id == cq_id).first()
    if cq_info:
        cq_info.goods_id = goods.goods_id
        cq_info.is_collected = 1
        cq_info.plan_time = curr_time
        cq_info.collected_time = curr_time
    ch = CollectionHistory()
    ch.goods_id = goods.goods_id
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


def get_material(material_str):
    material_list =['Olefin', 'polyester', 'stainless', 'polyurethane', 'brass', 'gold', 'stainless',
                     'PVC', 'acrylic', 'semiprecious', 'zincChain', 'sterling',
                     'SBR','poly',
                     'TPR',
                     'TPU',
                     'acrylic',
                     'cotton',
                     'elastane',
                     'leather',
                     'linen',
                     'lyocell',
                     'metallic',
                     'modal',
                     'nylon', 'polypropylene', 'brassapprox', 'gold', 'copper',
                     'polyesterhand', 'silverchain', 'pvc', 'paper', 'spandex', 'rayon', 'cotton',
                     'genuine', 'crystal', 'semiprecious', 'stainless', 'other', 'acrylic',
                     'polyesterlength', 'sterling', 'brassband', 'polyurethane', 'zincband', 'silicone',
                     'polyestermade', 'glass', 'brass', 'leather', 'zincwrist', 'metal',
                     'goldfilledchain', 'zincchain', 'suede', 'goldchain', 'nylon','pigskin',
                     'nylonhand', 'spandex', 'nylonpolyamide', 'regenerated', 'cottonhand', 'acrylicdry',
                     'polyurethanemade', 'pvc', 'cottonmachine', 'polyesterhand', 'spandexhand', 'rayon',
                     'cotton', 'olefinmade', 'tprmade', 'modacrylic', 'genuine', 'woolmachine', 'linen',
                     'viscose', 'spandexdry', 'rayonmachine', 'metallic', 'rubber', 'spandexmachine',
                     'other', 'polyesterdry', 'olefin', 'cottonmade', 'acrylic', 'novasuede', 'sbr', 'acrylics',
                     'outsole', 'polyurethane', 'acrylichand', 'polyestermade', 'cottonspot', 'polyethylene',
                     'spandexelastanehand', 'rayonhand', 'rayonsize', 'rabbit', 'mohair', 'jute', 'polyester',
                     'wool', 'leather', 'eva', 'viscosehand', 'viscosemachine', 'polyesterspot', 'rubbermade',
                     'woolhand', 'polyestermachine', 'tpu', 'tpr', 'modal', 'nylon'
                     'nylonapprox','other',
                     'polyurethane',
                     'ramie',
                     'rayon',
                     'rubber',
                     'spandex',
                     'viscose',
                     'wool']
    for material in material_list:
        if material in material_str:
            return material

    return ''

if __name__== '__main__':
    get_queue()
    for i in url_list:
        get_url(i)

