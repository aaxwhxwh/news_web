#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/11
"""
from datetime import datetime

from info.models import User
from . import passport_blue
from flask import request, jsonify, current_app, make_response, session
from info.utils.response_code import RET
from info.utils.captcha.captcha import captcha
from info import redis_store, db
from info import constants
from info.libs.yuntongxun import sms
import random
import re


@passport_blue.route('/image_code')
def get_image_code():

    image_code_id = request.args.get('image_code_id')
    if not image_code_id:
        return jsonify(errno=RET.NODATA, errmsg='uuid生成错误')
    else:
        name, text, image = captcha.generate_captcha()

    if not all([name, text, image]):
        return make_response(jsonify(errno=RET.PARAMERR, errmsg=''))
    # 在redis存储生成的验证码text与uuid
    try:
        redis_store.setex('ImageCode_'+image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='验证码图片保存失败'))

    # 发送验证码图片至前端
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response


@passport_blue.route('/sms_code', methods=['GET', 'POST'])
def send_sms():

    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')
    if not all({mobile, image_code, image_code_id}):
        return jsonify(errno=RET.PARAMERR, errmsg='提交参数有误')

    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号输入有误')

    # 数据库查找用户信息，确认该手机号是否已注册
    try:
        find_user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    if find_user:
        return jsonify(errno=RET.DATAEXIST, errmsg="用户已存在")

    try:
        redis_image_code = redis_store.get('ImageCode_'+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取验证码数据失败')

    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")

    try:
        redis_store.delete('ImageCode_'+image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    if redis_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    smsCode = '%06d' % random.randint(0, 999999)

    try:
        redis_store.setex('SMS_'+mobile, constants.SMS_CODE_REDIS_EXPIRES, smsCode)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="sms验证码写入错误")

    try:
        cpp = sms.CCP()
        resp = cpp.send_template_sms(mobile, [smsCode, constants.SMS_CODE_REDIS_EXPIRES/60], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="第三方接口错误")

    if resp == 0:
        return jsonify(errno=RET.OK)
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送失败')


@passport_blue.route('/register', methods=["POST"])
def register():

    # 获取参数 mobile, smscode, password
    mobile = request.json.get('mobile')
    sms_code = request.json.get('smscode')
    password = request.json.get('password')

    # 判断文件是否不为空
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")

    # 判断手机号格式
    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号输入有误')

    # 检查手机号是否已注册
    try:
         user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户失败")
    else:
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已注册")

    # 获取redis中短信验证码
    try:
        redis_sms_code = redis_store.get('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    # 查询数据结果是否过期
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已过期")

    # 比较短信验证码是否正确
    if redis_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    # 删除已使用的短信验证码
    try:
        redis_store.delete('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 创建数据库模型对象，写入mysql数据库
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 调用密码加密模块
    user.password = password
    # 提交用户注册信息到mysql
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 提交异常，msyql操作回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据写入失败")

    # 缓存用户信息
    session['mobile'] = mobile
    session['user_id'] = user.id
    session['nick_name'] = mobile

    # 返回成功信息
    return jsonify(errno=RET.OK, errmsg="用户注册成功")


@passport_blue.route('/login', methods=["POST"])
def login():
    # 获取参数
    mobile = request.json.get('mobile')
    password = request.json.get('password')

    # 检查参数是否完整
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机号格式
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号输入有误')

    # 查询mysql确认用户是否注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据读取失败")

    # # 判断查询的数据
    # if not user:
    #     return jsonify(errno=RET.NODATA, errmsg="用户名不存在")
    #
    # # 判断用户密码
    # if user.check_password(password):
    #     return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    # 判断用户名及密码
    if user is None or not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")

    # 保存用户登陆时间
    user.last_login = datetime.now()

    # 提交数据
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 提交异常，msyql操作回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据写入失败")

    # 写入状态信息
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name

    return jsonify(errno=RET.OK, errmsg="用户登陆成功")


@passport_blue.route('/logout', methods=["DELETE"])
def logout():
    session.pop('user_id', None)
    session.pop('nick_name', None)
    session.pop('mobile', None)

    return jsonify(errno=RET.OK, errmsg="退出登陆成功")



