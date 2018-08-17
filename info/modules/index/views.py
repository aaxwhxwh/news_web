#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/08
"""
from flask import session, render_template, current_app, jsonify

from info.models import User, News, Category
from info.utils.response_code import RET
from . import index_blue
from info import models


@index_blue.route('/')
def index():
    # 从redis中获取user_id
    user_id = session.get('user_id')

    # 新闻点击排行榜
    try:
        news_click = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    if not news_click:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据为空")

    news_click_list = []
    for new in news_click:
        news_click_list.append(new.to_dict())

    # 判断登陆状态，返回已登陆的用户信息
    user_info = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据获取失败")

        user_info = user.to_dict()

    # 获取新闻类目信息
    news_category = Category.query.filter().all()
    category_list = []
    for category in news_category:
        category_list.append(category.to_dict())

    # 整理并返回数据
    data = {
        "user_info": user_info,
        "news_click_list": news_click_list,
        "category_list": category_list,
    }
    return render_template('news/index.html', data=data)


@index_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')

