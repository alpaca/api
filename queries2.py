import csv
from app.models import *
from app.models import db
from sqlalchemy import or_, and_
from datetime import datetime
from dateutil import parser

######################################################
# Dynamic Queries
######################################################

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

def currentcity(city=None, unknown=False):
    if unknown: 
        filtr = FacebookUser.currentcity == None
    else:
        filtr = FacebookUser.currentcity.ilike("%%%s%%" % city)
    return filtr

def currentCityInList(cityList=[], unknown=False):
    if unknown: filtr = currentcity(unknown=True)
    elif len(cityList) <1: filtr=None
    elif type(cityList[0]) == int:
        or_list = [zipcode(x, "currentcity") for x in cityList]
        filtr = or_(*or_list)
    else:
        or_list = [currentcity(x) for x in cityList]
        filtr = or_(*or_list)
    return filtr

def hometown(city=None, unknown=False):
    if unknown: 
        filtr = FacebookUser.hometown == None
    else:
        filtr = FacebookUser.hometown.ilike("%%%s%%" % city)
    return filtr

def hometownInList(cityList=[], unknown=False):
    if unknown: filtr = hometown(unknown=True)
    elif len(cityList) <1: filtr= None
    elif type(cityList[0]) == int:
        or_list = [zipcode(x, "hometown") for x in cityList]
        filtr = or_(*or_list)
    else:
        or_list = [hometown(x) for x in cityList]
        filtr = or_(*or_list)
    return filtr

def zipcode(zipcode=None, typeCity=None, unknown=False):
    if unknown:
        filtr = FacebookUser.locations == None
    else:
        filtr = FacebookUser.locations.any(zipcode=zipcode, type=typeCity)

    return filtr

def employer(employer=None, unknown=False):
    if unknown: filtr = FacebookUser.employer == None
    else: filtr = FacebookUser.employer.ilike("%%%s%%" % employer)

    return filtr

def employerInList(employerList=[], unknown=False):
    if unknown: filtr = employer(unknown=True)
    elif len(employerList) <1: filtr=FacebookUser.employer=="fsdfsdfsdfsdfdsfsdfsdfdsdsfsd"
    else:
        or_list = [employer(x) for x in employerList]
        filtr = or_(*or_list)
    return filtr

def school(school=None, unknown=False):
    if unknown:
        filtr = and_(
            FacebookUser.college == None,
            FacebookUser.highschool == None
        )
    else:
        filtr = or_(
            FacebookUser.college.ilike("%%%s%%" % school),
            FacebookUser.highschool.ilike("%%%s%%" % school),
        )

    return filtr

def college(college=None, unknown=False):
    if unknown: filtr = FacebookUser.college == None
    else: filtr =  FacebookUser.college.ilike("%%%s%%" % college)

    return filtr

def collegeInList(schoolList=[], unknown=False):
    if unknown: filtr = college(unknown=True)
    elif len(schoolList) <1: filtr= None
    else:
        or_list = [college(x) for x in schoolList]
        filtr = or_(*or_list)
    return filtr

def highSchoolInList(schoolList=[], unknown=False):
    if unknown: filtr = highschool(unknown=True)
    elif len(schoolList) <1: filtr= None
    else:
        or_list = [highschool(x) for x in schoolList]
        filtr = or_(*or_list)
    return filtr

def highschool(college=None, unknown=False):
    if unknown: filtr = FacebookUser.highschool == None
    else: filtr = FacebookUser.highschool.ilike("%%%s%%" % highschool)

    return filtr

def likes(unknown=False):
    if unknown: filtr = FacebookUser.pages == None
    else: filtr = FacebookUser.pages != None

    return filtr

