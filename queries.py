import csv
from app.models import *
from sqlalchemy import or_, and_
from datetime import datetime
from dateutil import parser

def birthday(age = [0, 10000], unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """

    if unknown:
        query = FacebookUser.query.filter_by(birthday=None)
    else:
        min_age = age[0]
        max_age = age[1]
        tNow = datetime.now()
        query = FacebookUser.query.filter(
            FacebookUser.birthday.between(
                datetime(year=tNow.year-max_age, month=1, day=1), 
                datetime(year=tNow.year-min_age,month=1, day=1)
            )
        )
    
    return query.all()

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

    return query.all()

def currentcity(cityList=[], unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """
    if unknown:
        query = FacebookUser.query.filter_by(currentcity=None)
    else:
        cityString = ""
        for city in cityList:
            cityString = cityString + "OR currentcity Like '%"+city+"%'"
        cityString= cityString[2:]
        query = FacebookUser.query.from_statement("Select * from facebook_users where " + cityString)

    return query.all()


def hometown(city=[], unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """

    if unknown:
        query = FacebookUser.query.filter_by(hometown=None)
    else:
        cityString = ""
        for city in cityList:
            cityString = cityString + "OR hometown Like '%"+city+"%'"
        cityString= cityString[2:]
        query = FacebookUser.query.from_statement("Select * from facebook_users where " + cityString)

    return query.all()


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

    return query.all()

def collegeGradYear(years = [1000, 3000], unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """
    minYear = years[0]
    maxYear = years[1]
    if unknown:
        query = FacebookUser.query.filter_by(college=None)
    else:
        gradString = ""
        for year in range(minYear,maxYear):
            gradString = gradString + "OR college Like '%"+str(year)+"%'"
        gradString= gradString[2:]
        query = FacebookUser.query.from_statement("Select * from facebook_users where " + gradString)

    return query.all()


def highSchoolGradYear(years = [1000, 3000], unknown=None):
    """
    Queries the database for people who are between a certain age range

    Ignores all people who don't have a birth year set because their birth year is set to 2014 and the query will only query up to january 1st on the current year

    """
    minYear = years[0]
    maxYear = years[1]
    if unknown:
        query = FacebookUser.query.filter_by(highschool=None)
    else:
        gradString = ""
        for year in range(minYear,maxYear):
            gradString = gradString + "OR highschool Like '%"+str(year)+"%'"
        gradString= gradString[2:]
        query = FacebookUser.query.from_statement("Select * from facebook_users where " + gradString)

    return query.all()

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

    return query.all()

def employerInList(employerList=[], unknown=None):
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

    return query.all()

def andQuery(query1, query2):
    final = []
    for q in query1:
        if q in query2:
            final = final + [q]
    return final

def orQuery(query1, query2):
    final = query2
    for q in query1:
        if q not in query2:
            final = final + [q]
    return final





# def buildTree(depth = 0, funcArray = [], query=[], printString = ""):
#     line = ("--"*depth) + "Size: " + str(len(query))
#     print line 
#     f.write(line + "\n")
#     if depth < len(funcArray) and (depth == 0 or len(query) > 0):
#         for x in funcArray[depth][2]:
#             line =  ("--"*depth) + funcArray[depth][1] + " = " + str(x)
#             print line
#             f.write(line+"\n")
#             if depth ==0:
#                 buildTree(depth +1, funcArray, funcArray[depth][0](x))
#             else:
#                 buildTree(depth +1, funcArray, andQuery(query, funcArray[depth][0](x)))
        
def buildTree(depth = 0, funcArray = [], query=[], printString = ""):
    line = printString + " : " + str(len(query))
    print line 
    f.write(line + "\n")
    if depth < len(funcArray) and (depth == 0 or len(query) > 0):
        for x in funcArray[depth][2]:
            if depth ==0:
                buildTree(depth +1, funcArray, funcArray[depth][0](x), printString+str(x[0]))
            else:
                buildTree(depth +1, funcArray, andQuery(query, funcArray[depth][0](x)), printString+", " + str(x[0]))
        


def permutations(istr, cstr, used_indices):
    if len(used_indices) == len(istr): return [cstr]
    result = []
    for idx, char in enumerate(istr):
        if idx not in used_indices:
            result.extend(permutations(istr, cstr + [char], used_indices | {idx}))
    return result

def fixQuote(x):
    if x == "'":
        return "\'"
    else:
        return x


employArray= []

with open('Employment.csv', 'rb') as c:
    creader = csv.reader(c, delimiter=',')
    firstLine = True
    for row in creader:
        if firstLine:
            firstLine = False
        else:    
            for i in range(1,len(row)):
                if row[i] != '':
                    line = filter(lambda x: x != "'", row[i])
                    if i>=len(employArray):
                        employArray.append([line])
                    else:
                        employArray[i].append(line)

funArray = [[employerInList, "Employer" , employArray], [birthday, "Age", [[15,24], [25,34], [35,44], [45, 54], [55, 64], [65, 200]]] , [sex, "Sex", ["m", "f", "o"]], [currentcity, "Current Location", [["Illinois"], ["New York"], ["California"]]]]
perm = permutations([0, 1, 2, 3] , [], set())
f = open("result.txt", 'w')
for p in perm:
    buildTree(funcArray=map(lambda x: funArray[x], p))