#!/usr/bin/env python
#coding=utf-8

from flask import current_app

from aladin.helpers import log_debug, log_info, log_error,call_asyn_api,json_encode



def push(data,user):
    log_debug("begin push(data,user)-->param:%s;user:%s;"%(data,user))
    param              = {}
    param["pushtoken"] = user.pushtoken
    param["uid"]   = user.uid
    param["os"]        = user.os
    param["version"]   = user.version
    
    aps_json           = json_encode({'aps':data})
    param              = json_encode({'param':param})
    _SERVICE_URL = current_app.config['SERVICE_URL']
    service_url        = _SERVICE_URL or "http://service.zzkko.com:5000"

    if user.os == 'android':
        service_url = service_url+'/push/android'
    elif user.os == 'iPhone OS':
        service_url = service_url+'/push/ios'

    call_asyn_api(service_url, {'aps_json':aps_json, 'param':param}, 'POST')
    log_debug("tpush(data,user) end。")
