# -*- coding: utf-8 -*-

from __future__ import division
import logging, os, sys, pickle, pdb
from celery.signals import worker_init
from celery import group, chord, subtask

from socialscraper.twitter import TwitterScraper
from socialscraper.facebook import FacebookScraper

from sqlalchemy import or_, and_
from sqlalchemy.exc import DatabaseError, OperationalError

from datetime import datetime

import socket

from app.tasks import celery
from app.models import db, FacebookUser, FacebookPage, Transaction
from socialscraper.adapters.adapter_sqlalchemy import convert_result

logger = logging.getLogger(__name__)

"""

Need to fix up this code later.

Essentially, the requests session is based on a urllib3 pool which gets full if we 
try to do thousands of requests from the same session. Thus we're no longer going with
a module level facebook_scraper.

Made an issue about it:
https://github.com/shazow/urllib3/issues/384

"""

def manual_init():
    global facebook_scraper

    hostname = socket.gethostname().replace(".ece.northwestern.edu", "")

    if not os.path.isfile('facebook_scraper_' + hostname + '.pickle'):
        facebook_scraper = FacebookScraper(scraper_type='nograph')
        facebook_scraper.add_user(email=os.getenv('FACEBOOK_EMAIL'), password=os.getenv('FACEBOOK_PASSWORD'), id=os.getenv('FACEBOOK_USERID'), username=os.getenv('FACEBOOK_USERNAME'))
        facebook_scraper.pick_random_user()
        facebook_scraper.login()
        facebook_scraper.init_api()
        pickle.dump(facebook_scraper, open('facebook_scraper_' + hostname + '.pickle', 'wb'))
    else:
        facebook_scraper = pickle.load(open('facebook_scraper_' + hostname + '.pickle', "rb" ))

@worker_init.connect
def worker_init(*args, **kwargs):
    manual_init()

@celery.task()
def get_uids(limit=None): 
    return filter(lambda uid: uid, map(lambda user: user.uid, FacebookUser.query.limit(limit).all()))

@celery.task()
def get_usernames(limit=None, get='all', fname=None): 

    if get == 'file':
        return open(fname).read().splitlines()

    # All People
    elif get == 'all':
        return filter(lambda username: username, map(lambda user: user.username, FacebookUser.query.limit(limit).all()))

    # People that have no pieces of about information
    elif get == 'empty':
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

    # People that have at least one piece of about information
    elif get == 'nonempty_or':
        return filter(lambda username: username, 
            map(lambda user: user.username, 
                FacebookUser.query.filter(
                    or_(
                        FacebookUser.currentcity.isnot(None), 
                        FacebookUser.hometown.isnot(None), 
                        FacebookUser.college.isnot(None), 
                        FacebookUser.highschool.isnot(None), 
                        FacebookUser.employer.isnot(None), 
                        FacebookUser.birthday.isnot(None)
                    )
                ).limit(limit).all()
                )
            )

    # People that have all pieces of about information
    elif get == 'nonempty_and':
        return filter(lambda username: username, 
            map(lambda user: user.username, 
                FacebookUser.query.filter(
                    and_(
                        FacebookUser.currentcity.isnot(None), 
                        FacebookUser.hometown.isnot(None), 
                        FacebookUser.college.isnot(None), 
                        FacebookUser.highschool.isnot(None), 
                        FacebookUser.employer.isnot(None), 
                        FacebookUser.birthday.isnot(None)
                    )
                ).limit(limit).all()
                )
            )

    # People with likes
    elif get == 'haslikes':
        return filter(lambda username: username,
                map(lambda user: user.username,
                    FacebookUser.query.filter(FacebookUser.pages != None).limit(limit).all()
                )
            )

    # People with no likes
    elif get == 'nolikes':
        return filter(lambda username: username,
                map(lambda user: user.username,
                    FacebookUser.query.filter(FacebookUser.pages == None).limit(limit).all()
                )
            )


    # People that have at least one piece of about information BUT no likes
    elif get == 'nonempty_or_nolikes':
        return filter(lambda username: username, 
            map(lambda user: user.username, 
                FacebookUser.query.filter(
                    and_(
                        or_(
                            FacebookUser.currentcity.isnot(None), 
                            FacebookUser.hometown.isnot(None), 
                            FacebookUser.college.isnot(None), 
                            FacebookUser.highschool.isnot(None), 
                            FacebookUser.employer.isnot(None), 
                            FacebookUser.birthday.isnot(None),
                        ),
                        FacebookUser.pages == None
                    )
                ).limit(limit).all()
                )
            )

    # People that have all pieces of about information BUT no likes
    elif get == 'nonempty_and_nolikes':
        return filter(lambda username: username, 
            map(lambda user: user.username, 
                FacebookUser.query.filter(
                    and_(
                        FacebookUser.currentcity.isnot(None), 
                        FacebookUser.hometown.isnot(None), 
                        FacebookUser.college.isnot(None), 
                        FacebookUser.highschool.isnot(None), 
                        FacebookUser.employer.isnot(None), 
                        FacebookUser.birthday.isnot(None),
                        FacebookUser.pages == None
                    )
                ).limit(limit).all()
                )
            )

