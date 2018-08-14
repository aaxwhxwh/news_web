#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/12
"""
import random
from datetime import datetime
from flask import render_template, session, current_app, request, jsonify, make_response

from info import db
from info.models import User
from info.utils.commons import login_status
from info.utils.response_code import RET
from . import user_blue


@user_blue.route('/')
@login_status
def user_index():

    mobile = session.get('mobile')

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

    user_pic = user.avatar_url if user.avatar_url else '../../static/news/images/user_pic.png'

    # 获取当前用户session信息
    user_id = session.get('user_id')

    # 查询该用户信息
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    return render_template('news/user.html', data={"user_info": user.to_dict() if user else None}, user_pic=user_pic)


@user_blue.route('/user_base_info.html', methods=["POST", "GET"])
def user_base_info():
    if request.method == 'POST':
        nick_name = request.json.get('nick_name')
        gender = request.json.get('gender')
        signature = request.json.get('signature')
        if not all([nick_name, gender, signature]):
            return jsonify(errno=RET.NODATA, errmsg="信息输入不能为空")

        try:
            find_user = User.query.filter_by(nick_name=nick_name).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="获取信息失败")
        if find_user:
            return jsonify(errno=RET.DATAEXIST, errmsg="改昵称已被占用")

        # 获取当前用户session信息
        user_id = session.get('user_id')

        # 查询该用户信息
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        user.nick_name = nick_name
        user.gender = gender
        user.signature = signature
        user.update_time = datetime.now()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库写入错误")

        session['nick_name'] = nick_name

        return jsonify(errno=RET.OK, errmsg="个人信息修改成功")

    return render_template('news/user_base_info.html')


@user_blue.route('/user_pic_info.html', methods=["POST", "GET"])
def user_pic_info():
    mobile = session.get('mobile')

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

    user_pic = user.avatar_url if user.avatar_url else '../../static/news/images/user_pic.png'

    if request.method == "POST":
        pic = request.files.get('file')
        if not pic:
            return jsonify(errno=RET.NODATA, errmsg="发送数据为空")

        num = random_string()
        try:
            pic.save('./info/static/news/images/user_pic/user_pic_' + num + '.png')
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.IOERR, errmsg="文件保存错误")

        user.avatar_url = '../../static/news/images/user_pic/user_pic_' + num + '.png'

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库写入错误")

        return jsonify(errno=RET.OK)
    return render_template('news/user_pic_info.html', user_pic=user_pic)















@user_blue.route('/user_collection.html')
def user_collection():
    return render_template('news/user_collection.html')


@user_blue.route('/user_follow.html')
def user_follow():
    return render_template('news/user_follow.html')


@user_blue.route('/user_news_list.html')
def user_news_list():
    return render_template('news/user_news_list.html')


@user_blue.route('/user_news_release.html')
def user_news_release():
    return render_template('news/user_news_release.html')


@user_blue.route('/user_pass_info.html')
def user_pass_info():
    return render_template('news/user_pass_info.html')


def random_string(length=32):
    base_str = 'abcdefghijklnopqrstuvwxyz1234567890'
    return ''.join(random.choice(base_str) for i in range(length))