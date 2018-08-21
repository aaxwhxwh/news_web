#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: views.py
@time: 2018/08/14
"""
from flask import request, jsonify, current_app, render_template, g

from info import db
from info.models import News, User, Comment, CommentLike
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

    # 获取新闻内容
    try:
        new = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

    if not new:
        return jsonify(errno=RET.NODATA, errmsg="查询数据为空")

    user = g.user

    # 获取作者信息
    author_id = new.user_id
    if author_id:
        try:
            author = User.query.get(author_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")
    else:
        author = new.source

    # 获取父级评论
    try:
        comments = Comment.query.filter_by(news_id=news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

    comment_like_ids = []
    if g.user:
        try:
            comment_ids = [comment.id for comment in comments]
            if len(comment_ids) > 0:
                comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                         CommentLike.user_id == g.user.id)
                comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)

    comment_list = []
    for comment in comments if comments else []:
        comment_dict = comment.to_dict()
        comment_dict['is_like'] = False
        if g.user and comment.id in comment_like_ids:
            comment_dict['is_like'] = True
        comment_list.append(comment_dict)

    # 判断作者被关注状态
    is_focused = False
    if user and author in user.followers:
        is_focused = True

    # 判断文章收藏状态
    is_collected = False
    if user and new in user.collection_news:
        is_collected = True

    # 获取作者被关注数
    fans_num = None
    if author in User.query.filter().all():
        try:
            fans_num = author.followed.count()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库读取失败")

    # 获取作者文章总数
    news_num = None
    if author in User.query.filter().all():
        try:
            news_num = News.query.filter_by(user_id=author_id).count()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库读取失败")

    data = {
        "new": new.to_dict(),
        "user": (user.to_dict() if user else None),
        "news_click_list": news_click_list,
        "author_id": author_id,
        "author": author,
        "is_collected": is_collected,
        "is_focused": is_focused,
        "fans_num": fans_num,
        "news_num": news_num,
        "comment_list": comment_list,

    }

    new.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

    return render_template('news/detail.html', data=data)


@news_blue.route('/news_collection', methods=["POST"])
@login_status
def news_collect():

    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    news_id = request.json.get('news_id')
    action = request.json.get('action')

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="请求数据为空")

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="执行请求格式错误")

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.DBERR, errmsg="参数范围错误")

    # 查询是否存在该新闻
    try:
        new = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻失败")

    if not new:
        return jsonify(errno=RET.NODATA, errmsg="不存在该新闻")

    if action == "collect":
        if new not in user.collection_news:
            user.collection_news.append(new)
    else:
        user.collection_news.remove(new)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库存储失败")

    return jsonify(errno=RET.OK, errmsg="收藏操作成功")


@news_blue.route('/comment', methods=["POST"])
@login_status
def news_comment():
    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    news_id = request.json.get('news_id')
    content = request.json.get('content')
    parent_id = request.json.get('parent_id')

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="参数格式错误")

    print(news_id, content, parent_id)
    print(type(news_id))

    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="请求参数缺失")

    try:
        new = News.query.get(news_id)
        print(new)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库读取错误")

    print(new)
    if not new:
        return jsonify(errno=RET.NODATA, errmsg="未找到该新闻")

    comment = Comment()
    comment.news_id = news_id
    comment.content = content
    comment.user_id = user.id
    if parent_id:
        try:
            parent_id = int(parent_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DATAERR, errmsg="参数格式错误")
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库存储错误")

    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())


@news_blue.route('/comment_like', methods=["POST"])
@login_status
def comment_like():

    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    comment_id = request.json.get('comment_id')
    action = request.json.get('action')

    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.DATAERR, errmsg="请求参数格式错误")

    try:
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="请求参数格式错误")

    try:
        comments = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    if not comments:
        return jsonify(errno=RET.NODATA, errmsg='评论不存在')

    if action == 'add':
        comment_like = CommentLike()
        comment_like.comment_id = comment_id
        comment_like.user_id = user.id
        db.session.add(comment_like)
        comments.like_count += 1
    else:
        try:
            comment_like = CommentLike.query.filter(CommentLike.comment_id==comment_id, CommentLike.user_id==user.id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

        if comment_like:
            db.session.delete(comment_like)
            comments.like_count -= 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库操作失败")

    return jsonify(errno=RET.OK, errmsg="点赞成功")






