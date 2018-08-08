#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: manage.py
@time: 2018/08/08
"""

from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'index'


if __name__ == "__main__":
    app.run()
