from app.models import *
import sys, json
from sqlalchemy import and_, or_
from socialanalyzer.queries import *

### Leaving this code as is for backwards compatibility ###
funEmploy = [employerInList, "Employer" , readEmploy2()]
funAge = [age, "Age", [["15-24", 15,24], ["25-34", 25,34], ["35-44", 35,44], ["45-54", 45, 54], ["55-64", 55, 64], ["65+", 65, 200]]]
funSex = [sex, "Sex", ["Mm", "Ff", "Oo"]]
funCurrentCity  = [ currentCityInList, "Current City", [ readZip(), ["Illinois", "Illinois"]]]
funHometown  = [hometownInList, "Hometown", [readZip(), ["Illinois", "Illinois"]]]
funHighSchool = [highSchoolInList, "High School", [readZip(), ["Illinois", "Illinois"]]]
funCollege = [collegeInList, "College", [readZip(), ["Illinois", "Illinois"]]]
funcArray = [funEmploy, funAge , funSex, funCurrentCity, funHometown, funHighSchool, funCollege]

def bitvector_order():
    # PRINT ORDER OF CATEGORIES
    print "------------------"
    counter = 0
    for func, name, inputs in funcArray:
        for inpt in inputs:
            filtr = func(inpt[1:])
            print counter, name, inpt[0]
            counter += 1
        print counter, name, "Unknown"
        counter += 1
    print "------------------"

def bitvectorify():

    users = FacebookUser.query.all()
    allUsers = {}
    for user in users: allUsers[user.uid] = {'string': ''}

    def thing(name, inpt=None, unknown=False):
        stuff = inpt[1:] if inpt else None
        filtr = func(stuff, unknown)  
        title = inpt[0] if unknown==False else "Unknown"
        print name, title,  FacebookUser.query.filter(filtr).count()
        current_users = FacebookUser.query.filter(filtr).all()
        for user in users:
            allUsers[user.uid]['string'] += '1' if user in current_users else '0'
            if not name in allUsers[user.uid]: allUsers[user.uid][name] = {}
            allUsers[user.uid][name][title] = True if user in current_users else False

    for func, name, inputs in funcArray:
        for inpt in inputs:
            thing(name, inpt)
        thing(name, unknown=True)

    return allUsers

if __name__ == "__main__":

    try:
        args = sys.argv[1:]
    except IndexError:
        print "usage: python bitvectorify.py"

    allUsers = bitvectorify(*args)