#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: manage.py
@time: 2018/08/08
"""

from flask import Flask, session
from flask_script import Manager
from config import Config, Develop, Produce
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

app = Flask(__name__)
app.config.from_object(Develop)
Session(app)
db = SQLAlchemy(app)
manage = Manager(app)


@app.route('/')
def index():
    session['name'] = 2412413
    return 'index'


if __name__ == "__main__":
    manage.run()
