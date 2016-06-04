#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import logging
import uuid
import urllib2
import time
from datetime import date

from aladin.helpers import make_thumb

class DownloadImageService(object):
    """图片service，提供下载，上传，裁剪功能"""
    def __init__(self):
        self.logger = logging.getLogger('root')

    def download(self, img_url, image_type, retry=0, max_retry=3):
        """图片下载
        :param img_url 图片绝对url
        :param retry 重试次数
        :param max_retry 最大重试次数
        :return 保存到硬盘的绝对路径
        """
        if retry > max_retry:
            return None

        target_path = "/media/data/images/%s/%s" % (image_type, date.today())
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        # haha.jpg => .jpg
        extname = img_url[img_url.rfind('.'):]

        # 212db7f4-c767-4581-8fd4-aeb1ea043113.jpg
        filename = '%s%s' % (uuid.uuid4(), extname)

        # /data/goods_image/2014-01-04/212db7f4-c767-4581-8fd4-aeb1ea043113.jpg
        target_filename = os.path.join(target_path, filename)

        if not os.path.exists(target_filename):
            img_file = None
            try:
                img = urllib2.urlopen(img_url, timeout=30)
                img_file = open(target_filename, 'w')
                img_file.write(img.read())
                img_file.close()
            except Exception, e:
                self.logger.error('[DownloadImageException] %s, %d, %s' % (img_url, retry, e))
                time.sleep(retry+1)
                self.download(img_url, image_type, retry+1, max_retry)
            finally:
                if img_file:
                    img_file.close()

        return target_filename

    def thumb(self, target_filename, width=0, height=0, quality=80):
        """生成缩略图，返回缩略图绝对路径"""
        try:
            thumb_filename = make_thumb(target_filename, width, height, quality)
            return "%s/%s" % (self.get_target_path(target_filename), thumb_filename)
        except Exception, e:
            self.logger.info("[MakeThumbException] %s" % e)
            
        return None

    def get_target_path(self, target_filename):
        p = target_filename.rfind('/')
        return target_filename[:p]

