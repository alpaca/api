# -*- coding: utf-8 -*-
import requests, os
from app.tasks import celery

from socialscraper import twitter

@celery.task(name='addition')
def addition(x, y):
	return x + y

@celery.task(name='scrape.twitter.followers')
def scrape_followers(username):
	scraper = twitter.TwitterScraper()
	scraper.add_user_info(os.getenv("TWITTER_USERNAME"),os.getenv('TWITTER_PASSWORD'))
	followers = []
	for follower in scraper.get_followers('aljohri'):
		# do something
		followers.append(follower)
	return str(followers)


@celery.task(name='scrape')
def urlopen(url):
    print('Opening: {0}'.format(url))
    try:
        resp = requests.get(url)
    except Exception as exc:
        print('Exception for {0}: {1!r}'.format(url, exc))
        return url, '', 0
    print('Done with: {0}'.format(url))
    return url, resp.text, 1