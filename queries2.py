import csv
from app.models import *
from app.models import db
from sqlalchemy import or_, and_
from datetime import datetime
from dateutil import parser

###################################################################

# Queries

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

def city(city=None, unknown=False):
    if unknown: 
        filtr = and_(
            FacebookUser.currentcity == None,
            FacebookUser.hometown == None,
        )
    else:
        filtr = or_(
            FacebookUser.currentcity.ilike("%%%s%%" % city),
            FacebookUser.hometown.ilike("%%%s%%" % city),
        )

    return filtr

def zipcode(zipcode=None, unknown=False):
    if unknown:
        filtr = FacebookUser.locations == None
    else:
        filtr = FacebookUser.locations.any(zipcode=zipcode)

    return filtr

def employer(employer=None, unknown=False):
    if unknown: filtr = FacebookUser.employer == None
    else: filtr = FacebookUser.employer.ilike("%%%s%%" % employer)

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

def highschool(college=None, unknown=False):
    if unknown: filtr = FacebookUser.highschool == None
    else: filtr = FacebookUser.highschool.ilike("%%%s%%" % highschool)

    return filtr

def likes(unknown=False):
    if unknown: filtr = FacebookUser.pages == None
    else: filtr = FacebookUser.pages != None

    return filtr

###################################################################

# Examples

# Example 1
print "Example 1: Querying people of age 20 to 30"
query = FacebookUser.query.filter(
            age(age=(20,30))
        )
print map(lambda user: (user.username, user.birthday), query.all())
print "\n"

# Example 2
print "Example 2: Querying people of age 20 to 30 who are male"
query = FacebookUser.query.filter(
    and_(
        age(age=(20,30)),
        sex(sex='m')
    )
)
print map(lambda user: (user.username, user.birthday, user.sex), query.all())
print "\n"

# Example 3
print "Example 3: Querying people of age 20 to 30 who are male and from evanston"
query = FacebookUser.query.filter(
    and_(
        age(age=(20,30)),
        sex(sex='m'),
        city('evanston')
    )
)
print map(lambda user: (user.username, user.birthday, user.sex, user.currentcity, user.hometown), query.all())
print "\n"

# Example 4
print "Example 4: People who have zipcode 60201"
query = FacebookUser.query.filter(
    zipcode('60201')
)
print map(lambda user: (user.username, map(lambda location: (location.type, location.zipcode) ,user.locations)), query.all())
print "\n"

# Example 5
print "Example 5: People who's employer is microsoft"
query = FacebookUser.query.filter(
    employer('microsoft')
)
print map(lambda user: (user.username, user.employer), query.all())
print "\n"

# Example 6
print "Example 6: People who's college is Northwestern"
query = FacebookUser.query.filter(
    college('northwestern')
)
print map(lambda user: (user.username, user.college), query.all())
print "\n"

print "------------------------------------------------------------"

###################################################################

# Iterate through above queries

def employerInList(employerList=[], unknown=False):
    if unknown: filtr = employer(unknown=True)
    else:
        or_list = [employer(x) for x in employerList]
        filtr = or_(*or_list)
    return filtr

def zipcodeInList(zipCodeList=[], unknown=False):
    if unknown: filtr = zipcode(unknown=True)
    else:
        or_list = [zipcode(x) for x in zipCodeList]
        filtr = or_(*or_list)
    return filtr
###################################################################

# Code mildly modified from original queries.py

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
    return zipArray

funEmploy = [employerInList, "Employer" , readEmploy()]
funAge = [age, "Age", [["15-24", 15,24], ["25-34", 25,34], ["35-44", 35,44], ["45-54", 45, 54], ["55-64", 55, 64], ["65+", 65, 200]]]
funSex = [sex, "Sex", ["Mm", "Ff", "Oo"]]
funZipcode  = [zipcodeInList, "Zipcode", [readZip(), ["Illinois"]]]

funArray = [funEmploy, funAge , funSex, funZipcode]

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
                printString+", " + funcArray[depth][1] + ": Unknown" 
            )

    elif length>0:
        print printString + " Count : " + str(length)
        for q in users:
            bitstring = ""
            for i in range(len(funcArray)):
                seg = printString.split(",")[i]
                cat = seg.split(":")[1][1:]
                cats = map(lambda x: x[0], funArray[i][2])+["Unknown"]
                pos = cats.index(cat)
                bitstring += "0"*pos + "1"+ ("0"*(len(cats)-pos-1))
            line = str(q.uid) +": "+ bitstring
            # f2.write(line+"\n")

buildTree(funcArray=funArray)
