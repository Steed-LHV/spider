#!/usr/bin/env python
#coding=utf-8

from sqlalchemy import create_engine, or_, and_, not_, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import Table, Column, Integer, String, Float,MetaData, ForeignKey, Text
from decimal import Decimal
import requests, time

# DB_CONNECT_STRING = 'mysql://root:@localhost/Reptile?charset=utf8'
DB_CONNECT_STRING = 'mysql://root:@10.10.0.219/go?charset=utf8'
# DB_CONNECT_STRING = 'mysql://root:@10.10.0.219/Reptile?charset=utf8'

# DB_CONNECT_STRING = 'mysql://go:go@123@zzkko.cqrxa4hpcscy.us-west-1.rds.amazonaws.com/go?charset=utf8'

Base        = declarative_base()
engine      = create_engine(DB_CONNECT_STRING, echo=False)
DB_Session  = sessionmaker(bind=engine)
session = DB_Session()
session._model_changes = {}


headers = {
    'accept-encoding': "gzip, deflate, sdch",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
    'accept-language': "en-US,en;q=0.8",
    'Cookie': '_isuid=E3B9F20D-DDDA-4DED-87CB-0B7B42349B4A; _rfkckid=5hb5umvtdy621qvb-1463555754643; GSIDPuJr8IyoDRkn=2296cb09-cf59-47f0-a82d-c9e284edcf42; wtid=ckeb3hdkodefldtibar0o22rf6ov374645gge0sp05odl46ob930; SESSION_SERVER=SER03_INSTANCE02; __rutmc=3961389; gate=1; _ga=GA1.2.697591709.1463555754; _gat=1; __utmt=1; __utma=3961389.697591709.1463555754.1463555754.1463555754.1; __utmb=3961389.1.10.1463709811; __utmc=3961389; __utmz=3961389.1463555754.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); STSD397067=0; STSID397067=bddda0bd-981e-4d15-9869-27975e99b4bc; __zlcmid=ajfYw6Fz0UZRLb; __btr_id=bc157025-d286-471d-b8bc-520cdb06305a; __rutmb=3961389; __rutma=3961389-7w-74-4b-yw-7jnpx9jfq2bd91p2nkdb-1463555754643.1463706348493.1463709819968.4.12.1; __rcmp=n%3D_gc%2Cf%3Dgc%2Cs%3D1%2Cc%3D1051%2Ctr%3D100%2Crn%3D752%2Cts%3D20160518.0713%2Cd%3Dpc%3Bn%3Drw1%2Cf%3Drw%2Cs%3D1%2Cc%3D747%2Ct%3D20151106.2331%3Bn%3Dsb1%2Cf%3Dsb%2Cs%3D1%2Cc%3D750%2Ct%3D20151106.2332; __utma=3961389.697591709.1463555754.1463555754.1463555754.1; __utmb=3961389.2.9.1463709820040; __utmc=3961389; __utmz=3961389.1463555754.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __rpck=%7B%22pro%22%3A%22direct%22%2C%22bt%22%3A%7B%220%22%3Atrue%2C%221%22%3A0%2C%222%22%3Anull%2C%223%22%3A1%7D%2C%22C%22%3A%7B%7D%2C%22csp%22%3A%7B%22b%22%3A0%2C%22t%22%3A0%2C%22sp%22%3A0%2C%22c%22%3A0%7D%2C%22bfiv%22%3A%5B%22wkjbyxondo6t%22%2C%22LNX%2021%2C0%2C0%2C216%22%5D%2C%22bfif%22%3A%228rc0j3wr4rgu%22%7D',
    'content-type': "application/json",
    'accept': "application/json, text/javascript, */*; q=0.01",
    'host': 'www.lulus.com'
    }


class CollectionQueue(Base):
    __tablename__ = 'collection_queue'

    cq_id = Column(Integer, primary_key=True)
    site_name = Column(String(50), default='')
    url = Column(String(512), default='')
    img_url = Column(String(255), default='')
    is_collected = Column(Integer, default=0)
    goods_id = Column(Integer, default=0)
    add_time = Column(Integer, default=0)
    # plan_time = Column(Integer, default=0)
    collected_time = Column(Integer, default=0)
    rank = Column(Integer, default=0)
    # parent_id = Column(Integer, default=0)
    category = Column(String(64), default='')
    secondary_category = Column(String(64), default='')
    # # sub_category = Column(String(64), default='')
    # prev_price = Column(String(12), default='')
    # other_info = Column(Text, default=None)

    def __str__(self):
        return "CollectionQueue => { \
            cq_id:%d, site_name:'%s', url:'%s', img_url:'%s',  \
            add_time:%d, rank:%d, goods_id:%d  \
            category:'%s', secondary_category:'%s'}" % (
            self.cq_id, self.site_name, self.url, self.img_url,
            self.add_time, self.rank, self.goods_id,
            self.category, self.secondary_category,)

    __repr__ = __str__

