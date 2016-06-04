#!/usr/bin/env python
# coding=utf-8

import hashlib
import time
import json
import requests
from aladin.helpers import log_debug, log_info
from flask import current_app


def md5(s):
    m = hashlib.md5(s)
    return m.hexdigest()


class UmPush():
    @staticmethod
    def alias_notification(alias, os, event_type, trans_id, text, title='The Shein', production_mode='true'):
        """别名推送
        :param os: 系统
        :param alias: 别名
        :param text:  推送内容
        :param title:  推送标题
        :production_mode: true 正式环境, false 测试环境
        :return:
        """
        if os.lower() == 'android':
            appkey = current_app.config['UM_PUSH_AD_KEY']
            app_master_secret = current_app.config['UM_PUSH_AD_SECRET']

            body_info = {'ticker': 'The Shein',
                         'title': title,
                         'text': text,
                         'after_open': 'go_custom'}
            payload = {'body': body_info,
                       'display_type': 'notification',
                       'extra':{'event_type':event_type, 'trans_id':trans_id}
                       }

        else:
            appkey = current_app.config['UM_PUSH_IOS_KEY']
            app_master_secret = current_app.config['UM_PUSH_IOS_SECRET']

            payload = {'aps': {'alert': text},
                       'event_type':event_type, 'trans_id':trans_id
                       }




        timestamp = int(time.time())
        params = {'appkey': appkey,
                  'timestamp': timestamp,
                  'type': 'customizedcast',
                  "alias": alias,
                  "alias_type": "shein",
                  'payload': payload,
                  "production_mode": production_mode

                  }
        post_body = json.dumps(params)
        sign = UmPush.get_sign(post_body, app_master_secret)
        url = 'http://msg.umeng.com/api/send' + '?sign=' + sign

        r = requests.post(url, data=post_body)
        log_debug(r.text)


    @staticmethod
    def filter_notification(os, tag_arr_json, event_type, trans_id, text, title='The Shein', production_mode='true'):
        """标签推送
        :param os:
        :param tag_arr_json: [{"tag":"shein"},{"tag":"cart-list"},{"tag":"unpay-order"}]
        :param event_type:
        :param trans_id:
        :param text:
        :param title:
        :param production_mode:
        :return:
        """


        if os.lower() == 'android':
            appkey = current_app.config['UM_PUSH_AD_KEY']
            app_master_secret = current_app.config['UM_PUSH_AD_SECRET']

            body_info = {'ticker': 'The Shein',
                         'title': title,
                         'text': text,
                         'after_open': 'go_custom'}
            payload = {'body': body_info,
                       'display_type': 'notification',
                       'extra':{'event_type':event_type, 'trans_id':trans_id}
                       }

        else:
            appkey = current_app.config['UM_PUSH_IOS_KEY']
            app_master_secret = current_app.config['UM_PUSH_IOS_SECRET']

            payload = {'aps': {'alert': text},
                       'event_type':event_type, 'trans_id':trans_id
                       }


        timestamp = int(time.time())
        params = {'appkey': appkey,
                  'timestamp': timestamp,
                  'type': 'groupcast',
                  'filter':{"where":{"and":[{"or":tag_arr_json}]}},
                  'payload': payload,
                  "production_mode": production_mode,

                  }

        post_body = json.dumps(params)
        sign = UmPush.get_sign(post_body, app_master_secret)
        url = 'http://msg.umeng.com/api/send' + '?sign=' + sign

        r = requests.post(url, data=post_body)
        log_debug(r.text)


    @staticmethod
    def get_sign(post_body, app_master_secret):
        """生成加密签名
        :param post_body: json字符串的推送参数
        :param app_master_secret: 加密字符串
        :return:
        """

        method = 'POST'
        url = 'http://msg.umeng.com/api/send'
        log_debug(post_body)
        sign = md5('%s%s%s%s' % (method, url, post_body, app_master_secret))
        return sign
