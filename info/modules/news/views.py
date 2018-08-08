#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/08
"""
from flask import session, render_template
from manage import app
from . import news_blue


@news_blue.route('/')
def index():
    session['name'] = 2018
    return 'index'