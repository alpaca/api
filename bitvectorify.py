from app.models import *
import sys, json

from sqlalchemy import and_, or_

from queries2 import funArray as funcArray

def bitvectorify():
    # rows = open('bitarrays.txt').read().splitlines()
    # bitvectors = {}

    # for row in rows:
    #     print row
    #     user, vector = row.split(':')
    #     bitvectors[user] = vector

    print "------------------"

    # PRINT ORDER OF CATEGORIES
    for func, name, inputs in funcArray:
        for inpt in inputs:
            filtr = func(inpt[1:])
            print name, inpt[0]

    print "------------------"

    # Create dict of bitstrings, allUsers

    users = FacebookUser.query.all()
    allUsers = {}

    for user in users:
        allUsers[user.uid] = ''

    for func, name, inputs in funcArray:
        
        # Known Attributes of FUNC (i.e. age, sex, employer)
        for inpt in inputs:
            filtr = func(inpt[1:])
            print name, inpt[0], FacebookUser.query.filter(filtr).count()
            current_users = FacebookUser.query.filter(filtr).all()
            for user in users:
                if user in current_users:
                    allUsers[user.uid] += '1'
                else:
                    allUsers[user.uid] += '0'

        # Unknown of FUNC (i.e. unknown, age, unknown sex, unknown employer)
        filtr = func(unknown=True)
        print name, "Unknown", FacebookUser.query.filter(filtr).count()
        current_users = FacebookUser.query.filter(filtr).all()
        for user in users:
            if user in current_users:
                allUsers[user.uid] += '1'
            else:
                allUsers[user.uid] += '0'

    import pdb; pdb.set_trace()    

if __name__ == "__main__":

    try:
        bitvectorify(*sys.argv[1:])
    except IndexError:
        print "usage: python bitvectorify.py filename limit"