#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: __init__.py.py
@time: 2018/08/11
"""

from flask import Blueprint

passport_blue = Blueprint('passport_blue', __name__)

from . import views