# -*- coding: utf-8 -*-

import sys

# gevent monkey patch
if 'threading' in sys.modules: del sys.modules['threading']
import gevent.monkey; gevent.monkey.patch_thread()

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand

import os, pprint

from app import app
from app.models import db
from app.tasks import celery
from app.controllers import api
from app.handlers import socketio

manager = Manager(app)
migrate = Migrate(app, db)

class GeventSocketIOServer(Server):
    def handle(self, app, host, port, use_debugger, use_reloader,
               threaded, processes, passthrough_errors):

        socketio.run(app, host=host, port=port)

manager.add_command("runserver", GeventSocketIOServer(host="0.0.0.0"))
manager.add_command('db', MigrateCommand)

@manager.command 
def presentation(name):

    # https://www.facebook.com/michaelamarasco?fref=ts
    # https://www.facebook.com/todd.warren.seattle?fref=ts
    # https://www.facebook.com/richgor?fref=ts
    # https://www.facebook.com/chris.riesbeck?fref=ts
    # https://www.facebook.com/steve.olechowski
    # https://www.facebook.com/megan.everett
    # https://www.facebook.com/vlmitra?fref=ts
    # https://www.facebook.com/mcafeeryan?fref=ts
    # https://www.facebook.com/benrafshoon?fref=ts    
    from identityresolver.social import SocialProfileResolver, ResolvedPerson
    from socialscraper.facebook import FacebookScraper
    from socialscraper.twitter import TwitterScraper
    pp = pprint.PrettyPrinter(indent=4)

    resolver = SocialProfileResolver()
    facebook_scraper = FacebookScraper()
    facebook_scraper.add_user(email=os.getenv("FACEBOOK_EMAIL"), password=os.getenv("FACEBOOK_PASSWORD"))
    facebook_scraper.login()
    twitter_scraper = TwitterScraper()
    
    def pages_liked(username):
        for item in facebook_scraper.graph_search(username, "pages-liked"):
            print item

    def about(username):
        stuff = facebook_scraper.get_about(username)
        pp.pprint(stuff)

    def timeline(username):
        from socialscraper.facebook import timeline
        timeline.search(facebook_scraper.browser, facebook_scraper.cur_user, username)

    def resolve(name):
        for person in resolver.resolve([ResolvedPerson(0,full_name=name)]):
            print person
            print "\n==========\n"
            return person

    resolved = resolve(name)
    pages_liked(resolved.facebook_username)
    print "\n==========\n"
    about(resolved.facebook_username)
    print "\n==========\n"
    timeline(resolved.facebook_username)
    print "\n==========\n"
    twitter_scraper.get_feed_by_screen_name(resolved.twitter_username)

if __name__ == "__main__":
    manager.run()