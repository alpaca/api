# -*- coding: utf-8 -*-

import sys

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

from celery.signals import task_postrun
from app.models import db

@task_postrun.connect
def close_session(*args, **kwargs):
	# http://stackoverflow.com/questions/12044776/how-to-use-flask-sqlalchemy-in-a-celery-task
    # Flask SQLAlchemy will automatically create new sessions for you from 
    # a scoped session factory, given that we are maintaining the same app
    # context, this ensures tasks have a fresh session (e.g. session errors 
    # won't propagate across tasks)
    db.session.remove()

__all__ = ['scrape']

from . import *