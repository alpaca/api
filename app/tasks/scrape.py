# -*- coding: utf-8 -*-
import requests, os
from app.tasks import celery
from app.models import db

from app.models.tweet import Tweet
from app.models.twitter_user import TwitterUser

from socialscraper import twitter
from sqlalchemy.exc import IntegrityError

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