import csv
from app.models import *
from app.models import db
from sqlalchemy import or_, and_
from datetime import datetime
from dateutil import parser

def age(min_age=None, max_age=None, unknown=False):
    if unknown: filtr = FacebookUser.birthday == None
    else:
        tNow = datetime.now()
        filtr = FacebookUser.birthday.between(
                datetime(year=tNow.year-max_age, month=1, day=1), 
                datetime(year=tNow.year-min_age,month=1, day=1)
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
    filtr = FacebookUser.locations.any(zipcode=60093)

    return filtr


def likes(unknown=False):
    if unknown: filtr = FacebookUser.pages == None
    else: filtr = FacebookUser.pages != None

    return filtr


query = FacebookUser.query.filter(
    or_(
        birthday(age=(20,30)),
        sex(sex='m')
    )
)

print query.all()