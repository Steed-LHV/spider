#!/usr/bin/env python
#coding=utf-8
"""
    helpers.py
    ~~~~~~~~~~~~~
    :助手工具文件
"""
from __future__ import division
import email
import re
import urlparse
import functools
import hashlib
import socket, struct
import json
import types
import datetime
import time
import logging
import string
import os
import urllib

from decimal import Decimal
from datetime import timedelta
from cookielib import Cookie, CookieJar

try:
    import Image
except Exception, e:
    from PIL import Image

from flask import current_app, g, request, session, redirect, url_for, \
                    render_template as flask_render_template
from flask.ext import sqlalchemy
from sqlalchemy.util import KeyedTuple


def render_template(template, **context):
    #return render_theme_template(get_theme(), template, **context)
    return flask_render_template(template, **context)


def domain(url):
    """
    Returns the domain of a URL e.g. http://reddit.com/ > reddit.com
    """
    rv = urlparse.urlparse(url).netloc
    if rv.startswith("www."):
        rv = rv[4:]
    return rv

def ip2long(ip):
    return struct.unpack("!I",socket.inet_aton(ip))[0]

def long2ip(num):
    return socket.inet_ntoa(struct.pack("!I",num))
    

def log_info(logtext):
    extra_log = {'clientip':request.remote_addr, 'username':session.get('username', '')}
    # current_app.logger.info(logtext, extra=extra_log)
    logger = logging.getLogger('web.info')
    logger.info(logtext, extra=extra_log)

def log_error(logtext):
    extra_log = {'clientip':request.remote_addr}
    logger = logging.getLogger('web.error')
    logger.error(logtext, extra=extra_log)

def log_debug(logtext):
    if current_app.config.get('DEBUG', False):
        extra_log = {'clientip':request.remote_addr}
        logger = logging.getLogger('web.debug')
        logger.debug(logtext, extra=extra_log)

def get_start_end_row(page, pagesize=20):
    page = toint(page)
    pagesize = toint(pagesize)

    page = page <= 0 and 1 or page

    if pagesize <= 0:
        pagesize = 20
    elif pagesize > 50:
        pagesize = 50

    start = (page-1) * pagesize
    end = start + pagesize

    return (start, end)

def getoffset(page, pagesize=20):
    """
    获取分页偏移量
    :param page:
    :param pagesize:
    :return: 偏移量
    """
    page = toint(page)

    page = page <= 0 and 1 or page

    if pagesize <= 0:
        pagesize = 20
    elif pagesize > 50:
        pagesize = 50

    return (page-1) * pagesize


def toint(s, base=10):
    """
    字符串转换成整型，对于不能转换的返回0
    :param s: 需要转换的字符串
    :param base: 多少进制，默认是10进制。如果是16进制，可以写0x或者0X
    :return: int
    """
    try:
        ns = '%s' % s
        return string.atoi(ns, base)
    except ValueError:
        #忽略错误
        pass

    return 0

def tofloat(s):
    """
    字符串转换成浮点型, 对于不能转换的返回float(0)
    :param s: 需要转换的字符串
    :return: float
    """
    try:
        return string.atof(s)
    except ValueError:
        pass

    return float(0)

def tolong(s):
    try:
        return string.atol(s)
    except ValueError:
        pass

    return long(0)

def show_admin_error(title, errmsg=None, jumpurl='', time=0, links=None):
    if not errmsg:
        errmsg = u'系统繁忙，请稍候重试。'

    return render_template('admin/error.html', title=title, errmsg=errmsg, jumpurl=jumpurl, time=time, links=links)

def show_admin_success(title, msg, jumpurl='', time=3, links=None):
    return render_template('admin/success.html', title=title, msg=msg, jumpurl=jumpurl, time=time, links=links)

def ismobile(mobile):
    """
    是否手机号码
    @param mobile: 手机号码
    @return: boolean
    """
    import re
    #return re.match('^0?1[3458]\d{9}$', mobile)

    #为了方便测试，增加8开头的测试手机号码段
    return re.match('^0?[18][3458]\d{9}$', mobile)

