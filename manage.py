# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand

from app import app
from app.models import db

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command("runserver", Server(host="0.0.0.0"))
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()