def age(age = [0, 10000], unknown=False):
    if unknown: filtr = FacebookUser.birthday == None
    else:
        min_age = age[0]
        max_age = age[1]        
        tNow = datetime.now()
        filtr = FacebookUser.birthday.between(
                datetime(year=tNow.year-max_age, month=1, day=1), 
                datetime(year=tNow.year-min_age,month=1, day=1)
            )
        filtr2 = collegeInList(map( str , range(2014-max_age+20, 2014-min_age+22)))
        filtr3 = highSchoolInList(map( str , range(2014-max_age+16, 2014-min_age+18)))
        filtr = or_(filtr, filtr2, filtr3)
    
    return filtr

######################################################
# Parse CSV/TSV files
######################################################

def readEmploy():
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
                            employArray[i-1].append(line)
    return employArray

def readZip():
    zipArray= []
    with open('Location.tsv', 'rb') as c:
        creader = csv.reader(c, delimiter='\t')
        firstLine = True
        for row in creader:
            if firstLine:
                firstLine = False
            else:    
                zipArray.append(row[0])
    return [zipArray[0]] + map(int, zipArray[1:])

if __name__ == "__main__":

    """
    Example Usage of Dynamic Queries
    --------------------------------
    query = FacebookUser.query.filter(age(age=(20,30)))
    query = FacebookUser.query.filter(and_(age(age=(20,30)),sex('m')))
    query = FacebookUser.query.filter(and_(age(age=(20,30)),sex('m'),currentcity('evanston')))
    query = FacebookUser.query.filter(zipcode('60201'))
    query = FacebookUser.query.filter(employer('microsoft'))
    query = FacebookUser.query.filter(college('northwestern'))
    """

    # Still need read AGE, read LIKES

    funEmploy = [employerInList, "Employer" , readEmploy()]
    funAge = [age, "Age", [["15-24", 15,24], ["25-34", 25,34], ["35-44", 35,44], ["45-54", 45, 54], ["55-64", 55, 64], ["65+", 65, 200]]]
    funSex = [sex, "Sex", ["Mm", "Ff", "Oo"]]
    funCurrentCity  = [currentCityInList, "Current City", [readZip(), ["Illinois", "Illinois"]]]
    funHometown  = [hometownInList, "Hometown", [readZip(), ["Illinois", "Illinois"]]]

    funArray = [funEmploy, funAge , funSex, funCurrentCity, funHometown]

    def buildTree(depth = 0, funcArray = [], filters=None, printString = ""):

        if filters is not None: 
            users = FacebookUser.query.filter(filters).all()
            length = len(users)
        else: 
            users = []
            length = 0

        line = printString + " : " + str(length)
        print line 
        # f.write(line + "\n")

        if depth < len(funcArray) and (depth == 0 or length > 0):

            if depth == 0:

                for x in funcArray[depth][2]:
                    buildTree(
                        depth + 1, 
                        funcArray, 
                        funcArray[depth][0](x[1:]), 
                        funcArray[depth][1] + ": " + str(x[0])
                    )

                buildTree(
                    depth +1, 
                    funcArray, 
                    funcArray[depth][0](unknown=True), 
                    funcArray[depth][1] + ": Unknown" 
                )

            else:

                for x in funcArray[depth][2]:   
                    buildTree(depth +1, funcArray, 
                        and_(
                            filters, 
                            funcArray[depth][0](x[1:])
                        ), 
                        printString + ", " + funcArray[depth][1] + ": " + str(x[0])
                    )

                buildTree(depth +1, funcArray, 
                    and_(
                        filters, 
                        funcArray[depth][0](unknown=True)
                    ), 
                    printString + ", " + funcArray[depth][1] + ": Unknown" 
                )

        elif length>0:
            # print printString + " Count : " + str(length)
            for q in users:
                bitstring = ""
                for i in range(len(funcArray)):
                    seg = printString.split(",")[i]
                    cat = seg.split(":")[1][1:]
                    cats = map(lambda x: x[0], funcArray[i][2])+["Unknown"]
                    pos = cats.index(cat)
                    bitstring += "0"*pos + "1"+ ("0"*(len(cats)-pos-1))
                line = str(q.uid) +": "+ bitstring
                # f2.write(line+"\n")

    for i in range(len(funArray)):
        buildTree(funcArray=funArray[i:])