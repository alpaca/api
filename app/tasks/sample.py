# -*- coding: utf-8 -*-
import requests, os
from app.tasks import celery

from socialscraper import twitter

from celery import chord, group, chain, signature

@celery.task(name='scrape.twitter.followers')
def scrape_followers(username):
	scraper = twitter.TwitterScraper()
	scraper.add_user_info(os.getenv("TWITTER_USERNAME"),os.getenv('TWITTER_PASSWORD'))
	followers = []
	subtasks = []
	for follower in scraper.get_followers('aljohri'):
		#print follower.screen_name
		sig = celery.send_task('scrape.twitter.feed', args=[follower.screen_name], queue='celery')
		subtasks.append(sig)
		followers.append(follower)

	return str(followers)

@celery.task(name='scrape.twitter.feed')
def scrape_feed(username):
	scraper = twitter.TwitterScraper()
	tweets = scraper.get_feed_by_screen_name(username)
	return str(tweets)