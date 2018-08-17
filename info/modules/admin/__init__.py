#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: __init__.py.py
@time: 2018/08/17
"""
from flask import Blueprint

admin_blue = Blueprint('admin_blue', __name__, url_prefix='/admin')

from . import views