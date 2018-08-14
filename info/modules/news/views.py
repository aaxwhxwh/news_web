#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/14
"""
from flask import request, jsonify, current_app, render_template, g

from info.models import News
from info.utils.commons import login_status
from info.utils.response_code import RET
from . import news_blue


@news_blue.route('/')
def get_news():
    category_id = request.args.get('category_id', '1')
    current_page = request.args.get('current_page', '1')
    per_page = request.args.get('per_page', '10')

    try:
        current_page, per_page = int(current_page), int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="请求参数格式错误")

    category_list = []
    if category_id != "1":
        category_list.append(News.category_id == category_id)

    try:
        news = News.query.filter(*category_list).order_by(News.create_time.desc()).paginate(current_page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg="数据库读取失败")

    all_news = news.items
    total_page = news.pages
    current_page = news.page

    news_list = []
    for new in all_news:
        news_list.append(new.to_dict())

    data = {
        "news_list": news_list,
        "total_page": total_page,
        "current_page": current_page
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)


@news_blue.route('/<int:news_id>')
@login_status
def get_new(news_id):

    try:
        new = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

    if not new:
        return jsonify(errno=RET.NODATA, errmsg="查询数据为空")

    user = g.user

    data = {
        "new": new.to_dict(),
        "user": user.to_dict()
    }
    return render_template('news/detail.html', data=data)




