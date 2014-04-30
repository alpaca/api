# -*- coding: utf-8 -*-

from __future__ import division

import os, sys, pickle
from app.tasks import celery
from app.models import db

from time import time
from datetime import datetime
from urlparse import urlparse, parse_qs
from facebook import GraphAPI, GraphAPIError

from socialscraper import twitter, facebook
from sqlalchemy.exc import IntegrityError

from celery.signals import worker_init
from celery import group, chord

from flask import current_app

import pdb

import logging
logger = logging.getLogger('')

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

from ..models import FacebookUser, FacebookPage

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

# @celery.task(name='scrape.facebook.page')
# def scrape_page(username):
#     # facebook_scraper = pickle.loads(serialized_facebook_scraper)
#     facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
#     facebook_scraper.add_user(email=facebook_username, password=facebook_password)
#     facebook_scraper.pick_random_user()
#     page_id = facebook_scraper.get_graph_id(username)
    
#     if not FacebookPage.query.get(page_id):
#         page = FacebookPage(page_id=page_id, username=username)
#         db.session.add(page)
#         db.session.commit()

#     celery.send_task('scrape.facebook.page.about', args=[username,uid], queue='celery')
#     celery.send_task('scrape.facebook.page.likes', args=[username,page_id], queue='celery')

# @celery.task(name='scrape.facebook.fan')
# def scrape_fan(username):
#     # facebook_scraper = pickle.loads(serialized_facebook_scraper)
#     facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
#     facebook_scraper.add_user(email=facebook_username, password=facebook_password)
#     facebook_scraper.pick_random_user()
#     uid = facebook_scraper.get_graph_id(username)
    
#     if not FacebookUser.query.get(uid):
#         user = FacebookUser(uid=uid, username=username)
#         db.session.add(user)
#         db.session.commit()

#     celery.send_task('scrape.facebook.fan.about', args=[username,uid], queue='celery')
#     celery.send_task('scrape.facebook.fan.likes', args=[username,uid], queue='celery')

# @celery.task(name='scrape.facebook.fan.about')
# def scrape_fan_about(username,uid):
#     # facebook_scraper = pickle.loads(serialized_facebook_scraper)
#     facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
#     facebook_scraper.add_user(email=facebook_username, password=facebook_password)
#     facebook_scraper.pick_random_user()
#     result = facebook_scraper.get_about(username)
#     # result = facebook_scraper.get_about(username, graph_id=uid)

#     print result

#     # Find better way to do this!!! Mad ugly to repeat this code.
#     user = FacebookUser(
#         uid=result.uid, 
#         username=result.username, 
#         email=result.email, 
#         birthday=result.birthday, 
#         sex=result.sex, 
#         college=result.college, 
#         employer=result.employer,
#         highschool=result.highschool,
#         currentcity=result.currentcity,
#         hometown=result.hometown
#     )

#     db.session.merge(user)
#     db.session.commit()
#     return result

# @celery.task(name='scrape.facebook.fan.likes')
# def scrape_fan_likes(username,uid):
#     # facebook_scraper = pickle.loads(serialized_facebook_scraper)
#     facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
#     facebook_scraper.add_user(email=facebook_username, password=facebook_password)
#     facebook_scraper.pick_random_user()
#     pages = []
#     results = []
#     for result in facebook_scraper.graph_search(username, "pages-liked", graph_id=uid):
#         print result.page_id
#         print result.username
#         page = FacebookPage(
#             page_id=result.page_id,
#             username=result.username,
#             url=result.url,
#             name=result.name
#         )
#         page.users.append(FacebookUser.query.get(uid))
#         db.session.merge(page)
#         db.session.commit()
#         pages.append(page)
#         results.append(result)
#         print page.username
#     return results

# @celery.task(name='scrape.facebook.page.likes')
# def scrape_page_likes(username,page_id):
#     # facebook_scraper = pickle.loads(serialized_facebook_scraper)
#     facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
#     facebook_scraper.add_user(email=facebook_username, password=facebook_password)
#     facebook_scraper.pick_random_user()
#     users = []
#     results = []
#     for result in facebook_scraper.graph_search(username, "likers", graph_id=page_id):
#         user = FacebookUser(
#             uid=result.uid,
#             username=result.username,
#             # profile_url=result.url,
#             name=result.name,
#         )
#         user.pages.append(FacebookPage.query.get(page_id))
#         db.session.merge(user)
#         db.session.commit()
#         users.append(user)
#         results.append(result)
#     return results

# @celery.task(name='scrape.facebook.db.about')
# def scrape_db_about(username):
#     # facebook_scraper = pickle.loads(serialized_facebook_scraper)
#     facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
#     facebook_scraper.add_user(email=facebook_username, password=facebook_password)
#     facebook_scraper.pick_random_user()
#     for result in FacebookUser.query.filter(FacebookUser.pages.any(username=username)):
#         celery.send_task('scrape.facebook.fan.about', args=[result.username,result.uid], queue='celery')

# @celery.task(name='scrape.facebook.db.likes')
# def scrape_db_likes(username):
#     # facebook_scraper = pickle.loads(serialized_facebook_scraper)
#     facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser)
#     facebook_scraper.logout()
#     # facebook_scraper.add_user(email=facebook_username, password=facebook_password)

#     for result in FacebookUser.query:
#         usr = result.username
#         scrape_likes_nograph(usr)
#         # celery.send_task('scrape.facebook.db.likes_nograph', args=[usr], queue='celery')
#         # celery.send_task('scrape.facebook.db.likes_nograph', args=[usr], queue='celery')
#     return

