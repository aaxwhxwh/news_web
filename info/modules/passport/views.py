#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/11
"""
from . import passport_blue
from flask import request, jsonify, current_app, make_response
from info.utils.response_code import RET
from info.utils.captcha.captcha import captcha
from info import redis_store
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


'''
发送短信验证码实现流程：
        接收前端发送过来的请求参数
        检查参数是否已经全部传过来
        判断手机号格式是否正确
        检查图片验证码是否正确，若不正确，则返回
        删除图片验证码
        生成随机的短信验证码
        使用第三方SDK发送短信验证码
:return:
'''