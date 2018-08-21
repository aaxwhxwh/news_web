#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/12
"""
import random
from flask import render_template, session, current_app, request, jsonify, make_response, url_for, redirect, g

from info import db, constants
from info.models import User, Category, News
from info.utils.commons import login_status
from info.utils.response_code import RET
from . import user_blue


@user_blue.route('/')
@login_status
def user_index():

    user = g.user

    if not user:
        return redirect('/')

    user_pic = user.avatar_url if user.avatar_url else '../../static/news/images/user_pic.png'

    data = {
        "user": user.to_dict(),
        "user_pic": user_pic
    }

    return render_template('news/user.html', data=data)


@user_blue.route('/user_base_info.html', methods=["POST", "GET"])
@login_status
def user_base_info():
    user = g.user

    if request.method == "GET":
        return render_template('news/user_base_info.html', data=user.to_dict())

    nick_name = request.json.get('nick_name')
    gender = request.json.get('gender')
    signature = request.json.get('signature')
    if not all([nick_name, gender, signature]):
        return jsonify(errno=RET.NODATA, errmsg="信息输入不能为空")

    if gender not in ["MAN", "WOMEN"]:
        return jsonify(errno=RET.DATAERR, errmsg="参数格式错误")

    try:
        find_user = User.query.filter_by(nick_name=nick_name).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取信息失败")
    if find_user:
        return jsonify(errno=RET.DATAEXIST, errmsg="改昵称已被占用")

    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库写入错误")

    session['nick_name'] = nick_name

    return jsonify(errno=RET.OK, errmsg="个人信息修改成功")


@user_blue.route('/user_pic_info.html', methods=["POST", "GET"])
@login_status
def user_pic_info():
    user = g.user
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
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库写入错误")

        return jsonify(errno=RET.OK, user_pic=user_pic)
    return render_template('news/user_pic_info.html', user_pic=user_pic)


@user_blue.route('/user_collection.html', methods=["GET"])
@login_status
def user_collection():

    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    current_page = request.args.get('p', '1')

    try:
        current_page = int(current_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="请求格式错误")

    try:
        paginate = user.collection_news.paginate(current_page, constants.USER_COLLECTION_MAX_NEWS, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    total_page = paginate.pages
    current_page = paginate.page
    news = paginate.items
    print(news)

    news_list = []
    for new in news:
        news_list.append(new)

    data = {
        "news_list": news_list,
        "total_page": total_page,
        "current_page": current_page
    }
    return render_template('news/user_collection.html', data=data)


@user_blue.route('/user_follow.html', methods=["GET", "POST"])
@login_status
def user_follow():

    user = g.user

    if request.method == "GET":
        cur_page = request.args.get('page')

        try:
            paginate = user.followers.paginate(cur_page, constants.USER_FOLLOWED_MAX_COUNT, False)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

        total_pages = paginate.pages
        cur_page = paginate.page
        followers = paginate.items

        follower_list = []
        for follower in followers:
            follower_list.append(follower.to_dict())

        print(follower_list)

        data = {
            "total_page": total_pages,
            "cur_page": cur_page,
            "follower_list": follower_list
        }

        return render_template('news/user_follow.html', data=data)

    author_id = request.json.get('author_id')
    action = request.json.get('action')

    if not all([author_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数输入不完整")

    if action not in ["focus", "cancel_focus"]:
        return jsonify(errno=RET.DATAERR, errmsg="参数格式错误")

    try:
        author = User.query.get(author_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

    if not author:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    if action == "focus":
        if author not in user.followers:
            user.followers.append(author)
    else:
        user.followers.remove(author)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库写入失败")

    return jsonify(errno=RET.OK, errmsg="关注成功")


@user_blue.route('/user_news_list.html')
@login_status
def user_news_list():

    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    cur_page = request.args.get('page', '1')

    try:
        cur_page = int(cur_page)
    except Exception as e:
        cur_page.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="请求参数格式错误")

    try:
        paginate = user.news_list.paginate(cur_page, constants.USER_FOLLOWED_MAX_COUNT, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="请求参数格式错误")

    total_page = paginate.pages
    cur_page = paginate.page
    news = paginate.items

    news_list = []
    for new in news:
        news_list.append(new)

    data = {
        "news_list": news_list,
        "total_page": total_page,
        "cur_page": cur_page
    }
    return render_template('news/user_news_list.html', data=data)


@user_blue.route('/user_news_release.html', methods=["GET", "POST"])
@login_status
def user_news_release():

    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    if request.method == "GET":

        news_id = request.args.get('news_id')
        news = None
        if news_id:
            try:
                news = News.query.get(news_id)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

        if not categories:
            return jsonify(errno=RET.NODATA, errmsg="无新闻分类")

        category_list = []
        for category in categories:
            category_list.append(category.to_dict())

        category_list.pop(0)
        data = {
            "category_list": category_list,
            "news": news
        }
        return render_template('news/user_news_release.html', data=data)

    title = request.form.get('title')
    digest = request.form.get('digest')
    category_id = request.form.get('category_id')
    content = request.form.get('content')
    index_image = request.files.get('index_image')

    if not all([title, digest, category_id, content, index_image]):
        return jsonify(errno=RET.PARAMERR, errmsg="提交参数缺失")

    num = random_string()
    try:
        index_image.save('./info/static/news/images/index/index' + num + '.png')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.IOERR, errmsg="文件保存错误")

    # # 读取图片数据
    # try:
    #     image_data = index_image.read()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DATAERR, errmsg="参数格式错误")

    # try:
    #     image_name = storage(image_data)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")

    news = News()
    news.title = title
    news.digest = digest
    news.category_id = category_id
    news.content = content
    # news.index_image_url = constants.QINIU... + image_name
    news.index_image_url = './info/static/news/images/index/index' + num + '.png'

    news.user_id = user.id
    news.source = '用户发布'
    news.status = 0

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库存储失败")

    return jsonify(errno=RET.OK, errmsg="新闻已提交")


@user_blue.route('/user_pass_info.html', methods=["POST", "GET"])
@login_status
def user_pass_info():

    if request.method == 'POST':
        old_passwd = request.json.get('old_passwd')
        new_passwd = request.json.get('new_passwd')

        # 判断不为空
        if not all([old_passwd, new_passwd]):
            return jsonify(errno=RET.PARAMERR, errmsg="密码输入不能为空")

        user = g.user

        if not user.check_password(old_passwd):
            return jsonify(errno=RET.PWDERR, errmsg="密码输入错误")

        user.password = new_passwd

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库存储失败")

        return jsonify(errno=RET.OK, errmsg="密码修改成功")

    return render_template('news/user_pass_info.html')


def random_string(length=32):
    base_str = 'abcdefghijklnopqrstuvwxyz1234567890'
    return ''.join(random.choice(base_str) for i in range(length))