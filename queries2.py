import csv
from app.models import *
from app.models import db
from sqlalchemy import or_, and_
from datetime import datetime
from dateutil import parser

def age(mina=0, maxa=2000, unknown=False):
    if unknown: filtr = FacebookUser.birthday == None
    else:
        tNow = datetime.now()
        filtr = FacebookUser.birthday.between(
                datetime(year=tNow.year-maxa, month=1, day=1), 
                datetime(year=tNow.year-mina,month=1, day=1)
            )
    
    return filtr

def sex(sex=None, unknown=False):
    if unknown: filtr = FacebookUser.sex == None
    elif sex=='m': filtr = or_(FacebookUser.sex=="male", FacebookUser.sex=="Male")      
    elif sex=='f': filtr = or_(FacebookUser.sex=="female", FacebookUser.sex=="Female")
    elif sex=='o': 
        filtr = and_(
            FacebookUser.sex!="male", 
            FacebookUser.sex!="Male", 
            FacebookUser.sex!="female", 
            FacebookUser.sex!="Female"
        )
    else: filtr = FacebookUser.sex == sex

    return filtr

def city(city, unknown=False):
    filtr = or_(
        FacebookUser.currentcity.ilike("%%%s%%" % city),
        FacebookUser.hometown.ilike("%%%s%%" % city),
    )

    return filtr

def zipcode(zipcode, unknown=False):
    filtr = FacebookUser.locations.any(zipcode=zipcode)

    return filtr


def likes(unknown=False):
    if unknown: filtr = FacebookUser.pages == None
    else: filtr = FacebookUser.pages != None

    return filtr

###################################################################

# Examples

# Example 1
print "Querying people of age 20 to 30"
query = FacebookUser.query.filter(
            age(mina=20, maxa=30)
        )
print map(lambda user: (user.username, user.birthday), query.all())
print "\n"

# Example 2
print "Querying people of age 20 to 30 who are male"
query = FacebookUser.query.filter(
    and_(
        age(mina=20, maxa=30),
        sex(sex='m')
    )
)
print map(lambda user: (user.username, user.birthday, user.sex), query.all())
print "\n"

# Example 3
print "Querying people of age 20 to 30 who are male and from evanston"
query = FacebookUser.query.filter(
    and_(
        age(mina=20, maxa=30),
        sex(sex='m'),
        city('evanston')
    )
)
print map(lambda user: (user.username, user.birthday, user.sex, user.currentcity, user.hometown), query.all())
print "\n"

