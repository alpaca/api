# -*- coding: utf-8 -*-

from __future__ import division
import logging, os, sys, pickle, pdb
from celery.signals import worker_init
from celery import group, chord, subtask
from socialscraper import twitter, facebook

from app.tasks import celery
from app.models import db, FacebookUser, FacebookPage

logger = logging.getLogger(__name__)

twitter_scraper = twitter.TwitterScraper()
twitter_username = os.getenv("TWITTER_USERNAME")
twitter_password = os.getenv('TWITTER_PASSWORD')
if twitter_username and twitter_password:
    twitter_scraper.add_user(username=twitter_username,password=twitter_password)

facebook_scraper = facebook.FacebookScraper()
facebook_username = os.getenv("FACEBOOK_USERNAME")
facebook_password = os.getenv("FACEBOOK_PASSWORD")
if facebook_username and facebook_password:
    facebook_scraper.add_user(email=facebook_username, password=facebook_password)

serialized_browser = None

@worker_init.connect
def worker_init(*args, **kwargs):
    # facebook_scraper.login()
    facebook_scraper.init_api()

    global serialized_browser
    serialized_browser = pickle.dumps(facebook_scraper.browser)

@celery.task()
def get_users(limit=None): return map(lambda user: user.username, FacebookUser.query.limit(limit).all())

@celery.task()
def get_pages(limit=None): return map(lambda page: page.username, FacebookPage.query.limit(limit).all())

@celery.task()
def get_about(username):
    about = facebook_scraper.get_about(username)
    logger.info(about)
    return about

@celery.task()
def dmap(it, callback):
    callback = subtask(callback)
    return group(callback.clone([arg,]) for arg in it)()

# http://stackoverflow.com/questions/13271056/how-to-chain-a-celery-task-that-returns-a-list-into-a-group
# process_list = (scrape.get_users.s(10) | scrape.dmap.s(scrape.get_about.s()))