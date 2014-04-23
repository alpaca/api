# -*- coding: utf-8 -*-

import sys, csv, os

# gevent monkey patch
if 'threading' in sys.modules: del sys.modules['threading']
import gevent.monkey; gevent.monkey.patch_thread()

import logging
logging.basicConfig(level=logging.INFO)

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand
import flask.ext.migrate as flmigrate

import os, pprint

from app import app
from app.models import db
from app.tasks import celery
from app.controllers import api


from sqlalchemy.exc import IntegrityError

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
    elif scrape_type == "pages":
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

@manager.command
def import_csv(path,pkey_colname):
    csvname = path.split('/')[-1]

    def _make_header_arr(raw_header,data_row):
        fields = []
        for h_col,d_col in zip(raw_header,data_row):
            is_pkey = True if (pkey_colname in h_col) else False
            if is_pkey:
                print "Found pkey: %s" % h_col
            py_type = 'str'
            # try:
            #     float(d_col)
            #     py_type = 'float'
            # except ValueError:
            #     pass

            fields.append({
                "name" : h_col,
                "py_type" : py_type,
                "db_type" :  "String",#"Float" if (py_type == float) else "String", || Just String for now
                "primary_key" : is_pkey
                })
        return fields

    from app.models.contributor import generate_contrib_model
    with open(path, 'rbU') as csvfile:
        csvreader = csv.reader(csvfile)
        for idx,row in enumerate(csvreader):
            if idx == 0:
                raw_header = row
            elif idx == 1: # header row
                header = _make_header_arr(raw_header,row)
                Contributor = generate_contrib_model(header)

                # trololol
                flmigrate.migrate()
                flmigrate.upgrade()

                print "Generated Contributor Model: %s" % str(Contributor)
            if idx != 0:
                contrib = Contributor(csvname)
                for kv in zip(header,row):
                    setattr(contrib,kv[0]['name'],eval("%s(\"%s\")" % (kv[0]['py_type'], kv[1])))
                db.session.add(contrib)
                try:
                    db.session.commit()
                except IntegrityError:
                    print "Warning: DB Integrity Error"
                    db.session.rollback()
    return

if __name__ == "__main__":
    manager.run()