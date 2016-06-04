#!/usr/bin/env python
#coding=utf-8
"""
   日期工具
"""
import time
import datetime as dt
from datetime import datetime, timedelta
from pytz import timezone

import pytz
import types


def get_today_unixtime():
    """
    获取当天unixtime 
    参数 zone 时区（可选）
    """
    return int(time.mktime(dt.date.today().timetuple()))


def get_yesterday_unixtime():
    """获取昨天00:00的unixtime"""
    today = dt.date.today()
    yesterday = today - timedelta(days=1)
    yesterday_unixtime = int(time.mktime(yesterday.timetuple()))
    return yesterday_unixtime


def get_diff_days(str_begin_date, str_end_date):
    """获取相差天数
    2015-03-01 到 2015-03-09 相差9天，区间是[]
    """
    begin_datetime = datetime.strptime(str_begin_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(str_end_date, '%Y-%m-%d')

    diff_days = (end_datetime-begin_datetime).days

    return diff_days


def get_date_list(str_begin_date, str_end_date, order_by='asc'):
    """获取日期列表
    :str_begin_date 2015-03-09
    :str_end_date 2015-03-07
    :order_by desc|asc
    :return => [2015-03-09, 2015-03-08, 2015-03-07]
    """
    diff_days = get_diff_days(str_begin_date, str_end_date)
    begin_datetime = datetime.strptime(str_begin_date, '%Y-%m-%d')
    date_list = []
    for index in range(1, diff_days):
        day_date = begin_datetime + timedelta(days=index)
        if order_by == 'desc':
            day_date = begin_datetime + timedelta(days=(diff_days-index))

        date_list.append(day_date)

    return date_list


def format_timestamp(timestamp, format='%Y-%m-%d %H:%M:%S',zone=None):
    """
    unixtime 时间 转 字符串
    默认：%Y-%m-%d %H:%M:%S
    """

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
    if zone :
        tz = timezone(zone)
        t = pytz.utc.localize(datetime.utcfromtimestamp(timestamp))
        t = t.astimezone(tz)
        
        return t.strftime(format)
    return datetime.fromtimestamp(timestamp).strftime(format)


def strToTimeStamp(date,format="%Y-%m-%d",zone=None):
    """
    字符串形式日期转换为时间戳 ，默认格式"%Y-%m-%d"
    转换出错默认返回 0
    """
    
    timeArray = time.strptime(date, format)
    if zone:
        tz = timezone(zone)
        y,m,d,H,M,S = timeArray[0:6]
        dt = datetime(y,m,d,H,M,S)
        t = tz.localize(dt)
        t = t.astimezone(pytz.utc)
        return int(time.mktime(t.utctimetuple()))-time.timezone
    return int(time.mktime(timeArray))


def add_date(date, num):
    """日期加减运算"""
    return date + timedelta(days=num)

    
if __name__ == '__main__':

    a = time.time()
    print a
    b = format_timestamp(a,zone='Asia/Shanghai')
    print b
    c=  format_timestamp(a,zone='UTC')
    print c
    d =format_timestamp(a,zone='Europe/Amsterdam')
    print d

    e =  strToTimeStamp(b,'%Y-%m-%d %H:%M:%S',zone='Asia/Shanghai')
    print e
    f =  strToTimeStamp(d,'%Y-%m-%d %H:%M:%S',zone="Europe/Amsterdam")
    print f
    print format_timestamp(f,zone='Asia/Shanghai')