#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: manage.py
@time: 2018/08/08
"""

from flask_script import Manager
from info import create_app
from flask_migrate import Migrate, MigrateCommand
from info import db, models


app = create_app('develop')

manage = Manager(app)
Migrate(app, db)
manage.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manage.run()
