#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: __init__.py.py
@time: 2018/08/08
"""
from flask import Flask
from config import config, Config
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import logging
from logging.handlers import RotatingFileHandler
from redis import StrictRedis
from flask_wtf import CSRFProtect,csrf


# 日志文件设置
# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)

db = SQLAlchemy()
redis_store = StrictRedis(host=Config.HOST, port=Config.PORT, decode_responses=True)


def create_app(config_name):
    app = Flask(__name__)

    CSRFProtect(app)
    # 加载配制
    app.config.from_object(config[config_name])

    Session(app)
    db.init_app(app)

    @app.after_request
    def after_request(resp):
        csrf_token = csrf.generate_csrf()
        resp.set_cookie('csrf_token', csrf_token)
        return resp

    from info.utils.commons import index_class
    app.add_template_filter(index_class, 'index_class')

    # 注册蓝图
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue, url_prefix="/passport")
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)
    from info.modules.user import user_blue
    app.register_blueprint(user_blue)
    from info.modules.admin import admin_blue
    app.register_blueprint(admin_blue)

    return app
