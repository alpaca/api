# -*- coding: utf-8 -*-

import os

from . import app
from .tasks import celery
from flask import render_template, request, redirect

@app.route('/')
def root():
	return "Hello Alpaca"

@app.route('/sample')
def sample():
	thing = celery.send_task("addition", args=[1,2], queue="celery")
	print thing
	return str(thing.get())


@app.route('/scrape')
def scrape():
	for page in range(100):
		thing = celery.send_task("scrape", args=['http://stackoverflow.com/questions?page=' + str(page)], queue="celery")
		print thing
	return "started 100 tasks"

@app.route('/scrape/twitter/followers')
def scrape_twitter_followers():
	thing1 = celery.send_task("scrape.twitter.followers", args=['aljohri'], queue="celery")
	print thing1
	# thing2 = celery.send_task("scrape.twitter.followers", args=['mogellner'], queue="celery")
	# thing3 = celery.send_task("scrape.twitter.followers", args=['cpottamus'], queue="celery")

	return "started three scrape tasks"