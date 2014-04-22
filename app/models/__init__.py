# -*- coding: utf-8 -*-

from .. import app
from sqlalchemy import Table, MetaData, Column, ForeignKey, Integer, String, BigInteger, Date, Text, Boolean, Float
from sqlalchemy.orm import mapper

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class BaseModel(object):
	created_at = db.Column(db.DateTime)
	updated_at = db.Column(db.DateTime)
	def __init__(self,created_at,updated_at):
		self.created_at = created_at
		self.updated_at = updated_at

# Instantiate Social Scraper Models
#################################################################################

from socialscraper.facebook.models import User, Family, Friend, Page, CategoriesPages, Status, PagesUsers, Location
socialscraper_models = ['User', 'Family', 'Friend', 'Page', 'CategoriesPages', 'Status', 'PagesUsers', 'Location']
# __all__ = []
# metadata = MetaData()
metadata = db.metadata

def create_columns(columns):
	# columns = map(lambda x: getattr(User, x), columns)
	sqlalchemy_cols = []
	for col in columns:
		if col.primary_key and col.foreign_key:
			sqlalchemy_cols.append(Column(col.name, eval(col.type), ForeignKey(col.foreign_key_reference), primary_key=True))
		elif col.foreign_key:
			sqlalchemy_cols.append(Column(col.name, eval(col.type), ForeignKey(col.foreign_key_reference)))
		elif col.primary_key:
			sqlalchemy_cols.append(Column(col.name, eval(col.type), primary_key=True))
		else:
			sqlalchemy_cols.append(Column(col.name, eval(col.type)))
	return sqlalchemy_cols

for model in socialscraper_models:
	columns = create_columns(eval(model).get_columns())
	propeties = {}
	for column in columns:
		propeties[column.name] = column
	table = Table(eval(model).__name__.lower(), metadata, *columns)
	mapper(eval(model) , table, properties=propeties)
	# __all__.append(table)

#################################################################################


from app.models import *

# foreign keys, do them