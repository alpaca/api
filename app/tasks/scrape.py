# -*- coding: utf-8 -*-
import os, pickle
from app.tasks import celery
from app.models import db

from socialscraper import twitter, facebook
from sqlalchemy.exc import IntegrityError

from celery.signals import worker_init

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
serialized_facebook_scraper = None

@worker_init.connect
def worker_init(*args, **kwargs):
    global serialized_browser
    # facebook_scraper.login()
    # serialized_browser = pickle.dumps(facebook_scraper.browser)
    # serialized_facebook_scraper = pickle.dumps(facebook_scraper)

# ----------------------------------------------------- #
#                        Twitter                        #
# ----------------------------------------------------- #

# @celery.task(name='scrape.twitter.followers')
# def scrape_followers(username):
#     twitter_scraper.add_user(username=twitter_username,password=twitter_password)
#     subtasks = []
#     for follower in twitter_scraper.get_followers(username):
#         #print follower.screen_name
#         sig = celery.send_task('scrape.twitter.follower', args=[follower.screen_name], queue='celery')
#         subtasks.append(sig)

#         follower_obj = TwitterUser(user_id=follower.id,screen_name=follower.username)
#         db.session.add(follower_obj)
#         try:
#             db.session.commit()
#         except IntegrityError:
#             print "Warning: Integrity Error."
#             db.session.rollback()

#     return True

# @celery.task(name='scrape.twitter.follower')
# def scrape_follower(username):
#     scraper = twitter.TwitterScraper()
#     tweets = scraper.get_feed_by_screen_name(username)
#     # write to DB

#     for tweet in tweets:
#         tweet_obj = Tweet(id=tweet.id,
#                           timestamp=tweet.timestamp,
#                           screen_name=username,
#                           content=tweet.content)
#         db.session.add(tweet_obj)
#         try:
#             db.session.commit()
#         except IntegrityError:
#             print "Warning: Integrity Error."
#             db.session.rollback()
#     return True

# ------------------------------------------------------ #
#                        Facebook                        #
# ------------------------------------------------------ #

from ..models import FacebookUser, FacebookPage

@celery.task(name='scrape.facebook.page')
def scrape_page(username):
    # facebook_scraper = pickle.loads(serialized_facebook_scraper)
    facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
    facebook_scraper.add_user(email=facebook_username, password=facebook_password)
    facebook_scraper.pick_random_user()
    page_id = facebook_scraper.get_graph_id(username)
    
    if not FacebookPage.query.get(page_id):
        page = FacebookPage(page_id=page_id, username=username)
        db.session.add(page)
        db.session.commit()

    # celery.send_task('scrape.facebook.page.about', args=[username,uid], queue='celery')
    celery.send_task('scrape.facebook.page.likes', args=[username,page_id], queue='celery')
    # celery.send_task('scrape.facebook.fan.timeline', args=[username], queue='celery')

@celery.task(name='scrape.facebook.fan')
def scrape_fan(username):
    # facebook_scraper = pickle.loads(serialized_facebook_scraper)
    facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
    facebook_scraper.add_user(email=facebook_username, password=facebook_password)
    facebook_scraper.pick_random_user()
    uid = facebook_scraper.get_graph_id(username)
    
    if not FacebookUser.query.get(uid):
        user = FacebookUser(uid=uid, username=username)
        db.session.add(user)
        db.session.commit()

    celery.send_task('scrape.facebook.fan.about', args=[username,uid], queue='celery')
    celery.send_task('scrape.facebook.fan.likes', args=[username,uid], queue='celery')
    # celery.send_task('scrape.facebook.fan.timeline', args=[username], queue='celery')

