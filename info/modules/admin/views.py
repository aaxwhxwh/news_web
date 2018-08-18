#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/17
"""
from datetime import datetime, timedelta

from flask import render_template, current_app, jsonify, session, g, request, url_for, redirect

from info import db
from info.models import User, News, Category
from info.utils.response_code import RET
from . import admin_blue
from info.utils.commons import login_status
import time


@admin_blue.before_request
def check_admin():
    if not request.url.endswith(url_for('admin_blue.admin_login')):
        is_admin = session.get('is_admin', False)
        user_id = session.get('user_id')

        if not user_id or not is_admin:
            return redirect('/')


@admin_blue.route('/index')
@login_status
def admin_index():
    user = g.user
    return render_template('admin/index.html', data=user.to_dict())


@admin_blue.route('/', methods=["GET", "POST"])
def admin_login():

    if request.method == "GET":
        user_id = session.get('user_id')
        is_admin = session.get('is_admin')
        if user_id and is_admin:
            return redirect(url_for('admin_blue.admin_index'))

        return render_template('admin/login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if not all([username, password]):
        return render_template('admin/login.html', errmsg="参数缺失")

    try:
        admin = User.query.filter_by(mobile=username, is_admin=True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="数据库读取错误")

    if not admin or not admin.check_password(password):
        return render_template('admin/login.html', errmsg="用户名或密码错误")

    session['user_id'] = admin.id
    session['nick_name'] = admin.nick_name
    session['mobile'] = admin.mobile
    session['is_admin'] = admin.is_admin

    return redirect(url_for('admin_blue.admin_index'))


@admin_blue.route('/user_count')
def user_count():
    
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户总数失败")
    
    mon_count = 0
    t = time.localtime()
    mon_begin_date_str = "%d-%02d-01" % (t.tm_year, t.tm_mon)
    mon_begin_date = datetime.strptime(mon_begin_date_str, '%Y-%m-%d')

    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time > mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="用户数据查询失败")

    day_count = 0
    today_str = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    today = datetime.strptime(today_str, '%Y-%m-%d')

    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > today).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="用户数据查询失败")

    active_count = []
    active_time = []

    now_start_date_str = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    now_start_date = datetime.strptime(now_start_date_str, '%Y-%m-%d')

    for d in range(0, 31):
        start_date = now_start_date - timedelta(days=d)
        end_date = now_start_date - timedelta(days=d-1)
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= start_date, User.last_login < end_date).count()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

        active_time.append(datetime.strftime(start_date, '%Y-%m-%d'))
        active_count.append(count)

    active_count.reverse()
    active_time.reverse()
    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_time": active_time,
        "active_count": active_count
    }
        
    return render_template('admin/user_count.html', data=data)


@admin_blue.route('/user_list')
def user_list():
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')

    try:
        page, per_page = int(page), int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="请求参数格式错误")

    try:
        paginate = User.query.filter().paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    if not paginate:
        return jsonify(errno=RET.NODATA, errmsg="用户列表为空")

    total_pages = paginate.pages
    current_page = paginate.page
    users = paginate.items

    user_list = []
    for user in users:
        user_list.append(user)
    print(user_list)
    data = {
        "user_list": user_list,
        "total_page": total_pages,
        "current_page": current_page
    }
    return render_template('admin/user_list.html', data=data)


@admin_blue.route('/news_review')
def news_review():
    current_page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    try:
        current_page, per_page = int(current_page), int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="请求参数格式错误")

    try:
        paginate = News.query.filter_by(status=1).order_by(News.create_time.desc()).paginate(current_page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    current_page = paginate.page
    total_page = paginate.pages
    news = paginate.items

    news_list = []
    for new in news:
        news_list.append(new)

    data = {
        "news_list": news_list,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template('admin/news_review.html', data=data)


@admin_blue.route('/news_edit')
def news_edit():
    current_page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    try:
        current_page, per_page = int(current_page), int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="请求参数格式错误")

    try:
        paginate = News.query.filter_by(status=1).order_by(News.create_time.desc()).paginate(current_page, per_page,
                                                                                             False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    current_page = paginate.page
    total_page = paginate.pages
    news = paginate.items

    news_list = []
    for new in news:
        news_list.append(new)

    data = {
        "news_list": news_list,
        "current_page": current_page,
        "total_page": total_page
    }

    return render_template('admin/news_edit.html', data=data)


@admin_blue.route('/news_type')
def news_type():
    return render_template('admin/news_type.html')


@admin_blue.route('/news_review_detail/<int:news_id>', methods=["GET", "POST"])
def news_review_detail(news_id):
    if request.method == "GET":
        try:
            new = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

        if not new:
            return jsonify(errno=RET.NODATA, errmsg="查询新闻为空")

        data = {
            "new": new
        }

        return render_template('admin/news_review_detail.html', data=data)

    news_id = request.json.get('news_id')
    action = request.json.get('action')
    reason = request.json.get('reason')

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="请求参数不完整")

    try:
        new = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

    if not new:
        return jsonify(errno=RET.NODATA, errmsg="该新闻不存在")

    if action == "reject":
        if not reason:
            return jsonify(errno=RET.NODATA, errmsg="请输入审核不通过原因")
        else:
            new.status = '-1'
            new.reason = reason

    else:
        new.status = '0'

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库连接失败")

    return jsonify(errno=RET.OK, errmsg="审核已完成")


@admin_blue.route('/news_edit_detail/<int:news_id>', methods=["GET", "POST"])
def news_edit_detail(news_id):
    if request.method == "GET":
        try:
            new = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

        if not new:
            return jsonify(errno=RET.NODATA, errmsg="查询新闻为空")

        try:
            categorys = Category.query.filter().all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

        category_list = []
        for category in categorys:
            category_list.append(category.to_dict())

        category_list.pop(0)

        data = {
            "new": new,
            "category_list": category_list
        }
        return render_template('admin/news_edit_detail.html', data=data)

    title = request.form.get('title')

    print(title, news_id)
    return jsonify(errno=RET.OK, errmsg="修改已成功")