#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
极光推送，接口文档请参见：http://docs.jpush.cn/pages/viewpage.action?pageId=2621796

"""

import json
import hashlib
import urllib
import urllib2
import time

from aladin.helpers import log_info, log_debug

# 接口地址
#API_URL = 'http://api.jpush.cn:8800/sendmsg/v2/sendmsg'
API_URL = 'http://api.jpush.cn:8800/v2/push'

# 接口参数
KEY_PARAMS = (
    'sendno',
    'app_key',
    'receiver_type',
    'receiver_value',
    'verification_code',
    'msg_type',
    'msg_content',
    'send_description',
    'platform',
)

class JPushClient(object):
    """极光推送"""
    def __init__(self, username, master_secret, callback_url=""):
        self.username = username
        self.master_secret = master_secret
        self.callback_url = callback_url
        
    def _gen_params(self, kargs):
        """Generate Post params"""
        params = {}
        params["username"] = self.username
        params["callback_url"] = self.callback_url
        for k in KEY_PARAMS:
            params[k] = kargs.get(k)
        return params

    def _gen_content(self, msg_title, msg_content, msg_type, extras):
        """Generate message content"""
        content={}
        if msg_type == 1:   # notification
            content["n_title"] = msg_title
            content["n_content"] = msg_content
            content['n_extras'] = extras
        else:           # custom message
            content["title"] = msg_title
            content["message"] = msg_content
            content['extras'] = extras
        return json.dumps(content, separators=(',', ':'))

    def _gen_verification_code(self, sendno, receiver_type, receiver_value):
        """Generage verification code"""
        mobj = hashlib.md5()
        verification_str = "%d%s%s%s" % (sendno, receiver_type,
                                         receiver_value, self.master_secret)
        mobj.update(verification_str)
        return mobj.hexdigest().upper()

    def _send_msg(self, params):
        '''Push API for all kinds of message and notification,
           dict params restore all parameters'''
        try:
            api_post = urllib2.urlopen(data=urllib.urlencode(params),
                                       url=API_URL, timeout=5)
            if api_post:
                log_debug(api_post.read())

        except Exception, e:
            #print e, e.read()
            log_info("[JpushError] %s" % e)

    def send_notification_by_alias(self, alias, app_key, sendno, senddes,
                                   msgtitle, msg_content, platform, extras={}):
        '''Send notification by alias'''
        receiver_type = 3
        msg_type = 1
        msg_content = self._gen_content(msgtitle, msg_content,
                                        msg_type, extras)
        receiver_value = alias
        verification_code = self._gen_verification_code(sendno,
                                                        receiver_type,
                                                        receiver_value)
        params = self._gen_params(locals())
        self._send_msg(params)

    def send_custom_msg_by_alias(self, alias, app_key, sendno, senddes,
                                 msgtitle, msg_content, platform, extras={}):
        '''Send custom message by alias'''
        receiver_type = 3
        msg_type = 2
        msg_content = self._gen_content(msgtitle, msg_content,
                                        msg_type, extras)
        receiver_value = alias
        verification_code = self._gen_verification_code(sendno, receiver_type,
                                                        receiver_value)
        params = self._gen_params(locals())
        self._send_msg(params)


if __name__ == '__main__':
    push_token = '9e6f2d37725b074db07b23452ce03ccf'
    master_secret = '20124fc4c3b05db71a4b632e'
    app_key = '0b3b4d4937287837b70762b7'
    sendno = int(time.time())
    title = u'呼叫标题 -- python'
    content = u'呼叫内容 -- python'
    os = 'ios'
    data={'call_id':1234, 'event_id':1004}


    client = JPushClient(push_token, master_secret)

    client.send_notification_by_alias(push_token, app_key, 
                sendno, '', title, content, os, data)

    print 'end.............'