class Goods(Base):
    __tablename__ = 'goods'

    goods_id = Column(Integer, primary_key=True)
    goods_name = Column(String(255), default='')
    brands_name = Column(String(255), default='')
    goods_price = Column(Float, default=0.00)
    img_url = Column(String(255), default='')
    rank = Column(Integer, default=0)
    status = Column(Integer, default=0)
    is_markdown = Column(Integer, default=0)
    sku = Column(String(255), default='')
    add_time = Column(Integer, default=0)
    # sub_category = Column(String(64), default='')
    category = Column(String(64), default='')
    secondary_category = Column(String(64), default='')
    filter_info = Column(Text, default=None)
    rank_diff = Column(Integer, default=0)
    details_img4 = Column(String(255), default='')
    details_img3 = Column(String(255), default='')
    details_img2 = Column(String(255), default='')
    details_img1 = Column(String(255), default='')
    update_time = Column(Integer, default=0)
    goods_url = Column(String(255), default='')
    img_url_down = Column(String(255), default='')

    def __str__(self):
        return "Goods => { \
            goods_id:%d, goods_name:'%s', brands_name:'%s', goods_price:%0.2f, img_url:'%s',  \
            rank:%d, status:%d, is_markdown:%d, sku:'%s', add_time:%d,  \
            category:'%s', secondary_category:'%s', filter_info:'%s', rank_diff:%d,  \
            details_img4:'%s', details_img3:'%s', details_img2:'%s', details_img1:'%s', update_time:%d,  \
            goods_url:'%s', img_url_down:'%s'}" % (
            self.goods_id, self.goods_name, self.brands_name, self.goods_price, self.img_url,
            self.rank, self.status, self.is_markdown, self.sku, self.add_time,
            self.category, self.secondary_category, self.filter_info, self.rank_diff,
            self.details_img4, self.details_img3, self.details_img2, self.details_img1, self.update_time,
            self.goods_url, self.img_url_down)

    __repr__ = __str__

class CollectionHistory(Base):
    __tablename__ = 'collection_history'

    ch_id = Column(Integer, primary_key=True)
    goods_id = Column(Integer, default=0)
    goods_price = Column(Float, default=0.00)
    rank = Column(Integer, default=0)
    collected_time = Column(Integer, default=0)

    def __str__(self):
        return "CollectionHistory => { \
            ch_id:%d, goods_id:%d, goods_price:%0.2f, rank:%d, collected_time:%d}" % (
            self.ch_id, self.goods_id, self.goods_price, self.rank, self.collected_time)

    __repr__ = __str__


class GoodsFilter(Base):
    __tablename__ = 'goods_filter'

    gf_id = Column(Integer, primary_key=True)
    goods_id = Column(Integer, default=0)
    filter_id = Column(Integer, default=0)
    filter_name = Column(String(255), default='')
    fg_id = Column(Integer, default=0)
    filter_group_name = Column(String(64), default='')

    def __str__(self):
        return "GoodsFilter => { \
            gf_id:%d, goods_id:%d, filter_id:%d, filter_name:'%s', fg_id:%d,  \
            filter_group_name:'%s'}" % (
            self.gf_id, self.goods_id, self.filter_id, self.filter_name, self.fg_id,
            self.filter_group_name)

    __repr__ = __str__


class Filter(Base):
    __tablename__ = 'filter'

    filter_id = Column(Integer, primary_key=True)
    name = Column(String(255), default='')
    fg_id = Column(Integer, default=0)

    def __str__(self):
        return "Filter => { \
            filter_id:%d, name:'%s', fg_id:%d}" % (
            self.filter_id, self.name, self.fg_id)

    __repr__ = __str__


class FilterGroup(Base):
    __tablename__ = 'filter_group'

    fg_id = Column(Integer, primary_key=True)
    name = Column(String(64), default='')

    def __str__(self):
        return "FilterGroup => { \
            fg_id:%d, name:'%s'}" % (
            self.fg_id, self.name)

    __repr__ = __str__


def decimal_price(price_info):
    price = 0.0
    try:
        price = Decimal(price_info)
    except:
        pass
    return price


def create_session():
    """
    创建mysql session
    :return:
    """
    # DB_CONNECT_STRING = 'mysql://root:@localhost/Reptile?charset=utf8'
    DB_CONNECT_STRING = 'mysql://root:@10.10.0.219/go?charset=utf8'
    # DB_CONNECT_STRING = 'mysql://root:@10.10.0.219/Reptile?charset=utf8'
    # DB_CONNECT_STRING = 'mysql://go:go@123@zzkko.cqrxa4hpcscy.us-west-1.rds.amazonaws.com/go?charset=utf8'


    engine      = create_engine(DB_CONNECT_STRING, echo=False)
    DB_Session  = sessionmaker(bind=engine)
    session = DB_Session()
    session._model_changes = {}
    return session


def request_strong(url, retry=0, max_retry=3):
    if retry > max_retry:
        print "max"
        return None

    try:
        r = requests.get(url, headers=headers, timeout=60)
        if r.status_code != 200:
            raise Exception(u"[Error Status Code] code:%s url:%s" % (r.status_code, url))
        html = r.text
        return html
    except Exception, e:
        print Exception
        print e
        time.sleep(retry + 1)
        print("[Retry %s] url:%s" % (retry+1, url))
        return request_strong(url, retry+1)