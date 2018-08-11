#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/08
"""
from flask import session, render_template, current_app
from . import news_blue
from info import models


@news_blue.route('/')
def index():
    session['name'] = 2018
    news = models.News.query.filter(models.News.category_id == 1).all()
    print(news)
    return render_template('news/index.html', news=news)


@news_blue.route('/share')
def share():
    news = models.News.query.filter(models.News.category_id == 2).all()
    print(news)
    return render_template('news/index.html', news=news)


@news_blue.route('/bonds')
def bonds():
    news = models.News.query.filter(models.News.category_id == 3).all()
    print(news)
    return render_template('news/index.html', news=news)


@news_blue.route('/goods')
def goods():
    news = models.News.query.filter(models.News.category_id == 4).all()
    print(news)
    return render_template('news/index.html', news=news)


@news_blue.route('/foreign_currency')
def foreign_currency():
    news = models.News.query.filter(models.News.category_id == 5).all()
    print(news)
    return render_template('news/index.html', news=news)


@news_blue.route('/company')
def company():
    news = models.News.query.filter(models.News.category_id == 6).all()
    print(news)
    return render_template('news/index.html', news=news)


@news_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')

