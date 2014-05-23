from app.models import *
import sys, json

from sqlalchemy import and_, or_

from queries2 import funArray as funcArray

def bitvectorify2():

    users = {}

    def thing(user, inpt=None, unknown=False):
        user_query = FacebookUser.query.offset(i).limit(1)
        user_subquery = user_query.subquery()

        stuff = inpt[1:] if inpt else None

        user = user_query.first()
        filtr = func(stuff,unknown)

        test_filtr = FacebookUser.query.join(user_subquery, FacebookUser.uid == user_subquery.c.uid).filter(filtr).first()
        users[user.uid] = True if test_filtr else False
        print \
            user.uid, \
            user.username, \
            name, \
            inpt[0] if unknown==False else "Unknown", \
            users[user.uid]

    for i in range(FacebookUser.query.count()):
        for func, name, inputs in funcArray:
            for inpt in inputs:
                # if inpt[0] == "Fortune 1000": continue
                thing(i, inpt)
            thing(i, unknown=True)

if __name__ == "__main__":

    try:
        bitvectorify2(*sys.argv[1:])
    except IndexError:
        print "usage: python bitvectorify2.py"