def isamount(amount):
    """
    是否正确的金额格式
    @param  :amount   金额字符串
    @Returns  :None or SRE_Match
    """
    import re
    return re.match('^[0-9][0-9]*(\.[0-9]{1,2})?$', amount)

def isemail(email):
    """
    是否有效邮箱地址
    @param :email 邮箱地址
    @return :boolean
    """
    import re
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True

    return False

def make_thumb(filename, width=0, height=0, quality=80):
    """
    等比缩放，生成缩略图
    @param filename 原图绝对路径
    @param width    缩略图宽度
    @param height   缩略图高度
    @param quality  品质
    @return         缩略图文件名称(不含路径)
    """
    try:
        im = Image.open(filename)
        w,h = im.size

        # 等比缩放
        if width != height:
            if height == 0 and width < w and w != h:
                h = int((width/w) * h)
                w = width
            elif width == 0 and height < h and w != h:
                w = int((height/h) * w)
                h = height
            else:
                w = max(width, height)
                h = w

        # 正方形
        elif width == height:
            if w > h:
                left    = int( (w-h) / 2 )
                right   = left + h
                im      = im.crop((left, 0, right, h))
            elif w < h:
                upper   = int( (h-w) / 2 )
                lower   = upper + w
                im      = im.crop((0, upper, w, lower))

            w,h = width, height

        if im.mode != "RGB":
            im = im.convert("RGB")

        thumb_filename = "%s_%dx%d.jpg" % (filename, w, h)
        im.thumbnail((w,h), Image.ANTIALIAS)
        im.save(thumb_filename, quality=quality)

        # /photos/2013-03-04/5e65d51cbde93.jpg => 5e65d51cbde93.jpg
        return thumb_filename[thumb_filename.rfind('/')+1:]
    except Exception, e:
        raise e
        
