#!/usr/bin/env python
#coding=utf-8

import json
import urllib
import urllib2
import types

from cookielib import CookieJar
from requests.utils import guess_json_utf

from aladin.helpers import log_debug, log_error, toint, log_info, urlencode


class JSONService(object):
    """json服务"""

    def __init__(self, url, params=None, method='GET', 
            timeout=10, cookie_jar=None, json_type='me', headers=[('language', 'en')]):
        self.url        = url
        self.params     = params
        self.method     = method
        self.timeout    = timeout
        self.cookie_jar = cookie_jar
        self.json_type  = json_type
        self.headers    = headers

        self.res        = None
        self.json       = {}
        self.ret        = None
        self.msg        = None
        self.data       = None
        self.set_cookie = ''
        self.encoding   = None

    def call_service(self):
        """调用远程服务"""
        try:
            encode_data = None
            if self.params is not None:
                if self.method == 'GET':
                    self.url += '?' + urlencode(self.params)
                    log_debug(self.url)

                elif self.method == 'POST':
                    encode_data = urlencode(self.params)

            opener = urllib2.build_opener()
            opener.addheaders = self.headers
            
            if self.cookie_jar is not None:
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))

            res_obj = opener.open(self.url, data=encode_data, timeout=self.timeout)
            self.set_cookie = res_obj.info().getheader('Set-Cookie')
            self.res = res_obj.read()

            # encoding
            self.encoding = guess_json_utf(self.res)
            if self.encoding:
                self.res = self.res.decode(self.encoding)

            self.json = json.loads(self.res)
            self.ret  = self.json.get('ret')
            self.msg  = self.json.get('msg')
            self.data = self.json.get('data')
        except Exception, e:
            #log_error('[JSONService] url:%s, response:%s, expetion:%s' % (self.url, self.res, e))
            return False

        if self.ret != 0 and self.json_type == 'me':
            log_info('[JSONService] url:%s, response:%s' % (self.url, self.res))
            return False

        #log_debug('[JSONService] success url:%s, response:%s' % (self.url, self.res))

        return True


    def get_response_cookie(self):
        """获取响应返回cookie"""
        if not self.set_cookie:
            return {}

        cookie_map = {}
        cookie_arr = self.set_cookie.split(',')
        for cookie in cookie_arr:
            arr = cookie.split(';')
            str_kv = arr[0]
            str_kv = str_kv.strip()
            kv = str_kv.split('=')
            if len(kv) == 2:
                cookie_map[kv[0]] = kv[1]

        return cookie_map


if __name__ == '__main__':
    api_host = 'http://app.allinpass.com'
    my = '/my/'
    login = """/account/login/token?os=android&token=%23V1.0%23868943001291782%23201306051224450286866%2312246%23153%23234379315%233045022034FB267587F812B71EB3546052E70B358250B91E6547191118C8259A7A7D41CF022100A643AF0FBDC73AAA38159985F27736294CE20D8A9E4B16A66E111958899071C1&vendor=HUAWEI+U8860&push_token=BCA0760EF54B3EA8823D6A7440E972DA&client_flag=%E6%89%8B%E6%9C%BA%E5%BA%97&longitude=22.541129&latitude=22.541129&client_version=1.3.0.0&os_version=2.3.6"""

    cookie_jar = CookieJar()
    js_login = JSONService(api_host+login, cookie_jar=cookie_jar)
    js_login.call_service()
    print js_login.res
    print '------------------------------------'
    print cookie_jar
    print '------------------------------------'

    js = JSONService(api_host+my)
    js.call_service()
    print js.res
    print '------------------------------------'

    js_my = JSONService(api_host+my, cookie_jar=cookie_jar)
    js_my.call_service()
    print js_my.res


