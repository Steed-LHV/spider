#!/usr/bin/env python
#coding=utf-8

"""
服务错误代码列表
"""

SYSTEM_BUSY           = 101001 #服务器开小差中，请稍候重试。
SYSTEM_PAGE_NOT_FOUND = 101002 #页面找不到
NOT_LOGIN             = 101110 #用户未登录或者登录超时
PARAM_ERROR           = 101111 #请求参数错误
MODULE_CODE_NONE      = 101112 #module编码为None
ACTION_CODE_NONE      = 101113 #action编码为None
PAGESIZE_TOO_LARGE    = 101114 #页面记录数太大

G_SERVICE_CODE = {
    SYSTEM_BUSY           : u'Server error, please try again.',
    SYSTEM_PAGE_NOT_FOUND : u'Page not found.',
    NOT_LOGIN             : u'Please login.',
    PARAM_ERROR           : u'Request param error.',
    MODULE_CODE_NONE      : u'module code is null.',
    ACTION_CODE_NONE      : u'action code is null.',
    PAGESIZE_TOO_LARGE    : u'page size too large.',
}

