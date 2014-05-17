import csv
from app.models import *
from app.models import db
from sqlalchemy import or_, and_
from datetime import datetime
from dateutil import parser

def birthday(age = [0, 10000], unknown=False):
    if unknown: filtr = FacebookUser.birthday == None
    else:
        min_age = age[0]
        max_age = age[1]
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

def likes(unknown=False):
    if unknown: filtr = FacebookUser.pages == None
    else: filtr = FacebookUser.pages != None

    return filtr

def city(city, unknown=False):
    """
    FacebookUser.query.filter_by(username='joel.abraham.948').first().locations

    FacebookUser.query.filter(FacebookUser.locations != None).all()
    FacebookUser.query.filter(FacebookUser.locations.any(zipcode=60093)).all()
    """
    
    filtr = or_(
        FacebookUser.currentcity.ilike("%%%s%%" % city),
        FacebookUser.hometown.ilike("%%%s%%" % city),
    )

    return filtr

def zipcode(zipcode, unknown=False):
    filtr = FacebookUser.locations.any(zipcode=60093)

    return filtr

query = FacebookUser.query.filter(
    or_(
        birthday(age=(20,30)),
        sex(sex='m')
    )
)

print query.all()