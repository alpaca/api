# -*- coding: utf-8 -*-

from .. import app
import re
from datetime import datetime, timedelta
from flask.ext.sqlalchemy import SQLAlchemy

from . import sqlalchemy_monkey_patch

from socialscraper import facebook, twitter
from socialscraper.adapters import adapter_sqlalchemy

db = SQLAlchemy(app)

class BaseModel(object):
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    def __init__(self,created_at,updated_at):
        self.created_at = created_at
        self.updated_at = updated_at

    def test_filter(self, criterion):
        compiler = EvaluatorCompiler()
        return compiler.process(criterion)(self)

base_classes = (db.Model, BaseModel)
fbmodels = adapter_sqlalchemy.make_models(db, base_classes)

FacebookUser = fbmodels['FacebookUser']
FacebookPage = fbmodels['FacebookPage']
FacebookPagesUsers = fbmodels['FacebookPagesUsers']
FacebookFamily = fbmodels['FacebookFamily']
FacebookFriend = fbmodels['FacebookFriend']
FacebookStatus = fbmodels['FacebookStatus']
TwitterUser = fbmodels['TwitterUser']
TwitterTweet = fbmodels['TwitterTweet']

FacebookUser.locations = db.relationship('Location', primaryjoin='FacebookUser.uid==Location.uid', foreign_keys='FacebookUser.uid', uselist=True)

# __all__ = ['FacebookUser', 'FacebookFamily', 'FacebookLocation', 'FacebookFriend', 'FacebookPage', 'FacebookStatus', 'FacebookPagesUsers', 'TwitterUser', 'TwitterTweet']
from .transactions import Transaction
from .locations import Location
from contribscraper.models import *
Contributor = make_contributor_model(db.Model)
Committee = make_committee_model(db.Model)
__all__ = ['FacebookPage', 'FacebookUser', 'FacebookPagesUsers', 'Transaction', 'Contributor', 'Committee', 'Location']

from . import *
