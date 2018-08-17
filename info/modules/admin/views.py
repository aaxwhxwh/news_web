#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/17
"""
from datetime import datetime, timedelta

from flask import render_template, current_app, jsonify, session, g, request, url_for, redirect

from info.models import User
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
        mon_count = User.query.filter(User.is_admin==False, User.create_time > mon_begin_date).count()
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
    if request.method == "POST":
        return render_template('admin/user_list.html')




@admin_blue.route('/news_review')
def news_review():
    return render_template('admin/news_review.html')


@admin_blue.route('/news_edit')
def news_edit():
    return render_template('admin/news_edit.html')


@admin_blue.route('/news_type')
def news_type():
    return render_template('admin/news_type.html')