# @celery.task(name='scrape.facebook.db.likes_nograph')
# def scrape_likes_nograph(username):
#     try:
#         for item in facebook_scraper.get_pages_liked_by(username):
#             name = item['name']
#             link = item['link']
#             page_username = item['username']
#             page_id = item['uid']

#             page = FacebookPage(
#                 page_id=page_id,
#                 username=page_username,
#                 url=link,
#                 name=name,
#                 hometown=item['hometown'],
#                 talking_about_count=item['talking_about_count'],
#                 num_likes=item['num_likes']
#             )

#             uid = facebook_scraper.get_graph_id(username)
#             user = FacebookUser.query.get(uid)
#             if not user:
#                 user = FacebookUser(uid=uid, username=username)
#                 db.session.add(user)
#                 db.session.commit()

#             page.users.append(user)
#             db.session.merge(page)
#             db.session.commit()
#     except ValueError, IndexError:
#         print "[Caught a recognized exception (IndexError or ValueError.) It's probably fine.]"
#         pass
#     return

@celery.task()
def categories():
    subtasks = []
    # pages = FacebookPage.query
    # pages = FacebookPage.query.all()[10000:] # start from 10k
    pages = reversed(FacebookPage.query.all())
    
    for p in pages:

        if "l.php" in p.url: continue
        if "pages/" in p.url:
            graph_url = 'https://graph.facebook.com/' + p.url.split('/')[-1]
        else:
            graph_url = p.url.replace('https://www', 'https://graph')
        
        subtasks.append(categories_request.s(p.page_id, graph_url))

    logger.info("Created subtasks")
    job = group(subtasks).apply_async()

@celery.task()
def categories_request(page_id, graph_url):
    p = FacebookPage.query.get(page_id)
    response = requests.get(graph_url)
    data = json.loads(response.text)
    # logger.info(data)
    if data.get('error'): raise Exception("%s" % data['error'])
    p.type = data.get('category')
    print graph_url, p.type
    db.session.merge(p)
    db.session.commit()
    return (p.name, p.type)

########################################
# List of Attributes on Pages
########################################

# data.get('username')
# data.get('can_post')
# data.get('category_list')
# data.get('press_contact')
# data.get('hometown')
# data.get('booking_agent')
# data.get('mission')
# data.get('founded')
# data.get('affiliation')
# data.get('likes')
# data.get('parking')
# data.get('general_info')
# data.get('id')
# data.get('category')
# data.get('network')
# data.get('has_added_app')
# data.get('talking_about_count')
# data.get('record_label')
# data.get('location')
# data.get('company_overview')
# data.get('is_community_page')
# data.get('personal_interests')
# data.get('website')
# data.get('bio')
# data.get('description')
# data.get('schedule')
# data.get('hours')
# data.get('phone')
# data.get('personal_info')
# data.get('birthday')
# data.get('link')
# data.get('genre')
# data.get('checkins')
# data.get('about')
# data.get('name')
# data.get('release_date')
# data.get('cover')
# data.get('were_here_count')
# data.get('is_published')


####################################################################################################

graph = GraphAPI(os.getenv('FACEBOOK_USER_TOKEN'))

NORMAL_KEYS = ['id', 'first_name', 'gender', 'last_name', 'link', 'locale', 'name', 'updated_time', 'username']

@celery.task()
def about_callback(results):
    logger.info(results)
    logger.info(sum(results))
    logger.info(len(results))
    return sum(results)/len(results)

@celery.task()
def about():
    subtasks = []
    users = FacebookUser.query #.filter_by(sex=None)
    for u in users:
        subtasks.append(about_request.s(u.username))
    logger.info("Created subtasks")
    # job = group(subtasks).apply_async()
    job = chord(subtasks)(about_callback.s()).get()
    return job

@celery.task()
def about_request(username):
    # logger.info(NORMAL_KEYS)

    try:
        profile = graph.get_object(username)
    except GraphAPIError:
        return False

    uid = profile.get('id')
    user = FacebookUser.query.get(uid)

    user.data = json.dumps(profile)

    # logger.info(profile)
    for key in profile.keys(): 
        # logger.info(key)
        if key not in NORMAL_KEYS:
            user.misc = 'True'
            return True

    user.misc = 'False'

    db.session.merge(user)
    db.session.commit()

    return False

@celery.task()
def feed_request(username):
    def get_previous(previous_url):
        previous_url_parameters = parse_qs(urlparse(previous_url).query)
        return int(previous_url_parameters['since'][0])

    def get_next(next_url):
        next_url_parameters = parse_qs(urlparse(next_url).query)
        return int(next_url_parameters['until'][0])

    # ryan.berthold
    # user = "1cupcakelady" #sys.argv[1]

    graph = GraphAPI(os.getenv('FACEBOOK_APP_TOKEN'))
    profile = graph.get_object(username)

    print profile

    until = int(time())
    while True:

        print "Getting Feed Until: " + datetime.utcfromtimestamp(until).strftime('%Y-%m-%d %H:%M:%S')
        profile = graph.get_object(username + "/feed", until=str(until))
        if profile['data'] == []:
            print "End of Results"
            break
        since = get_previous(profile['paging']['previous'])
        until = get_next(profile['paging']['next'])

        print profile['data']

        for item in profile['data']:
            print item.get('type') + ": " + item.get('story', '') + item.get('message', '')