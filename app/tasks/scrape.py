# -*- coding: utf-8 -*-

from __future__ import division
import logging, os, sys, pickle, pdb
from celery.signals import worker_init
from celery import group, chord, subtask

from socialscraper.twitter import TwitterScraper
from socialscraper.facebook import FacebookScraper

from datetime import datetime

from app.tasks import celery
from app.models import db, FacebookUser, FacebookPage, Transaction

logger = logging.getLogger(__name__)

"""

Need to fix up this code later.

Essentially, the requests session is based on a urllib3 pool which gets full if we 
try to do thousands of requests from the same session. Thus we're no longer going with
a module level facebook_scraper.

Instead we instantiate a scraper to login to Facebook and serialize the session object.

We keep this serialized_browser at the module level and instantiate a new FacebookScraper
in each task that uses the serialized_browser as a parameter.

I should remove code that deals with pickling stuff from socialscraper. Instead unpickle
here and pass the real objects around in the library.

If I can figure out those urllib pool problems properly I won't have to do any of this stuff.

Or perhaps in the library itself I create a new session object everytime I want to do anything?
Seems like a lot of overhead because I'd need to deepcopy the logged_in cookiejar each time.

---------------------------------------

The same stuff applies for the GraphAPI although its probably overkill. In order to prevent
stale user access tokens, I run the init_api method to test whether the access token works.

I only test it in worker_init and assume it'll continue to work throughout the rest of the code.

Although, these tokens are technically for like an hour a pop so that might not be the best assumption.

"""

@worker_init.connect
def worker_init(*args, **kwargs):

    global facebook_scraper

    if not os.path.isfile('facebook_scraper.pickle'):
        facebook_scraper = FacebookScraper()
        facebook_scraper.add_user(email=os.getenv("FACEBOOK_USERNAME"), password=os.getenv("FACEBOOK_PASSWORD"))
        facebook_scraper.pick_random_user()
        facebook_scraper.login()
        facebook_scraper.init_api()
        pickle.dump(facebook_scraper, open('facebook_scraper.pickle', 'wb'))
    else:
        facebook_scraper = pickle.load(open( "facebook_scraper.pickle", "rb" ))

@celery.task()
def get_uids(limit=None): 
    return filter(lambda uid: uid, map(lambda user: user.uid, FacebookUser.query.limit(limit).all()))

@celery.task()
def get_usernames(limit=None): 
    return filter(lambda username: username, map(lambda user: user.username, FacebookUser.query.limit(limit).all()))

@celery.task()
def get_unscraped_users(limit=None):
    return filter(lambda username: username, 
        map(lambda user: user.username, 
            FacebookUser.query.filter_by(
                currentcity=None, 
                hometown=None, 
                college=None, 
                highschool=None, 
                employer=None, 
                birthday=None
            ).limit(limit).all()
            )
        )

# @celery.task()
# def get_fucked_up_users(limit=None):
#     return map(lambda user: user.username, 
#         FacebookUser.query.filter(FacebookUser.uid < xxxxx).limit(limit).all())

@celery.task()
def get_pages(limit=None): 
    return map(lambda page: page.username, FacebookPage.query.limit(limit).all())

# change scraper_type from graphapi to nograph to see different results
@celery.task()
def get_about(username):

    result = facebook_scraper.get_about(username)
    user = FacebookUser.query.filter_by(username=username).first()

    if not user:
        user = FacebookUser()
        convert_result(user, result)
        user.created_at = datetime.now()
        db.session.add(user)
    else:
        convert_result(user, result)

    user.updated_at = datetime.now()

    ## Scrape Transaction

    transact_type = 'create' if len(FacebookUser.query.filter_by(uid=result.uid).all()) == 0 else 'update'
    
    transaction = Transaction(
        timestamp = datetime.utcnow(),
        transact_type = transact_type,
        ref = "%s.%s" % (FacebookUser.__tablename__, str(result.uid)),
        func = 'get_about(%s)' % username,
        data = str(result)
    )

    db.session.add(transaction)
    db.session.commit()

    logger.info(result)
    return user

@celery.task()
def dmap(it, callback):
    callback = subtask(callback)
    return group(callback.clone([arg,]) for arg in it)()

# http://stackoverflow.com/questions/13271056/how-to-chain-a-celery-task-that-returns-a-list-into-a-group
# process_list = (scrape.get_users.s(10) | scrape.dmap.s(scrape.get_about.s()))
