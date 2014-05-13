# -*- coding: utf-8 -*-

import sys, csv, os

# gevent monkey patch
if 'threading' in sys.modules: del sys.modules['threading']
import gevent.monkey; gevent.monkey.patch_thread()

import logging
logging.basicConfig(level=logging.INFO)

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Server, Shell
from flask.ext.migrate import Migrate, MigrateCommand
import flask.ext.migrate as flmigrate

import os, pprint, pdb

from app import app
from app import models
from app.models import db

from sqlalchemy.exc import IntegrityError

manager = Manager(app)
migrate = Migrate(app, db)

from app.models import FacebookUser, FacebookPage

# from app.models import TwitterUser, TwitterTweet
# from app.models import FacebookUser, FacebookFamily, FacebookLocation, FacebookFriend, FacebookPage, FacebookStatus, FacebookPagesUsers

# from app.handlers import socketio
# class GeventSocketIOServer(Server):
#     def handle(self, app, host, port, use_debugger, use_reloader,
#                threaded, processes, passthrough_errors):

#         socketio.run(app, host=host, port=port)
# manager.add_command("runserver", GeventSocketIOServer(host="0.0.0.0"))

def _make_context():
    return dict(app=app, db=db, models=models)

BANNER = "Run the following commands: \n" + \
         "from __future__ import division \n" + \
         "from sqlalchemy import and_, or_ \n" + \
         "import os, pickle, json, requests \n" + \
         "from socialscraper.facebook import FacebookScraper \n" + \
         "from socialscraper.twitter import TwitterScraper \n" + \
         "from app.models import * \n" + \
         "from app.tasks import scrape \n\n" + \
         "scrape.get_about() \n" + \
         "scrape.get_likes() \n\n" + \
         "scrape.get_about.delay() \n" + \
         "scrape.get_likes.delay() \n\n" + \
         "process_list = (scrape.get_usernames.s(get='empty') | scrape.dmap.s(scrape.get_about.s())) \n" + \
         "res = process_list() \n\n" + \
         "# reuse logged in facebook_scraper pickle \n" + \
         "facebook_scraper = pickle.load(open( 'facebook_scraper.pickle', 'rb' )) \n\n" + \
         "facebook_scraper = FacebookScraper(scraper_type='nograph') \n" + \
         "facebook_scraper.add_user(email=os.getenv('FACEBOOK_EMAIL'), password=os.getenv('FACEBOOK_PASSWORD'), id=os.getenv('FACEBOOK_USERID'), username=os.getenv('FACEBOOK_USERNAME')) \n" + \
         "facebook_scraper.pick_random_user() \n" + \
         "facebook_scraper.login() \n" + \
         "facebook_scraper.init_api() \n" + \
         "pickle.dump(facebook_scraper, open('facebook_scraper.pickle', 'wb')) \n\n" + \
         "scrape.get_about.delay() \n" + \
         "scrape.get_likes.delay() \n" + \
         "process_list = (scrape.get_usernames.s(get='empty') | scrape.dmap.s(scrape.get_about.s())) \n" + \
         "process_list = (scrape.get_usernames.s(get='nonempty_and_nolikes') | scrape.dmap.s(scrape.get_likes.s())) \n" + \
         "len(map(lambda user: user.username, FacebookUser.query.filter(FacebookUser.pages != None))) \n" + \
         "len(map(lambda page: page.username, FacebookPage.query.all())) \n" + \
         "res = process_list() \n\n" + \
         "from app.tasks import datacomplete \n" + \
         "datacomplete.find_fb_place_addrs() \n"

manager.add_command("runserver", Server(host="0.0.0.0"))
manager.add_command('db', MigrateCommand)
manager.add_command("shell", Shell(make_context=_make_context, banner=BANNER))

