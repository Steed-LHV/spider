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
    'Cookie': "originalsource=""; currency=USD; remarketing=TypeB; newSitePref=newSite; optimizelyEndUserId=oeu1464170673732r0.364568362818932; userClosedNtfDialogCount=1; userLastSeenNtfDialogDate=2016-05-25; _msuuid_vxn6dlnn50=1401AE94-C627-481F-9F00-73B2CC609EFA; __lc.visitor_id.2506231=S1464170719.d51a7cb8de; SSP_PROFILED_USER=false; name.cookie.last.visited.product=OHMY-WD44; __cmbDomTm=0; __cmbU=ABJeb1-UHqXkxBRM3Lmr_IT7ywmtkIuUewvqkiNoW3TxfTTl1gNntrJqHyct6dwJfPQbJhWOcoQ26mBvrCIqtJlzGkM9hoVYOQ; __cmbTpvTm=3760; __cmbCk=PMRGK2LEEI5CEQKCJJSWEMJNHA4WEODNOZUEGSBZGRRDCRSEKRKEWWBRMJGXQU3IMRLGONSTNNPW432UKNCXO22QOJXHKLLCJVSTKNLIKVMDMNDSJNWF6WKDGFYS2UKROM2WIMCXGNLUQVSFNE2XATKKJZUFQ4RSHEZDEOKSKERCYITTNR2CEORRGQ3DIMJXGA4DKMJYG4ZCYITDMJ2CEORRHA2TSNRMEJ2HAIR2GMZTCMZRGB6Q====; _sp_id.9084=7d4bfb58-8ba6-4dff-8f21-6bd6dd83f7d0.1464170723.1.1464171217.1464170723.29d1ca5e-7b6b-4747-907b-300a2f6054f3; SSP_AB_Preselection_20160126=Test; SSP_AB_StyleFinder_20160425=Test; SSP_AB_StyleFinderPhase_20160425=Phase9; optimizelySegments=%7B%221000984897%22%3A%22false%22%2C%221009020749%22%3A%22gc%22%2C%221009820758%22%3A%22direct%22%2C%222007840916%22%3A%22none%22%2C%223342380158%22%3A%22true%22%7D; optimizelyBuckets=%7B%7D; uid_bam=1572141341144762935; JSESSIONID=399C10C38EC58C469B3D9DC21B51FE41.atom_tomcat4; newRevCom=user%20left; __lc.visitor_id.7020571=S1464745196.823be3f058; _gat=1; __utmt=1; bb_PageURL=%2Fr%2FBrands.jsp%3F%26aliasURL%3Ddresses%252Fbr%252Fa8e981%26navsrc%3Dsubclothing; ntfPopupSuppressionCount=10; userSeenNtfDialogDate=2016-05-31; sortByR2=newest; viewNumR1=100; isPopupEnabledR1=true; pocketViewR1=front; searchMobileFilterByR1=""; sizeFilterByR1=""; shoeSizeFilterByR1=""; topSizeFilterByR1=""; bottomSizeFilterByR1=""; handbagFilterByR1=""; heelFilterByR1=""; riseFilterByR1=""; colorFilterByR1=""; priceFilterByR1=""; percentFilterByR1=""; browserID=sutgddkUHGrDnOorD0IoNtLIOXBBUB; currencyOverride=USD; userLanguagePref=en; visitor-cookie30=true; visitor-cookie1=true; __utma=107829505.725228901.1464170679.1464572359.1464745195.3; __utmb=107829505.3.10.1464745195; __utmc=107829505; __utmz=107829505.1464170680.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.725228901.1464170679",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'host': 'www.revolve.com'
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