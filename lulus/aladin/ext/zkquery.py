#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyquery import PyQuery
from pyquery.pyquery import fromstring, no_default, PY3k
from pyquery.openers import _query
from pyquery.cssselectpatch import JQueryTranslator

from copy import deepcopy
from lxml import etree
import lxml.html
import inspect
import types
import sys

from urllib2 import urlopen


def _urllib(url, kwargs):
    method = kwargs.get('method')
    timeout = kwargs.get('timeout')
    url, data = _query(url, method, kwargs)
    if timeout:
        return urlopen(url, data, timeout)
    return urlopen(url, data)

def url_opener(url, kwargs):
    return _urllib(url, kwargs)


class ZzkkoQuery(PyQuery):
    """修正PyQuery没有设置超时问题
    """

    _translator_class = JQueryTranslator

    def __init__(self, *args, **kwargs):
        html = None
        elements = []
        self._base_url = None
        self.parser = kwargs.pop('parser', None)

        if (len(args) >= 1 and
                (not PY3k and isinstance(args[0], basestring) or
                (PY3k and isinstance(args[0], str))) and
                args[0].split('://', 1)[0] in ('http', 'https')):
            kwargs['url'] = args[0]
            if len(args) >= 2:
                kwargs['data'] = args[1]
            args = []

        if 'parent' in kwargs:
            self._parent = kwargs.pop('parent')
        else:
            self._parent = no_default

        if 'css_translator' in kwargs:
            self._translator = kwargs.pop('css_translator')
        elif self.parser in ('xml',):
            self._translator = self._translator_class(xhtml=True)
        elif self._parent is not no_default:
            self._translator = self._parent._translator
        else:
            self._translator = self._translator_class(xhtml=False)

        namespaces = kwargs.pop('namespaces', {})

        if kwargs:
            # specific case to get the dom
            if 'filename' in kwargs:
                html = open(kwargs['filename'])
            elif 'url' in kwargs:
                url = kwargs.pop('url')
                if 'opener' in kwargs:
                    opener = kwargs.pop('opener')
                    html = opener(url, **kwargs)
                else:
                    html = url_opener(url, kwargs)
                if not self.parser:
                    self.parser = 'html'
                self._base_url = url
            else:
                raise ValueError('Invalid keyword arguments %s' % kwargs)

            elements = fromstring(html, self.parser)
            # close open descriptor if possible
            if hasattr(html, 'close'):
                try:
                    html.close()
                except:
                    pass

        else:
            # get nodes

            # determine context and selector if any
            selector = context = no_default
            length = len(args)
            if length == 1:
                context = args[0]
            elif length == 2:
                selector, context = args
            else:
                raise ValueError(
                    "You can't do that. Please, provide arguments")

            # get context
            if isinstance(context, basestring):
                try:
                    elements = fromstring(context, self.parser)
                except Exception:
                    raise
            elif isinstance(context, self.__class__):
                # copy
                elements = context[:]
            elif isinstance(context, list):
                elements = context
            elif isinstance(context, etree._Element):
                elements = [context]

            # select nodes
            if elements and selector is not no_default:
                xpath = self._css_to_xpath(selector)
                results = []
                for tag in elements:
                    results.extend(tag.xpath(xpath, namespaces=namespaces))
                elements = results

        list.__init__(self, elements)


