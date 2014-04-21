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

# each scrape_feed creates its own scraper, is it possible
# to pass around a scraper for all tasks and use the same 
# scraper simultaneosly? this will be necessary for fb.
# we want one authenticated scraper (requests session)
# passed around. we can also perhaps possibly clone the
# cookies of a session and modify scraper to prevent login
# if creeated with cookies ?
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

@celery.task(name='scrape.facebook.fan')
def scrape_fan(username):
    scraper = twitter.FacebookScraper()
    self.scraper.add_user(email=os.getenv("FACEBOOK_USERNAME"), password=os.getenv("FACEBOOK_PASSWORD"))
    self.scraper.login()
    subtasks = []



@celery.task(name='scrape.facebook.')
