# -*- coding: utf-8 -*-

import sys

# gevent monkey patch
if 'threading' in sys.modules: del sys.modules['threading']
import gevent.monkey; gevent.monkey.patch_thread()

import logging
logging.basicConfig(level=logging.INFO)

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand

import os, pprint

from app import app
from app.models import db
from app.tasks import celery
from app.controllers import api


manager = Manager(app)
migrate = Migrate(app, db)

# from app.handlers import socketio
# class GeventSocketIOServer(Server):
#     def handle(self, app, host, port, use_debugger, use_reloader,
#                threaded, processes, passthrough_errors):

#         socketio.run(app, host=host, port=port)
# manager.add_command("runserver", GeventSocketIOServer(host="0.0.0.0"))

manager.add_command("runserver", Server(host="0.0.0.0"))
manager.add_command('db', MigrateCommand)

test_fb_users = [
    ('Al Johri', 'al.johri'),
    ('Moritz Gellner', 'moritz.gellner'), # fb works
    ('Michael Marasco', 'michaelamarasco'), 
    ('Todd Warren', 'todd.warren.seattle'),
    ('Rich Gordon', 'richgor'),
    ('Chris Riesbeck', 'chris.riesbeck'),
    ('Steve Olechowski', 'steve.olechowski'), # fb works, twitter works
    ('Megan Everett', 'megan.everett'),
    ('Mitra Veeramasuneni', 'vlmitra'), # fb works, twitter works
    ('Ryan Mcafee', 'mcafeeryan'),
    ('Ben Rafshoon', 'benrafshoon') # fb works, twitter works
]

# python manage.py resolve "Steve Olechowski" --city="Chicago" --state="IL"
# python manage.py resolve "Mitra Veeramasuneni"
# python manage.py resolve "Ben Rafshoon"
# python manage.py resolve "Rich Gordon" --city="Evanston" --state="IL"
# python manage.py resolve "Daniel Thirman" --city="Wilmette" --state="IL"
# python manage.py resolve "Moritz Gellner"

# python manage.py facebook vlmitra
# python manage.py facebook benrafshoon
# python manage.py facebook richgor
# python manage.py facebook dthirman
# python manage.py facebook moritz.gellner

# python manage.py facebook michaelamarasco
# python manage.py facebook todd.warren.seattle

# python manage.py twitter steveobd
# python manage.py twitter vlmitra
# python manage.py twitter captainshoon
# python manage.py twitter richgor

@manager.command
def facebook(scrape_type, username):
    from socialscraper.facebook import FacebookScraper
    pp = pprint.PrettyPrinter(indent=4)
    facebook_scraper = FacebookScraper()
    facebook_scraper.add_user(email=os.getenv("FACEBOOK_EMAIL"), password=os.getenv("FACEBOOK_PASSWORD"))
    facebook_scraper.login()

    def pages_liked(username):
        for item in facebook_scraper.graph_search(username, "pages-liked"):
            print item

    def about(username):
        stuff = facebook_scraper.get_about(username)
        pp.pprint(stuff)

    def timeline(username):
        from socialscraper.facebook import timeline
        timeline.search(facebook_scraper.browser, facebook_scraper.cur_user, username)

    if scrape_type == "about":
        about(username)
    elif scrape_type == "fans":
        pages_liked(username)
    elif scrape_type == "timeline":
        timeline(username)

@manager.command
def twitter(username):
    from socialscraper.twitter import TwitterScraper
    twitter_scraper = TwitterScraper()

    tweets = twitter_scraper.get_feed_by_screen_name(username)
    for tweet in tweets:
        print tweet

@manager.command 
def resolve(name, city=None, state=None):
    from identityresolver.social import SocialProfileResolver, ResolvedPerson
    resolver = SocialProfileResolver()
    
    def resolve(name):
        for person in resolver.resolve([ResolvedPerson(0,full_name=name,city=city,state=state)]):
            print person
            print "\n==========\n"
            return person

    resolved = resolve(name)

if __name__ == "__main__":
    manager.run()