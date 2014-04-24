# -*- coding: utf-8 -*-
import os
from app.tasks import celery
from app.models import db

from app.models import TwitterUser, TwitterTweet
from app.models import FacebookUser, FacebookFamily, FacebookLocation, FacebookFriend, FacebookPage, FacebookStatus, FacebookPagesUsers

from socialscraper import twitter, facebook
from sqlalchemy.exc import IntegrityError

# ----------------------------------------------------- #
#                        Twitter                        #
# ----------------------------------------------------- #
twitter_scraper = twitter.TwitterScraper()
twitter_username = os.getenv("TWITTER_USERNAME")
twitter_password = os.getenv('TWITTER_PASSWORD')
twitter_scraper.add_user(username=twitter_username,password=twitter_password)

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

facebook_scraper = facebook.FacebookScraper()
facebook_username = os.getenv("FACEBOOK_USERNAME")
facebook_password = os.getenv("FACEBOOK_PASSWORD")
facebook_scraper.add_user(email=facebook_username, password=facebook_password)
facebook_scraper.login()

@celery.task(name='scrape.facebook.fan')
def scrape_fan(username):
    uid = facebook_scraper.get_graph_id(username)
    celery.send_task('scrape.facebook.fan.about', args=[username,uid], queue='celery')
    celery.send_task('scrape.facebook.fan.likes', args=[username,uid], queue='celery')
    # celery.send_task('scrape.facebook.fan.timeline', args=[username], queue='celery')

@celery.task(name='scrape.facebook.fan.about')
def scrape_fan_about(username,uid):
    result = facebook_scraper.get_about(username, graph_id=uid)

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

    return True

import pdb

@celery.task(name='scrape.facebook.fan.likes')
def scrape_fan_likes(username,uid):
    for result in facebook_scraper.graph_search(username, "pages-liked", graph_id=uid):
        page = FacebookPage(
            page_id=result.page_id,
            username=result.username,
            url=result.url,
            name=result.name,
            users=[FacebookUser.query.get(uid)]
        )
        pdb.set_trace()
        db.session.merge(page)
        db.session.commit()
    return True

# @celery.task(name='scrape.facebook.fan.feed')
# @celery.task(name='scrape.facebook.fan.timeline')
# def scrape_fan_feed(username):
#     pass # TODO: need to implement generator in package side (Al)
