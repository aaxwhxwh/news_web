#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: config.py
@time: 2018/08/08
"""
from redis import StrictRedis


class Config(object):

    SECRET_KEY = 'VwrDqe7gN8rDax4J7nSikmVaZbWA7wS1YVtdouJLLIRoK/xdYomdAw=='
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mysql@127.0.0.1:3306/news_web'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    HOST = "127.0.0.1"
    PORT = 6379
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 86400
    SESSION_REDIS = StrictRedis(host=HOST, port=PORT)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


config = {
    'develop': DevelopmentConfig,
    'produce': ProductionConfig
}