# -*- coding: utf-8 -*-
import requests, os
from app.tasks import celery
from app.models import db

from app.models.tweet import Tweet
from app.models.twitter_user import TwitterUser

from socialscraper import twitter
from sqlalchemy.exc import IntegrityError

# ----------------------------------------------------- #
#                        Twitter                        #
# ----------------------------------------------------- #

@celery.task(name='scrape.twitter.followers')
def scrape_followers(username):
    scraper = twitter.TwitterScraper()
    scraper.add_user(username=os.getenv("TWITTER_USERNAME"),password=os.getenv('TWITTER_PASSWORD'))
    subtasks = []
    for follower in scraper.get_followers('aljohri'):
        #print follower.screen_name
        sig = celery.send_task('scrape.twitter.feed', args=[follower.screen_name], queue='celery')
        subtasks.append(sig)

        follower_obj = TwitterUser(user_id=follower.id,screen_name=follower.username)
        db.session.add(follower_obj)
        try:
            db.session.commit()
        except IntegrityError:
            print "Warning: Integrity Error."
            db.session.rollback()

    return True

# perhaps rename to scrape_follower (singular) ?
# perhaps rename scrape.twitter.XXXXX (data, information)
# something generic that can be used as the same interface between
# fb and twitter
# the fb, scrape_fan task should probably run subtasks:
#   scrape_fan_about, scrape_fan_likes, scrape_fan_feed
# just some ideas
@celery.task(name='scrape.twitter.feed')
def scrape_feed(username):
    scraper = twitter.TwitterScraper()
    tweets = scraper.get_feed_by_screen_name(username)
    # write to DB

    for tweet in tweets:
        tweet_obj = Tweet(id=tweet.id,
                          timestamp=tweet.timestamp,
                          screen_name=username,
                          content=tweet.content)
        db.session.add(tweet_obj)
        try:
            db.session.commit()
        except IntegrityError:
            print "Warning: Integrity Error."
            db.session.rollback()
    return True

# ------------------------------------------------------ #
#                        Facebook                        #
# ------------------------------------------------------ #

# I had previously commented that we may attempt to pass around
# the scraper to prevent incessant logins.

# We *might* want to come up with better solution than passing 
# around scraper, though. The scraper can only be pickled and isn't
# json serializable.

# Although we will probably use the outward method "scrape.facebook.fan"
# for services, we may want a different scraper service to handle
# scraping the about section vs. scraping the likes.

# In addition, the timeline scraper is written in a way that it can be done
# asynchronously using a cursor of datetime epoch.

# Logging into Facebook on each request is not an acceptable solution, but
# pickling in the short term might be okay. I'd prefer not to as it 
# severely limits our cross-langauge compatibility.
# Personally it also seems like a code smell. The pickled objects are
# significantly larger in size. Its like a ginormous blog of binary shit.

# The ideal solution is to somehow maintain a single login for each instance
# of the service and then have the tasks use that single instance.

# To accomplish this, we can instantiate both a facebook and twitter scraper
# in the __init__ of the tasks module. Then:
# from app.tasks import celery, facebook_scraper, twitter_scraper

# It seems like the requests Session object is threadsafe as long as we're
# not running any mutators.
# http://stackoverflow.com/questions/18188044/is-the-session-object-from-pythons-requests-library-thread-safe

@celery.task(name='scrape.facebook.fan')
def scrape_fan(username):
    scraper = twitter.FacebookScraper()
    self.scraper.add_user(email=os.getenv("FACEBOOK_USERNAME"), password=os.getenv("FACEBOOK_PASSWORD"))
    self.scraper.login()
    subtasks = []
    # sig1 = celery.send_task('scrape.facebook.fan.about', args=[follower.screen_name], queue='celery')
    # sig2 = celery.send_task('scrape.facebook.fan.likes', args=[follower.screen_name], queue='celery')
    # subtasks.append(sig1)
    # subtasks.append(sig2)

@celery.task(name='scrape.facebook.fan.about')
def scrape_fan_about(scraper, username):
    return scraper.get_about(username)

@celery.task(name='scrape.facebook.fan.likes')
def scrape_fan_likes(scraper, username):
    for fan in scraper.graph_search(username, "pages-liked"):
        print fan # commit to db
    return True

@celery.task(name='scrape.facebook.fan.feed')
@celery.task(name='scrape.facebook.fan.timeline')
def scrape_fan_feed(scraper, username):
    pass # TODO: need to implement generator in package side (Al)
