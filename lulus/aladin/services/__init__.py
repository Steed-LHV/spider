#!/usr/bin/env python
#coding=utf-8

import os

#from flask import Response
from flask import current_app

from aladin.helpers import to_json
from aladin.services_code import G_SERVICE_CODE, MODULE_CODE_NONE, ACTION_CODE_NONE


class ResponseJson(object):
    def __init__(self):
        """初始化函数"""
        self.module_code = None
        self.action_code = None

    def print_json(self, ret=0, msg='ok', data=None):
        #res = Response(status=200, mimetype='application/json')
        res = current_app.response_class(mimetype='application/json')

        if ret > 99 and msg is 'ok':
            
            # 从配置文件中获取错误消息
            msg = G_SERVICE_CODE.get(ret)

            if msg is None:
                msg = u'未知错误'

            res.data = to_json(ret, msg, data)
            return res

        if self.module_code is None:
            res.data = to_json(MODULE_CODE_NONE, G_SERVICE_CODE.get(MODULE_CODE_NONE))
            return res

        if self.action_code is None:
            res.data = to_json(ACTION_CODE_NONE, G_SERVICE_CODE.get(ACTION_CODE_NONE))
            return res

        if ret == 0:
            res.data = to_json(0, msg, data)
            return res

        ret = "%s%s%s" % (self.module_code, self.action_code, ret)
        ret = int(ret)
        res.data = to_json(ret, msg, data)
        return res
