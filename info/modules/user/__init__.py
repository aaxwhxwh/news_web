#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: __init__.py.py
@time: 2018/08/14
"""
from flask import Blueprint

user_blue = Blueprint('user_blue', __name__, url_prefix='/user')

from . import views