@celery.task(name='scrape.facebook.fan.about')
def scrape_fan_about(username,uid):
    # facebook_scraper = pickle.loads(serialized_facebook_scraper)
    facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
    facebook_scraper.add_user(email=facebook_username, password=facebook_password)
    facebook_scraper.pick_random_user()
    result = facebook_scraper.get_about(username)
    # result = facebook_scraper.get_about(username, graph_id=uid)

    print result

    # Find better way to do this!!! Mad ugly to repeat this code.
    user = FacebookUser(
        uid=result.uid, 
        username=result.username, 
        email=result.email, 
        birthday=result.birthday, 
        sex=result.sex, 
        college=result.college, 
        employer=result.employer,
        highschool=result.highschool,
        currentcity=result.currentcity,
        hometown=result.hometown
    )

    db.session.merge(user)
    db.session.commit()
    return result

from flask import current_app

import pdb

@celery.task(name='scrape.facebook.fan.likes')
def scrape_fan_likes(username,uid):
    # facebook_scraper = pickle.loads(serialized_facebook_scraper)
    facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
    facebook_scraper.add_user(email=facebook_username, password=facebook_password)
    facebook_scraper.pick_random_user()
    pages = []
    results = []
    for result in facebook_scraper.graph_search(username, "pages-liked", graph_id=uid):
        print result.page_id
        print result.username
        page = FacebookPage(
            page_id=result.page_id,
            username=result.username,
            url=result.url,
            name=result.name
        )
        page.users.append(FacebookUser.query.get(uid))
        db.session.merge(page)
        db.session.commit()
        pages.append(page)
        results.append(result)
        print page.username
    return results

@celery.task(name='scrape.facebook.page.likes')
def scrape_page_likes(username,page_id):
    # facebook_scraper = pickle.loads(serialized_facebook_scraper)
    facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
    facebook_scraper.add_user(email=facebook_username, password=facebook_password)
    facebook_scraper.pick_random_user()
    users = []
    results = []
    for result in facebook_scraper.graph_search(username, "likers", graph_id=page_id):
        user = FacebookUser(
            uid=result.uid,
            username=result.username,
            # profile_url=result.url,
            name=result.name,
        )
        user.pages.append(FacebookPage.query.get(page_id))
        db.session.merge(user)
        db.session.commit()
        users.append(user)
        results.append(result)
    return results

@celery.task(name='scrape.facebook.db.about')
def scrape_db_about(username):
    # facebook_scraper = pickle.loads(serialized_facebook_scraper)
    facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
    facebook_scraper.add_user(email=facebook_username, password=facebook_password)
    facebook_scraper.pick_random_user()
    for result in FacebookUser.query.filter(FacebookUser.pages.any(username=username)):
        celery.send_task('scrape.facebook.fan.about', args=[result.username,result.uid], queue='celery')

@celery.task(name='scrape.facebook.db.likes')
def scrape_db_likes(username):
    # facebook_scraper = pickle.loads(serialized_facebook_scraper)
    facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
    facebook_scraper.logout()
    # facebook_scraper.add_user(email=facebook_username, password=facebook_password)

    for result in FacebookUser.query:
        usr = result.username
        try:
            # scrape_likes_nograph(usr)
            celery.send_task('scrape.facebook.db.likes_nograph', args=[usr], queue='celery')
        except IndexError:
            print "IndexError (probably no likes)"
            continue
        # celery.send_task('scrape.facebook.db.likes_nograph', args=[usr], queue='celery')
    return

@celery.task(name='scrape.facebook.db.likes_nograph')
def scrape_likes_nograph(username):
    try:
        for item in facebook_scraper.get_pages_liked_by(username):
            name = item['name']
            link = item['link']
            page_username = item['username']
            page_id = item['uid']

            page = FacebookPage(
                page_id=page_id,
                username=page_username,
                url=link,
                name=name,
                hometown=item['hometown'],
                talking_about_count=item['talking_about_count'],
                num_likes=item['num_likes']
            )

            uid = facebook_scraper.get_graph_id(username)
            user = FacebookUser.query.get(uid)
            if not user:
                user = FacebookUser(uid=uid, username=username)
                db.session.add(user)
                db.session.commit()

            page.users.append(user)
            db.session.merge(page)
            db.session.commit()
    except ValueError, IndexError:
        print "[Caught a recognized exception (IndexError or ValueError.) It's probably fine.]"
        pass
    return