#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/08
"""
from flask import session, render_template, current_app
from . import news_blue


@news_blue.route('/')
def index():
    session['name'] = 2018
    return render_template('news/index.html')


@news_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/facicon.icon')


@news_blue.route('/regist')
def user_regist():
    return render_template('news/other.html')


@news_blue.errorhandler(404)
def error_index():
    return render_template('news/404.html')
