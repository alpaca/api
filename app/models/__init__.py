# -*- coding: utf-8 -*-

from .. import app
from sqlalchemy import Table, MetaData, Column, ForeignKey, Integer, String, BigInteger, Date, Text, Boolean, Float
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class BaseModel(object):
	created_at = db.Column(db.DateTime)
	updated_at = db.Column(db.DateTime)
	def __init__(self,created_at,updated_at):
		self.created_at = created_at
		self.updated_at = updated_at

from ..utils import get_model_properties
from socialscraper import facebook, twitter

FacebookUser = type('FacebookUser', (db.Model, BaseModel), get_model_properties(facebook.models.FacebookUser))
FacebookFamily = type('FacebookFamily', (db.Model, BaseModel), get_model_properties(facebook.models.FacebookFamily))
FacebookLocation = type('FacebookLocation', (db.Model, BaseModel), get_model_properties(facebook.models.FacebookLocation))
FacebookFriend = type('FacebookFriend', (db.Model, BaseModel), get_model_properties(facebook.models.FacebookFriend))
FacebookPage = type('FacebookPage', (db.Model, BaseModel), get_model_properties(facebook.models.FacebookPage))
FacebookStatus = type('FacebookStatus', (db.Model, BaseModel), get_model_properties(facebook.models.FacebookStatus))
FacebookPagesUsers = type('FacebookPagesUsers', (db.Model, BaseModel), get_model_properties(facebook.models.FacebookPagesUsers))

TwitterUser = type('TwitterUser', (twitter.models.TwitterUser, db.Model, BaseModel), get_model_properties(twitter.models.TwitterUser))
TwitterTweet = type('TwitterTweet', (twitter.models.TwitterTweet, db.Model, BaseModel), get_model_properties(twitter.models.TwitterTweet))

FacebookUser.pages = db.relationship('FacebookPage', secondary=FacebookPagesUsers.__table__)
FacebookPage.users = db.relationship('FacebookUser', secondary=FacebookPagesUsers.__table__)

# http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers-contacts-and-friends
FacebookUser.friends = db.relationship('FacebookUser', 
	secondary = FacebookFriend.__table__, 
	primaryjoin = (FacebookFriend.__table__.c.uid1 == FacebookUser.uid),
	secondaryjoin = (FacebookFriend.__table__.c.uid2 == FacebookUser.uid),
	backref = db.backref('facebook_friends', lazy = 'dynamic'), 
	lazy = 'dynamic'
)

# FacebookUser.locations = db.relationship('FacebookLocation') uid -> gid
# FacebookPage.locations = db.relationship('FacebookLocation') page_id -> gid

__all__ = ['FacebookUser', 'FacebookFamily', 'FacebookLocation', 'FacebookFriend', 'FacebookPage', 'FacebookStatus', 'FacebookPagesUsers', 'TwitterUser', 'TwitterTweet']

from . import *
