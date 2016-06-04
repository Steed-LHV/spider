# -*- coding: utf-8 -*-
"""
aladin.ext.uploads
================
flask上传模块
"""

import time
from datetime import date
import uuid
import os.path

from werkzeug import FileStorage, secure_filename

from aladin.helpers import make_thumb


# Extension presets

#: This just contains plain text files (.txt).
TEXT = ('txt',)

#: This contains various office document formats (.rtf, .odf, .ods, .gnumeric,
#: .abw, .doc, .docx, .xls, and .xlsx). Note that the macro-enabled versions
#: of Microsoft Office 2007 files are not included.
DOCUMENTS = tuple('rtf odf ods gnumeric abw doc docx xls xlsx'.split())

#: This contains basic image types that are viewable from most browsers (.jpg,
#: .jpe, .jpeg, .png, .gif, .svg, and .bmp).
#IMAGES = tuple('jpg jpe jpeg png gif svg bmp'.split())
IMAGES = tuple('jpg jpeg png bmp'.split())

#: This contains audio file types (.wav, .mp3, .aac, .ogg, .oga, and .flac).
AUDIO = tuple('wav mp3 aac ogg oga flac'.split())

#: This is for structured data files (.csv, .ini, .json, .plist, .xml, .yaml,
#: and .yml).
DATA = tuple('csv ini json plist xml yaml yml'.split())

#: This contains various types of scripts (.js, .php, .pl, .py .rb, and .sh).
#: If your Web server has PHP installed and set to auto-run, you might want to
#: add ``php`` to the DENY setting.
SCRIPTS = tuple('js php pl py rb sh'.split())

#: This contains archive and compression formats (.gz, .bz2, .zip, .tar,
#: .tgz, .txz, and .7z).
ARCHIVES = tuple('gz bz2 zip tar tgz txz 7z'.split())

#: This contains shared libraries and executable files (.so, .exe and .dll).
#: Most of the time, you will not want to allow this - it's better suited for
#: use with `AllExcept`.
EXECUTABLES = tuple('so exe dll'.split())

# 其它类型的
OTHER = tuple('apk '.split())

#: The default allowed extensions - `TEXT`, `DOCUMENTS`, `DATA`, and `IMAGES`.
DEFAULTS = TEXT + DOCUMENTS + IMAGES + DATA + OTHER

class UploadNotAllowed(Exception):
    """
    This exception is raised if the upload was not allowed. You should catch
    it in your view code and display an appropriate message to the user.
    """


def tuple_from(*iters):
    return tuple(itertools.chain(*iters))


def extension(filename):
    return filename.rsplit('.', 1)[-1]


def lowercase_ext(filename):
    if '.' in filename:
        main, ext = filename.rsplit('.', 1)
        return main + '.' + ext.lower()
    else:
        return filename.lower()


def addslash(url):
    if url.endswith('/'):
        return url
    return url + '/'

def file_allowed(storage, allowed=IMAGES):
    """
    判断文件类型是否允许上传
    @return boolean
    """
    basename = lowercase_ext(secure_filename(storage.filename))
    ext = extension(basename)
    return (ext in allowed)
    

class UploadSet(object):
    """
    文件上传对象
    @param name 上传分类名
    @param prefix_url 前辍url 如: http://img0.paytag.cn/
    @param save_dest 保存到磁盘的绝对路径 如: /data/www/img0.paytag.cn/
    @param extensions 允许上传的文件类型
    """
    def __init__(self, name, prefix_url, save_dest, extensions=DEFAULTS):
        if not name.isalnum():
            raise ValueError("Name must be alphanumeric (no underscores)")
        self.name = name
        self.prefix_url = prefix_url
        self.save_dest = save_dest
        self.extensions = extensions

        self.target = ''
        self.today_folder = ''
        self.target_folder = None

    def path(self):
        """
        获取保存的绝对路径文件名
        @return path => /data/www/img0.paytag.cn/logo/2013-05-27/96c3ac40-c785-11e2-880c-c01885e4eab0.jpg
        """
        return self.target

    def file_allowed(self, basename):
        ext = extension(basename)
        return (ext in self.extensions)

    def save(self, storage):
        """
        保存文件到磁盘，返回绝对url.
        @param storage werkzeug.FileStorage
        @return url => http://img0.paytag.cn/logo/2013-05-27/96c3ac40-c785-11e2-880c-c01885e4eab0.jpg
        """
        if not isinstance(storage, FileStorage):
            raise TypeError("storage must be a werkzeug.FileStorage")

        folder = "%s" % date.today()
        name = "%s" % uuid.uuid4()
        basename = lowercase_ext(secure_filename(storage.filename))
        basename = name + '.' + extension(basename)
        
        if not self.file_allowed(basename):
            raise UploadNotAllowed()

        # 目标目录不存在，则创建
        target_folder = os.path.join(self.save_dest, self.name, folder)
        self.target_folder = target_folder
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        target = os.path.join(target_folder, basename)
        storage.save(target)

        self.target = target
        self.today_folder = folder

        uri = self.name + '/' + self.today_folder + '/' + basename
        return self.prefix_url + uri

    def thumb(self, width=0, height=0, quality=80):
        """
        等比缩放，生成缩略图, 返回绝对url.
        @param width    缩略图宽度
        @param height   缩略图高度
        @param quality  品质
        @return         url => http://img0.paytag.cn/logo/2013-05-27/96c3ac40-c785-11e2-880c-c01885e4eab0.jpg_480x320.jpg
        """
        thumb_name = make_thumb(self.target, width, height, quality)
        uri = self.name + '/' + self.today_folder + '/' + thumb_name
        return self.prefix_url + uri

    def clear():
        self.target = ''
        self.today_folder = ''

    def url_to_target(self, url):
        """根据url获取目标存放路径"""
        basename = url[url.rfind('/')+1:]
        return os.path.join(self.target_folder, basename)

    @property
    def size(self):
        """获取原始图片宽度和高度
        :return (width, height)
        """
        try:
            import Image
        except Exception, e:
            from PIL import Image

        im = Image.open(self.path())
        return im.size

upload = {}
def init_upload_app(app):
    """
    初始化app上传组件
    """
    upload_host_config = app.config['UPLOAD_HOST_CONFIG']
    upload_save_config = app.config['UPLOAD_SAVE_CONFIG']

    for (hostname,hostinfo) in upload_host_config.items():
        for saveinfo in upload_save_config:
            objname = saveinfo['objname']
            upload_type = saveinfo['upload_type']
            upload_obj = UploadSet(objname, hostinfo['host'], hostinfo['dest'], upload_type)
            hostinfo[objname] = upload_obj

        upload[hostname] = hostinfo

def get_uploadinfo(tid=0):
    """
    获取上传Upload信息，如果tid不大于0，则用时间取模分割
    :param tid 第三方id
    """
    upload_keys = sorted(upload.keys())
    if tid <= 0:
        tid = int(time.time())
    upload_index = tid%(len(upload_keys))
    upload_hostname = upload_keys[upload_index]
    return upload.get(upload_hostname)

