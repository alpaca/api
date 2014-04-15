# -*- coding: utf-8 -*-

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