#!/usr/bin/env python
#coding=utf-8
import os
from flask import request, current_app, g

from aladin.helpers import log_error, log_debug

class SessionManager(object):
    """session管理"""

    # session的cookie名称
    __session_cookie_name__ = 'zzkko_session'

    # session缓存过期时间30天，memcached支持最大过期时间为30天
    __session_cache_expire__ = 30*24*60*60

    def __init__(self):
        """初始化函数"""

        self.cookie_name = 'zzkko_session'
        self.expire = 30*24*60*60

        g.session = g.get('session', {})

        self.session_new = False
        self.memcache_session_id = request.cookies.get(self.cookie_name, None)

        #log_debug('session:%s, memcache_session_id:%s' % (g.session, self.memcache_session_id))

        if not g.session and self.memcache_session_id:
            log_debug('[CacheInfo] get session:%s' % (self.memcache_session_id, ))
            try:
                g.session = current_app.cache.get(self.memcache_session_id)
                if g.session is None:
                    g.session = {}

            except Exception, e:
                log_error('[SessionManagerError] cache_id:%s, %s' % (self.memcache_session_id, e))

        if self.memcache_session_id is None:
            self.session_new = True
            self.memcache_session_id = os.urandom(40).encode('hex')        


    def get(self, session_name, default=None):
        """获取session数据
        :param session_name
        :param default 默认值
        :return object
        """

        return g.session.get(session_name, default)


    def set(self, session_name, session_value, is_commit=True):
        """设置session数据
        :param string session_name 
        :param object session_value 
        :param boolean is_commit 是否立即提交到memcached
        """
        g.session[session_name] = session_value

        if is_commit:
            self.commit()


    def commit(self):
        """提交到memcached"""
        try:
            current_app.cache.set(self.memcache_session_id, g.session, self.expire)
        except Exception, e:
            log_error('[SessionManagerError] set cache. cache_id:%s, %s' % 
                (self.memcache_session_id, e))


    def set_cookie(self, response):
        if self.session_new:
            response.set_cookie(self.cookie_name, self.memcache_session_id, self.expire)

    
    def delete_session(self):
        """删除session"""
        if not self.session_new:
            try:
                current_app.cache.delete(self.memcache_session_id)
                g.session = {}
            except Exception, e:
                log_error('[SessionManagerError] delete cache. cache_id:%s, %s' 
                    % (self.memcache_session_id, e))
            
