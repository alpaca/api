# -*- coding: utf-8 -*-

import sys

# gevent monkey patch
if 'threading' in sys.modules: del sys.modules['threading']
import gevent.monkey; gevent.monkey.patch_thread()

from .. import app as flask_app # app var conflicts with celery, needs absolute import from future?
from .. import environment
from .. import settings
from celery import Celery

def make_celery(flask_app):

	"""

	While you can use Celery without any reconfiguration with Flask, 
	it becomes a bit nicer by subclassing tasks and adding support 
	for Flask's application contexts and hooking it up with the 
	Flask configuration.

	- http://flask.pocoo.org/docs/patterns/celery/

	"""

	celery = Celery()
	celery.config_from_object(settings.config)

	TaskBase = celery.Task
	class ContextTask(TaskBase):
	    abstract = True
	    def __call__(self, *args, **kwargs):
	        with flask_app.app_context():
	            return TaskBase.__call__(self, *args, **kwargs)
	celery.Task = ContextTask

	return celery

celery = make_celery(flask_app)

__all__ = ['scrape']

# import the tasks you need
# from app.tasks import *