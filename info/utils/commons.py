#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: commons.py
@time: 2018/08/14
"""
import functools

from flask import session, g, current_app, jsonify

from info.models import User
from info.utils.response_code import RET


def index_class(index):
    if index == 0:
        return 'first'
    elif index == 1:
        return 'second'
    elif index == 2:
        return 'third'
    else:
        return


def login_status(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

        g.user = user

        return f(*args, **kwargs)
    return wrapper
