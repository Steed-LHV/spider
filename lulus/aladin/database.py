#!/usr/bin/env python
#coding=utf-8

import logging
from functools import partial
from sqlalchemy import orm
from flask.ext.sqlalchemy import SQLAlchemy, get_state


log = logging.getLogger(__name__)

__all__ = ['db']

db = SQLAlchemy()