def randomstr(random_len = 6, random_type = 0):
    """
    获取随机字符串
    @param random_len: 随机字符串长度
    @param random_type: 随机类型 0:大小写数字混合 1:数字 2:小写字母 3:大写字母
    @return string
    """
    random_string_array = ['0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        '0123456789', 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
    if random_type < 0 or random_type > len(random_string_array):
        random_type = 0

    random_string = random_string_array[random_type]

    import random
    return ''.join(random.sample(random_string, random_len))

def yuan2fen(amount_str):
    """
    元转换成分，对于不能转换的返回-1
    @param amount_str: 字符串，元
    @return int
    """
    fen = -1
    try:
        yuan = float(amount_str)
        fen = int(yuan * 100)
    except ValueError:
        pass
    
    return fen


def to_json(ret=0, msg='ok', data=None):
    now = int(time.time())
    jsondata = {'ret':ret, 'msg':msg, 'timestamp':now}

    if not data:
        return json.dumps(jsondata)

    jsondata['data'] = data
    return json_encode(jsondata)

def json_encode(data):

    def _any(data):
        ret = None
        if type(data) is types.ListType:
            ret = _list(data)
        elif type(data) is types.DictType:
            ret = _dict(data)
        elif isinstance(data, Decimal):
            ret = str(data)
        elif isinstance(data, sqlalchemy.Model):
            ret = _model(data)
        elif isinstance(data, KeyedTuple):
            ret = _dict(data._asdict())
        elif isinstance(data, datetime.datetime):
            ret = _datetime(data)
        elif isinstance(data, datetime.date):
            ret = _date(data)
        elif isinstance(data, datetime.time):
            ret = _time(data)
        else:
            ret = data

        return ret

    def _model(data):
        ret = {}
        for c in data.__table__.columns:
            ret[c.name] = _any(getattr(data, c.name))

        return ret

    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret

    def _dict(data): 
        ret = {}
        for k,v in data.items():
            ret[k] = _any(v)
        return ret

    def _datetime(data):
        return data.strftime("%s %s" % ("%Y-%m-%d", "%H:%M:%S"))

    def _date(data):
        return data.strftime("%Y-%m-%d")

    def _time(data):
        return data.strftime("%H:%M:%S")

    ret = _any(data)

    return json.dumps(ret)



def format_timestamp(timestamp, format='%Y-%m-%d %H:%M:%S'):

    if timestamp is None or not timestamp:
        return ''
        
    if type(timestamp) in (types.StringType, types.UnicodeType):
        return timestamp

    if format is 'isodate':
        format = '%Y-%m-%d %H:%M:%S'
    elif format in ('date', 'shortdate', 'short-date'):
        format = '%Y-%m-%d'
    elif format is 'time':
        format = '%H:%M:%S'

    return datetime.datetime.fromtimestamp(timestamp).strftime(format)

def call_asyn_api(url, params={}, method='GET'):
    """调用异步接口"""
    from aladin.ext.net import JSONService

    asyn_api_url = current_app.config['ASYN_API_URL']
    params['service_url'] = url
    params['service_method'] = method
    js = JSONService(asyn_api_url, params, method)
    js.call_service()
    return js.res

def form2model(form, model):
    """
    表单转换成model对象
    :param form request的args或者form对象
    :param model flask-sqlalchemy model对象
    :return (model, boolean, errmsg)
    """
    from sqlalchemy import types

    if form is None:
        return (model, False, {})

    is_success = True
    errmsg = {}
    for c in model.__table__.columns:

        if c.name not in form:
            continue

        if c.primary_key is True:
            continue

        v = form.get(c.name, '')
        if isinstance(c.type, types.String):
            if c.type.length is not None and len(v) > c.type.length:
                is_success = False
                errmsg[c.name] = u'长度太长' 
                log_debug('%s => %s, length:%s, type:%s' % 
                    (c.name, u'长度太长', c.type.length, type(c.type)))
        elif isinstance(c.type, types.Integer):
            try:
                v = string.atoi(v)
            except Exception, e:
                is_success = False
                errmsg[c.name] = u'类型错误'
                log_debug('%s => %s' % (c.name, u'类型错误'))

        if is_success:
            setattr(model, c.name, v)

    return (model, is_success, errmsg)

def conver_model(source_model, target_model, notin=[]):
    """
    转换model
    :param source_model 源model
    :param target_model 目标model
    :param notin 排除字段(属性)
    :return target_model
    """

    if source_model is None or target_model is None:
        return None

    tar_columns = []
    for c in target_model.__table__.columns:
        tar_columns.append(c.name)

    for c in source_model.__table__.columns:
        if c.name not in tar_columns or c.name in notin:
            continue

        v = getattr(source_model, c.name)
        setattr(target_model, c.name, v)

    return target_model

def model_to_string(model):
    """model对象输出string
    :param model db.Model
    :return string
    """
    from flask.ext import sqlalchemy

    if model is None or not isinstance(model, sqlalchemy.Model):
        return None

    s = '%s => {' % model.__class__.__name__
    for c in model.__table__.columns:
        v = getattr(model, c.name)
        s += '%s:%s, ' % (c.name, v)
    s += '}'
    return s 


def put_to_amazon(filename, upload_type, default_dir=None):
    """上传文件至amazon服务器
    :param string|list filename 文件名或者是文件列表
    :param string 上传类型，如:avatar|goods
    :default_dir string 默认目录，如果为None，则以日期来创建
    :return string|list 返回目标地址url或者列表
    """
    import boto
    import os.path
    from datetime import date
    
    key_id            = os.getenv('AMAZON_KEY_ID')
    access_key        = os.getenv('AMAZON_ACCEST_KEY')
    bucket_name       = os.getenv('AMAZON_BUCKET_NAME')
    cloudfront_domain = os.getenv('AMAZON_CLOUDFRONT_DOMAIN')

    filename_list = None
    if isinstance(filename, types.StringType) or \
                isinstance(filename, types.UnicodeType):
        filename_list = (filename, )
    else:
        filename_list = filename

    if default_dir is None:
        default_dir = '%s' % date.today()

    ret_filename_list = []
    s3 = boto.connect_s3(key_id, access_key)
    bucket = s3.get_bucket(bucket_name)
    for fn in filename_list:
        if not os.path.exists(fn):
            ret_filename_list.append('')
            continue

        # /goods/2014-01-04/haha.jpg
        base_filename = fn[fn.rfind('/')+1:]
        key_name = '%s/%s/%s' % (upload_type, default_dir, base_filename)
        
        k = bucket.new_key(key_name)
        k.metadata = s3_metadata(k.metadata)
        k.set_contents_from_filename(fn)
        k.make_public()
        target_url = '%s/%s' % (cloudfront_domain, key_name)
        ret_filename_list.append(target_url)

    if isinstance(filename, types.StringType) or \
                isinstance(filename, types.UnicodeType):
        return ret_filename_list[0]

    return ret_filename_list

def s3_metadata(meta):
    """设置S3文件过期时间"""

    five_year = datetime.datetime.now() + timedelta(days=365*5)

    # HTTP/1.0 (5 years)
    meta['Expires'] = '%s GMT+0800' % five_year.strftime('%a %b %d %Y %H:%M:%S')

    # HTTP/1.1 (5 years)
    five_year_sec = 5*365*24*60*60
    meta['Cache-Control'] = 'max-age=%d' % five_year_sec
    return meta


def call_zzkko_api(uri, params=None, method='GET', timeout=10, 
                api_url_prefix=None, session_cookie_name='zzkko_session', session_cookie_value=None):
    """调用zzkko api"""
    from aladin.ext.net import JSONService

    if api_url_prefix is None:
        api_url_prefix = current_app.config['API_ZZKKO_COM']

    if session_cookie_value is None:
        session_cookie_value = request.cookies.get(session_cookie_name, None)

    cj = CookieJar()
    if session_cookie_value is not None:
        c = Cookie(None, session_cookie_name, session_cookie_value, 
               port=None, port_specified=None, domain='', 
               domain_specified=None, domain_initial_dot=None, path='/', 
               path_specified=None, secure=None, expires=None, 
               discard=None, comment=None, comment_url=None, 
               rest=None)
        cj.set_cookie(c)
        
    url = api_url_prefix + uri
    js = JSONService(url, params, method, timeout, cj)
    return js

def get_api_service(uri, params=None, method='GET', timeout=30, 
        api_url_prefix=None, session_cookie_name='zzkko_session', session_cookie_value=None):
    """获取api Service类"""
    return call_zzkko_api(uri, params, method, timeout, 
                api_url_prefix, session_cookie_name, session_cookie_value)
    
def md5(str):
    return hashlib.md5(str).hexdigest()

def get_today_unixtime():
    """获取当天unixtime"""
    return int(time.mktime(datetime.date.today().timetuple()))

def get_count(q):
    from sqlalchemy import func
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count


def urlencode(params):
    _params = params.copy()
    for k,v in params.items():
        if isinstance(v, types.StringType) or isinstance(v, types.UnicodeType):
            _params[k] = v.encode('utf8')

    return urllib.urlencode(_params)


def shipping_tracking_link(shipping_company='', shipping_sn=''):
    """ 根据快递公司和快递单号获取物流跟踪链接 """

    link             = ''
    shipping_company = shipping_company.upper()
    shipping_company = shipping_company.replace('EXPRESS', '')
    shipping_company = shipping_company.replace('-', '')

    if not shipping_company  or not shipping_sn:
        return link

    if shipping_company == 'USPS':
        link = 'https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=' + shipping_sn
    elif shipping_company in ('DHL', 'SGDHL'):
        link = 'http://www.dhl.com/content/g0/en/express/tracking.html?brand=DHL&AWB=' + shipping_sn
    elif shipping_company == 'TOLL':
        link = 'http://www.17track.net/m/en/result/express-details-100009.shtml?nums=' + shipping_sn
    elif shipping_company == 'FEDEX':
        link = 'http://www.17track.net/m/en/result/express-details-100003.shtml?nums=' + shipping_sn
    elif shipping_company == 'GLS':
        link = 'http://www.17track.net/m/en/result/express-details-100005.shtml?nums=' + shipping_sn
    elif shipping_company == 'YUNPOST':
        link = 'http://www.17track.net/m/en/result/express-details-190008.shtml?nums=' + shipping_sn
    else:
        link = 'http://www.17track.net/m/en/result/post-details.shtml?pt=0&cm=0&cc=0&nums=' + shipping_sn

    return link