@manager.command
def facebook(scrape_type, graph_name):
    from socialscraper.facebook import FacebookScraper
    pp = pprint.PrettyPrinter(indent=4)
    facebook_scraper = FacebookScraper()
    # facebook_scraper.add_user(email=os.getenv("FACEBOOK_EMAIL"), password=os.getenv("FACEBOOK_PASSWORD"))
    # facebook_scraper.login()

    def pages_liked(username):
        print "pages liked."
        #for item in facebook_scraper.graph_search(username, "pages-liked"):
        #    print item
        for item in facebook_scraper.get_pages_liked_by(username):
            print item

    def likers(pagename):
        for item in facebook_scraper.graph_search(pagename, "likers"):
            print item

    def about(username):
        stuff = facebook_scraper.get_about(username)
        pp.pprint(stuff)

    def timeline(username):
        from socialscraper.facebook import timeline
        timeline.search(facebook_scraper.browser, facebook_scraper.cur_user, username)

    if scrape_type == "about":
        about(graph_name)
    elif scrape_type == "pages":
        pages_liked(graph_name)
    elif scrape_type == "likers":
        likers(graph_name)
    elif scrape_type == "timeline":
        timeline(graph_name)

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

@manager.command
def parse_schneider():
    from socialscraper.facebook.public import parse_url
    with open('schneider.txt', 'rb') as f:
        for line in f:
            url,name = eval(line)
            username = parse_url(url)
            string = u'("%s", "%s", "%s")\n' % (url,name,username)
            print string
            with open('schneider2.txt', 'a') as f2:
                f2.write(string.encode('utf-8'))

@manager.command
def parse_schneider2():
    from socialscraper.facebook import FacebookScraper
    from socialscraper.base import ScrapingError
    from app.models import db, FacebookUser
    facebook_scraper = FacebookScraper()
    facebook_scraper.init_api()

    with open('schneider2.txt', 'rb') as f:
        counter = 0
        for line in f:
            # if counter > 100: break
            url, name, username = eval(line)
            try:
                result = facebook_scraper.get_about(username)
                profile = result[0]
                user = FacebookUser(uid=profile.get('id'), username=profile.get('username'), name=profile.get('name'), sex=profile.get('gender'))
                print counter, user.uid, user.username, user.name, user.sex
                db.session.merge(user)
                db.session.commit()
            except ScrapingError as e:
                print "error: ", e
                continue
            counter = counter + 1

@manager.command
def schneider():
    from socialscraper.facebook import FacebookScraper
    pp = pprint.PrettyPrinter(indent=4)
    facebook_scraper = FacebookScraper()
    facebook_scraper.add_user(email=os.getenv("FACEBOOK_EMAIL"), password=os.getenv("FACEBOOK_PASSWORD"))
    facebook_scraper.login()
    for info in FacebookUser.query.filter(FacebookUser.pages.any(username='schneiderforcongress')):
        print info.username, info.uid
        result = facebook_scraper.get_about(info.username, graph_id=info.uid)
        user = FacebookUser(
            uid=result.uid, 
            username=result.username, 
            email=result.email, 
            birthday=result.birthday, 
            sex=result.sex, 
            college=result.college, 
            employer=result.employer,
            highschool=result.highschool,
            currentcity=result.currentcity,
            hometown=result.hometown
        )
        db.session.merge(user)
        db.session.commit()

@manager.command
def something():
    from socialscraper import facebook
    serialized_browser = open( "browser.pickle", "rb" ).read()
    serialized_api = open( "api.pickle", "rb" ).read()
    facebook_scraper = facebook.FacebookScraper(pickled_session=serialized_browser, pickled_api=serialized_api, scraper_type="nograph")
    facebook_scraper.add_user(email=os.getenv("FACEBOOK_USERNAME"), password=os.getenv("FACEBOOK_PASSWORD"))
    facebook_scraper.pick_random_user()

from subprocess import call, check_output

@manager.command
def drop_table(tablename):
    call(["psql", "-d", "alpaca_api_development", "-c", "DROP TABLE %s CASCADE" % tablename])

@manager.command
def restore_table(tablename, filename):
    call(["pg_restore", "-d", "alpaca_api_development", "--table", tablename, filename])

@manager.command
def clear_rabbit():
    call(["rabbitmqctl", "stop_app"])
    call(["rabbitmqctl", "reset"])
    call(["rabbitmqctl", "start_app"])

if __name__ == "__main__":
    manager.run()