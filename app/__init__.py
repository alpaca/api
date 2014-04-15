# -*- coding: utf-8 -*-

import os, sys, logging, site
from flask import Flask
from . import settings
from . import environment

# Allow importing libraries from lib folder

app = Flask(__name__)
app.config.from_object(settings.config)

from . import models
from . import controllers
from . import routes

if not app.debug:
    app.logger.setLevel(logging.INFO)
    settings.log_handler.setLevel(logging.INFO)
else:
    app.logger.setLevel(logging.DEBUG)
    settings.log_handler.setLevel(logging.DEBUG)

app.logger.addHandler(settings.log_handler)

from .models import db
from .models.tweet import Tweet
from .models.twitter_user import TwitterUser

# Example SQLAlchemy Use

# from sqlalchemy.exc import IntegrityError
# # add something to the database...
# try:
# 	db.session.add(User(1,'TestUser','pwhash'))
# 	db.session.commit()
# # ...and retrieve it!
# except IntegrityError:
# 	db.session.rollback()

# print User.query.filter_by(username='TestUser').first()