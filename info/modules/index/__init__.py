#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: __init__.py.py
@time: 2018/08/08
"""
from flask import Blueprint

index_blue = Blueprint('index_blue', __name__)

from . import views