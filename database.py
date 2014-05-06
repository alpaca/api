import re
from app.models import FacebookUser
from app.models import db
import requests
# from sqlalchemy.exc import IntegrityError
from sqlalchemy import exc
import json
regex1 = re.compile("^https:\/\/www.facebook.com\/([^?\n]+)(?:\?ref.*)?$")
regex2 = re.compile("https:\/\/www.facebook.com\/profile.php\?id=(.*)\&ref")


def get_id(graph_name):
    "Get the graph ID given a name."""
    get_response = lambda : requests.get('https://graph.facebook.com/' + graph_name)
    response = get_response()
    counter = 0
    while response.status_code == 400 and counter < 3:
        response = get_response()
        counter += 1
    id = json.loads(response.text).get('id', None)
    return int(id) if id else None

def parse_url(url):
    regex_result1 = regex1.findall(url)
    if regex_result1:
        username = regex_result1[0]
        if username == None: raise ValueError("No username was parsed %s" % url)
        if 'pages/' in username:
            uid = username.split('/')[-1]
            username = uid
        else:
            uid = get_id(username)
            if uid == None: raise ValueError("No userid was parsed %s" % username)
    else: # old style user that doesn't have username, only uid
        regex_result2 = regex2.findall(url)
        if not regex_result2: raise ValueError("URL not parseable %s" % url)
        uid = regex_result2[0]
        username = regex_result2[0]
        if uid == None: raise ValueError("No userid was parsed for username %s and url %s" % username, url)

    return username, int(uid)
badNames =[]


with open("badNames.txt", "r") as f:

    count = 0
    for line in f:
        url,name = eval(line)
        count = count + 1
        try:
            username,uid = parse_url(url)
            print count
            z = FacebookUser(username=username,uid=uid, name=name)
            db.session.add(z)
        except ValueError:
            stri = "(\"%s\", \"%s\")\n"  % (url, name)

            with open("badNames2.txt", "a") as f2:
                f2.write(stri.encode('utf8', 'ignore'))            

            badNames.append(stri)
            continue

        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            print "asdfsadfasdfasdfafsd"
            db.session.rollback()
            continue


    

