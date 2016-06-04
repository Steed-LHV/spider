#!/usr/bin/env python
#coding=utf-8

import requests, os
import uuid
import urllib2
import time
import types
import datetime
from datetime import timedelta
import boto
from datetime import date

headers = {

    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
    'accept': "Accept:text/css,*/*;q=0.1",
    }

def download_local(img_url, image_type, retry=0, max_retry=3):
        """图片下载
        :param
         图片绝对url
        :param retry 重试次数
        :param max_retry 最大重试次数
        :return 保存到硬盘的绝对路径
        """
        if retry > max_retry:
            return ""
        today_info = date.today()
        target_path = "/media/data/images/%s/%s" % (image_type, today_info)
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        # haha.jpg => .jpg
        extname = img_url[img_url.rfind('.'):]

        # 212db7f4-c767-4581-8fd4-aeb1ea043113.jpg
        filename = '%s%s' % (uuid.uuid4(), extname)

        # /data/goods_image/2014-01-04/212db7f4-c767-4581-8fd4-aeb1ea043113.jpg
        target_filename = os.path.join(target_path, filename)

        if not os.path.exists(target_filename):
            try:
                img = requests.get(img_url, timeout=30, headers=headers)
                if img.status_code != 200:
                    raise Exception("status_code error %s" % img.status_code)
                with open(target_filename, 'w') as img_file:
                    img_file.write(img.content)
            except Exception, e:
                print('[DownloadImageException] %s, %d, %s' % (img_url, retry, e))
                time.sleep(retry + 1)
                return download_local(img_url, image_type, retry+1, max_retry)

        url = 'http://img.trend.zzkko.com/%s/%s'%(today_info, filename)
        return url


def download(img_url, image_type, retry=0, max_retry=3):
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
                img = requests.get(img_url, timeout=30, headers=headers)
                if img.status_code != 200:
                    raise Exception("status_code error %s" % img.status_code)
                img_file = open(target_filename, 'w')
                img_file.write(img.content)
                img_file.close()
            except Exception, e:
                print('[DownloadImageException] %s, %d, %s' % (img_url, retry, e))
                time.sleep(retry+1)
                download(img_url, image_type, retry+1, max_retry)
            finally:
                if img_file:
                    img_file.close()

        return target_filename

if __name__ == '__main__':
    print download_local('http://cdn.lulus.com/images/product/xlarge/1670162_269906.jpg', 'go')