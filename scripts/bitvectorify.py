import sys; sys.path.append("..")

from app.models import *
from app import environment
from socialanalyzer.queries import *

import sys, json
from sqlalchemy import and_, or_

from build_tree import funcArray

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

    bitvectors = {}

    def thing(name, inpt=None, unknown=False):
        stuff = inpt[1:] if inpt else None
        filtr = func(stuff, unknown)  
        title = inpt[0] if unknown==False else "Unknown"
        print name, title,  FacebookUser.query.filter(filtr).count()
        current_users = FacebookUser.query.filter(filtr).all()
        for user in FacebookUser.query:
            if not user.uid in bitvectors: bitvectors[user.uid] = {}
            if not name in bitvectors[user.uid]: bitvectors[user.uid][name] = {}
            bitvectors[user.uid][name][title] = True if user in current_users else False

    for func, name, inputs in funcArray:
        for inpt in inputs:
            thing(name, inpt)
        thing(name, unknown=True)

    return bitvectors

if __name__ == "__main__":

    try:
        args = sys.argv[1:]
    except IndexError:
        print "usage: python bitvectorify.py"

    import pickle

    bitvectors = bitvectorify(*args)
    pickle.dump(users, open('../data/bitvectors.pickle.save', 'wb'))
    