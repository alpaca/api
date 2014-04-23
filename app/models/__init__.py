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

from ..utils import get_model_properties
from socialscraper import facebook, twitter

FacebookUser = type('FacebookUser', (facebook.models.FacebookUser, db.Model, BaseModel), get_model_properties(facebook.models.FacebookUser))
FacebookFamily = type('FacebookFamily', (facebook.models.FacebookFamily, db.Model, BaseModel), get_model_properties(facebook.models.FacebookFamily))
FacebookLocation = type('FacebookLocation', (facebook.models.FacebookLocation, db.Model, BaseModel), get_model_properties(facebook.models.FacebookLocation))
FacebookFriend = type('FacebookFriend', (facebook.models.FacebookFriend, db.Model, BaseModel), get_model_properties(facebook.models.FacebookFriend))
FacebookPage = type('FacebookPage', (facebook.models.FacebookPage, db.Model, BaseModel), get_model_properties(facebook.models.FacebookPage))
FacebookCategoriesPages = type('FacebookCategoriesPages', (facebook.models.FacebookCategoriesPages, db.Model, BaseModel), get_model_properties(facebook.models.FacebookCategoriesPages))
FacebookStatus = type('FacebookStatus', (facebook.models.FacebookStatus, db.Model, BaseModel), get_model_properties(facebook.models.FacebookStatus))
FacebookPagesUsers = type('FacebookPagesUsers', (facebook.models.FacebookPagesUsers, db.Model, BaseModel), get_model_properties(facebook.models.FacebookPagesUsers))

#################################################################################

__all__ = ['twitter_user', 'tweet']

from app.models import *

# foreign keys, do them