import csv
from app.models import *
from sqlalchemy import or_, and_
from datetime import datetime
from dateutil import parser

def birthday(age = [0, 10000], unknown=None):
    if unknown:
        filtr = FacebookUser.birthday == None
    else:
        min_age = age[0]
        max_age = age[1]
        tNow = datetime.now()
        filtr = FacebookUser.birthday.between(
                datetime(year=tNow.year-max_age, month=1, day=1), 
                datetime(year=tNow.year-min_age,month=1, day=1)
            )
    
    return filtr

def sex(sex=None, unknown=None):
    if unknown:
        filtr = FacebookUser.sex == None
    elif sex=='m':
        filtr = or_(FacebookUser.sex=="male", FacebookUser.sex=="Male")      
    elif sex=='f':
        filtr = or_(FacebookUser.sex=="female", FacebookUser.sex=="Female")
    elif sex=='o':
        filtr = and_(FacebookUser.sex!="male", FacebookUser.sex!="Male", FacebookUser.sex!="female", FacebookUser.sex!="Female")
    else:
        filtr = FacebookUser.sex == sex

    return filtr

query = FacebookUser.query.filter(
    or_(
        birthday(age=(20,30)),
        sex(sex='m')
    )
)

print query.all()