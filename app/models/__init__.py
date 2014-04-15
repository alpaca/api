# -*- coding: utf-8 -*-

from .. import app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

from app.models import *