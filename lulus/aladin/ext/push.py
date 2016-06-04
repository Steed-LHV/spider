#!/usr/bin/env python
#coding=utf-8
from flask import current_app

from aladin.helpers import call_asyn_api, json_encode, log_info, log_debug

class Push(object):
    """zzkko推送封装类"""
    
    @staticmethod
    def message(os, pushtoken, aps, version, uid):
        """推送消息"""
        aps['uid'] = uid
        Push.send(os, pushtoken, aps)


    @staticmethod
    def send(os, pushtoken, aps):
        """调用parse推送"""
        os         = 'android' if os == 'android' else 'ios'
        event_type = aps['event_type']
        trans_id   = aps['trans_id']
        content    = aps['alert']
        data       = aps.get('data', {})
        badge      = aps.get('badge', 1)
        sound      = aps.get('sound', 'default')
        uid        = aps.get('uid', 0)

        Push.pushtoken(pushtoken, os, event_type, trans_id, content, data=data, uid=uid)


    @staticmethod
    def pushtoken(pushtoken, os, event_type, trans_id, content, title='The Yub', data={}, uid=0, badge=1):
        """根据token推送
        pushtoken: 推送token
        os: 操作系统
        event_type: 事件类型
        trans_id: 交易id
        content: 显示内容
        title: 标题，只针对android用户
        data: 自定义报文，dict对象
        uid: 用户uid
        badge: APP右上角显示未阅读数
        """
        if not pushtoken or not os:
            log_info('[Push][PushError] pushtoken => %s, os => %s' % (pushtoken, os))
            return

        from parse_rest.connection import register
        from parse_rest.installation import Push as ParsePush
        parse_app_id  = current_app.config['PARSE_APP_ID']
        parse_app_key = current_app.config['PARSE_APP_KEY']
        register(parse_app_id, parse_app_key)

        where = {'objectId':pushtoken}
        push_params = {'badge':badge, 'uid':uid, 'data':data, 'sound':'default', 
            'event_type':event_type, 'trans_id':trans_id, 'alert':content, 'deviceType':os}

        ParsePush.alert(push_params, where=where)


    @staticmethod
    def send_tag(aps, tag_name):
        """parse 标签推送"""
        from parse_rest.connection import register
        from parse_rest.installation import Push as ParsePush
        parse_app_id  = "d44eWVZMfeiivL8vWg6S9mgiltSTQSrTyoT8sNOZ"
        parse_app_key = "RrvBWUH6FE1L1V2QcqyhNPbJKGtqKaBWuDWJGmlR"
        register(parse_app_id, parse_app_key)

        ParsePush.alert({'alert': aps['alert'],
                    'badge': aps['badge'],
                    'sound':aps['sound'],
                    'event_type':aps['event_type'],
                    'trans_id':aps['trans_id'],
                    'data':aps.get('data', {})},
                   where={"channels": tag_name})


    @staticmethod
    def asyn_send_tag(aps, tag_name):
        """异步推送按标签"""
        push_url = 'http://service.zzkko.com:5000/push/tag'
        aps_json = json_encode(aps)

        req_param = {}
        req_param['aps_json'] = aps_json
        req_param['tag_name'] = tag_name
        call_asyn_api(push_url, req_param, 'POST')


