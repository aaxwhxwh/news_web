#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: __init__.py.py
@time: 2018/08/14
"""
from flask import Blueprint

news_blue = Blueprint('news_blue', __name__, url_prefix="/news")

from . import views