# change scraper_type from graphapi to nograph to see different results
@celery.task(bind=True)
def get_about(self, username):

    # facebook_scraper = pickle.load(open( "facebook_scraper.pickle", "rb" ))
    try:
        result = facebook_scraper.get_about(username)
        user = FacebookUser.query.filter_by(username=username).first()

        if not user:
            user = FacebookUser()
            convert_result(user, result)
            user.created_at = datetime.now()
            db.session.add(user)
            transact_type = 'create'
        else:
            convert_result(user, result)
            transact_type = 'update'

        user.updated_at = datetime.now()
    except Exception as e:
        transaction = Transaction(
                timestamp = datetime.utcnow(),
                transact_type = 'error',
                func = 'get_about(%s)' % username,
                ref = "%s: %s" % (
                    str(e.errno) if hasattr(e, 'errno') else 0,
                    e.strerror if hasattr(e, 'strerror') else e
                )
            )
        if 'result' in locals():
            transaction.data = str(result)
            transaction.ref = "%s.%s" % (FacebookUser.__tablename__, str(result.uid))

        db.session.add(transaction)
        db.session.commit()
        return


    ## Scrape Transaction
    
    transaction = Transaction(
        timestamp = datetime.utcnow(),
        transact_type = transact_type,
        ref = "%s.%s" % (FacebookUser.__tablename__, str(result.uid)),
        func = 'get_about(%s)' % username,
        data = str(result)
    )

    db.session.add(transaction)
    db.session.commit()

    return result

@celery.task(bind=True)
def get_likes(self, username):
    
    # TODO: move this to FacebookUser model
    #
    # from sqlalchemy.exc import DatabaseError, OperationalError
    #
    # retries method on DatabaseError or OperationalError
    # def retry(fun):
    #     @wraps(fun)
    #     def _inner(*args, **kwargs):
    #         max_retries = kwargs.pop('max_retries', 3)
    #         for retries in xrange(max_retries + 1):
    #             try:
    #                 return fun(*args, **kwargs)
    #             except (DatabaseError, OperationalError):
    #                 if retries + 1 > max_retries:
    #                     raise
    #     return _inner
    #
    # @retry
    # def get(username_or_uid):
    #   if type(username_or_uid) == int:
    #       return FacebookUser.query.get(username_or_uid)
    #   elif type(username_or_uid) == str:
    #       return FacebookUser.query.filter_by(username=username).first()
    #   else:
    #       raise

    max_retries = 3
    for retries in xrange(max_retries + 1):
        try:
            user = FacebookUser.query.filter_by(username=username).first()
            break
        except (DatabaseError, OperationalError):
            if retries + 1 > max_retries:
                raise

    if not user: raise Exception("scrape the dude's about information first plz")

    results = []

    for result in facebook_scraper.get_likes(username):
        try:
            page = FacebookPage.query.filter_by(username=result.username).first()

            if not page:
                page = FacebookPage()
                convert_result(page, result)
                page.created_at = datetime.now()
                db.session.add(page)
                transact_type = 'create'
            else:
                convert_result(page, result)
                transact_type = 'update'

            # logger.debug()
            self.update_state(state='PROGRESS', meta={'transact_type': transact_type, 'current_result': result.username, 'current_total': len(results)})

        except Exception as e:
            transaction = Transaction(
                    timestamp = datetime.utcnow(),
                    transact_type = 'error',
                    func = 'get_likes(%s)' % username,
                    ref = "%s: %s" % (
                        str(e.errno) if hasattr(e, 'errno') else 0, 
                        e.strerror if hasattr(e, 'strerror') else e
                    )
                )
            if 'result' in locals():
                transaction.data = str(result)

            # logger.debug()
            self.update_state(state='PROGRESS', meta={'transact_type': transact_type, 'current_result': result.username, 'current_total': len(results)})

            db.session.add(transaction)
            db.session.commit()
            return      

        page.updated_at = datetime.now()
        page.users.append(user)

        ## Scrape Transaction
        
        transaction = Transaction(
            timestamp = datetime.utcnow(),
            transact_type = transact_type,
            ref = "%s.%s" % (FacebookPage.__tablename__, str(result.page_id)),
            func = 'get_likes(%s)' % username,
            data = str(result)
        )

        db.session.add(transaction)
        db.session.commit()

        results.append(result)
        logger.info( "%s - %i - %s" % (username, len(results), result.username))

    return results

@celery.task()
def dmap(it, callback):
    callback = subtask(callback)
    return group(callback.clone([arg,]) for arg in it)()

# http://stackoverflow.com/questions/13271056/how-to-chain-a-celery-task-that-returns-a-list-into-a-group
# process_list = (scrape.get_users.s(10) | scrape.dmap.s(scrape.get_about.s()))
