# -*- coding: utf-8 -*-

from .. import app
import re
from datetime import datetime, timedelta
from sqlalchemy import Table, MetaData, Column, ForeignKey, Integer, String, BigInteger, Date, Text, Boolean, Float
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList, ClauseList
from sqlalchemy.sql.operators import ilike_op, between_op

### START MONKEY PATCH ###

# NOTE1: CHANGE THIS TO SUBCLASS. MONKEY PATCHING IS STUPID WHAT WAS I THINKING???

# NOTE2: THE POINT OF THIS CODE WAS TO EFFICIENTLY CHECK FILTERS AGAINST SQL OBJECTS
# ALREADY LOADED IN THE DATABSE, BUT CERTAIN QUERIES THAT USE THE LOCATIONS TABLE
# OR PAGES (LIKES) CANNOT BE DONE IN THIS MANNER.

# Because of NOTE2, I'm abandoning this approach and trying to create subqueries 
# for each user instead. The end result is that I MUST do this through postgres
# somehow so that postgres can handle things like ilike_op or between_op and I don't
# need to write custom code for everything.

from sqlalchemy.orm.evaluator import EvaluatorCompiler, UnevaluatableError
from sqlalchemy.sql import sqltypes
orignal_process = EvaluatorCompiler.process
original_visit_binary = EvaluatorCompiler.visit_binary
original_visit_clauselist = EvaluatorCompiler.visit_clauselist

def patched_process(self, clause):
    try:
        truth_value = orignal_process(self, clause)
        if truth_value == None:
            raise

        return truth_value
    except UnevaluatableError:

        if  clause.__visit_name__ == "select":
            print "i need to handle this special case for select clause"
            print "this is happening when i'm using a relatinship on the"
            print "user model like pages or locations"
            import pdb; pdb.set_trace()

        else:
            raise

def patched_visit_binary(self, clause):
    try:
        truth_value = original_visit_binary(self, clause)
        if truth_value == None:
            raise
        return truth_value
    except UnevaluatableError:
        
        column, bind_parameter = clause.get_children()

        if clause.operator == ilike_op:
            if type(column.type) == sqltypes.String and type(bind_parameter.type) == sqltypes.String:
                return lambda obj: re.search(bind_parameter.value, getattr(obj, column.name), re.IGNORECASE) if getattr(obj, column.name) else False
            else:
                raise
        elif clause.operator == between_op:

            if type(bind_parameter) == ClauseList:
                if len(bind_parameter.clauses) == 2:

                    clause1 = bind_parameter.clauses[0]
                    clause2 = bind_parameter.clauses[1]
                    
                    if type(clause1.type) == sqltypes.DateTime and type(clause2.type) == sqltypes.DateTime:
                        
                        date1 = clause1.value
                        date2 = clause2.value

                        def compare_date(obj):
                            obj_date = getattr(obj, column.name)
                            # print "date1", date1
                            # print "date2", date2
                            # print "obj_date", obj_date
                            # print date1.date() <= obj_date
                            # print obj_date < date2.date()
                            # print date1.date() <= obj_date and obj_date < date2.date()

                            # truth_value = (obj_date < date2.date()) and (date1.date() <= obj_date)

                            # print date1.date()
                            # print date2.date()
                            # print obj_date

                            if obj_date == None: return False

                            return (obj_date < date2.date()) and (date1.date() <= obj_date)
                        return compare_date
                    else:
                        raise
                else:
                    raise 
            else:
                raise
        else:
            raise

EvaluatorCompiler.process = patched_process
EvaluatorCompiler.visit_binary = patched_visit_binary

#### END MONKEY PATCH ###

db = SQLAlchemy(app)

class BaseModel(object):
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    def __init__(self,created_at,updated_at):
        self.created_at = created_at
        self.updated_at = updated_at

    def to_json(self):
        d = {}
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            d[column.name] = val
        return d

    def test_filter(self, criterion):
        compiler = EvaluatorCompiler()
        truth_value = compiler.process(criterion)(self)
        # if truth_value == None:
            # print "fuck me"
        return truth_value
        # return compiler.process(criterion)(self)

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
# FacebookUser.friends = db.relationship('FacebookUser', 
#   secondary = FacebookFriend.__table__, 
#   primaryjoin = (FacebookFriend.__table__.c.uid1 == FacebookUser.uid),
#   secondaryjoin = (FacebookFriend.__table__.c.uid2 == FacebookUser.uid),
#   backref = db.backref('facebook_friends', lazy = 'dynamic'), 
#   lazy = 'dynamic'
# )

# FacebookUser.locations = db.relationship('FacebookLocation') uid -> gid
# FacebookPage.locations = db.relationship('FacebookLocation') page_id -> gid

FacebookUser.locations = db.relationship('Location', primaryjoin='FacebookUser.uid==Location.uid', foreign_keys='FacebookUser.uid', uselist=True)

def to_json(self):
    dic = super(FacebookUser,self).to_json()
    dic['pages'] = [pg.to_json() for pg in self.pages]
    dic['locations'] = [loc.to_json() for loc in self.locations]
    return dic

FacebookUser.to_json = to_json

# __all__ = ['FacebookUser', 'FacebookFamily', 'FacebookLocation', 'FacebookFriend', 'FacebookPage', 'FacebookStatus', 'FacebookPagesUsers', 'TwitterUser', 'TwitterTweet']
from .transactions import Transaction
from .locations import Location
from contribscraper.models import *
Contributor = make_contributor_model(db.Model)
Committee = make_committee_model(db.Model)
__all__ = ['FacebookPage', 'FacebookUser', 'FacebookPagesUsers', 'Transaction', 'Contributor', 'Committee', 'Location']

from . import *
