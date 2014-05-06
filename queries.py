from app.models import *
from sqlalchemy import or_, and_
from datetime import datetime
from dateutil import parser

def birthday(min_age=0, max_age=10000, unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """

    if unknown:
        query = FacebookUser.query.filter_by(birthday=None)
    else:
        tNow = datetime.now()
        query = FacebookUser.query.filter(
            FacebookUser.birthday.between(
                datetime(year=tNow.year-max_age, month=1, day=1), 
                datetime(year=tNow.year-min_age,month=1, day=1)
            )
        )
    
    return query

def sex(sex=None, unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """

    if unknown:
        query = FacebookUser.query.filter_by(sex=None)
    elif sex=='m':
        query = FacebookUser.query.filter(or_(FacebookUser.sex=="male", FacebookUser.sex=="Male"))        
    elif sex=='f':
        query = FacebookUser.query.filter(or_(FacebookUser.sex=="female", FacebookUser.sex=="Female"))
    elif sex=='o':
        query = FacebookUser.query.filter(and_(FacebookUser.sex!="male", FacebookUser.sex!="Male", FacebookUser.sex!="female", FacebookUser.sex!="Female"))
    else:
        query = FacebookUser.query.filter_by(sex=sex)

    return query

def currentcity(city=None, unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """

    if unknown:
        query = FacebookUser.query.filter_by(currentcity=None)
    else:
        query = FacebookUser.query.filter(or_(FacebookUser.currentcity==city))        

    return query

def hometown(city=None, unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """

    if unknown:
        query = FacebookUser.query.filter_by(hometown=None)
    else:
        query = FacebookUser.query.filter(or_(FacebookUser.hometown==city))        

    return query


def collegeInList(collegeList=[], unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """

    if unknown:
        query = FacebookUser.query.filter_by(college=None)
    else:
        collegeString = ""
        for college in collegeList:
            collegeString = collegeString + "OR college Like '%"+college+"%'"
        collegeString= collegeString[2:]
        query = FacebookUser.query.from_statement("Select * from facebook_users where " + collegeString)

    return query

def collegeGradYear(minYear = 1000, maxYear = 3000, unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """

    if unknown:
        query = FacebookUser.query.filter_by(college=None)
    else:
        gradString = ""
        for year in range(minYear,maxYear):
            gradString = gradString + "OR college Like '%"+str(year)+"%'"
        gradString= gradString[2:]
        query = FacebookUser.query.from_statement("Select * from facebook_users where " + gradString)

    return query


def highSchoolGradYear(minYear = 1000, maxYear = 3000, unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """

    if unknown:
        query = FacebookUser.query.filter_by(highschool=None)
    else:
        gradString = ""
        for year in range(minYear,maxYear):
            gradString = gradString + "OR highschool Like '%"+str(year)+"%'"
        gradString= gradString[2:]
        query = FacebookUser.query.from_statement("Select * from facebook_users where " + gradString)

    return query

def highSchoolInList(schoolList=[], unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """

    if unknown:
        query = FacebookUser.query.filter_by(highschool=None)
    else:
        schoolString = ""
        for school in schoolList:
            schoolString = schoolString + "OR highschool Like '%"+school+"%'"
        schoolString= schoolString[2:]
        query = FacebookUser.query.from_statement("Select * from facebook_users where " + schoolString)

    return query

def employerInList(schoolList=[], unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """

    if unknown:
        query = FacebookUser.query.filter_by(employer=None)
    else:
        employerString = ""
        for employer in employerList:
            employerString = employerString + "OR employer Like '%"+employer+"%'"
        employerString= employerString[2:]
        query = FacebookUser.query.from_statement("Select * from facebook_users where " + employerString)

    return query

print type(and_(highSchoolGradYear(1960, 1980), collegeInList(["Illinois"])))