# -*- coding: utf-8 -*-

from .. import app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class BaseModel(object):
	created_at = db.Column(db.DateTime)
	updated_at = db.Column(db.DateTime)
	def __init__(self,created_at,updated_at):
		self.created_at = created_at
		self.updated_at = updated_at

from app.models import *