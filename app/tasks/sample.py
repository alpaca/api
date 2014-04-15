# -*- coding: utf-8 -*-
import requests
from app.tasks import celery

@celery.task(name='addition')
def addition(x, y):
	return x + y

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