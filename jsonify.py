from app.models import *
import sys, json

from sqlalchemy import and_, or_

from queries2 import funArray as funcArray

def default(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        millis = int(
            calendar.timegm(obj.timetuple()) * 1000 + obj.microsecond / 1000
        )

        return millis

def del_none(d):
    """
    Delete keys with the value ``None`` in a dictionary, recursively.

    This alters the input so you may wish to ``copy`` the dict first.
    """
    # d.iteritems isn't used as you can't del or the iterator breaks.
    for key, value in d.items():
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d  # For convenience


def jsonify(fname, limit=None):

    rows = open('bitarrays.txt').read().splitlines()
    bitvectors = {}

    for row in rows:
        print row
        user, vector = row.split(':')
        bitvectors[user] = vector

    # Empty file
    f = open(fname,'w')
    f.close()

    f = open(fname,'a')

    filtr = and_(
                or_(
                    FacebookUser.currentcity.isnot(None), 
                    FacebookUser.hometown.isnot(None), 
                    FacebookUser.college.isnot(None), 
                    FacebookUser.highschool.isnot(None), 
                    FacebookUser.employer.isnot(None), 
                    FacebookUser.birthday.isnot(None),
                ),
                FacebookUser.pages != None,
                FacebookUser.locations != None
            )

    for user in FacebookUser.query.filter(filtr).limit(limit):
        js = user.to_json()

        # customize json

        for loc in js.get('locations'):
            loc['latlong'] = (loc['longitude'], loc['latitude'])

        print user.username, bitvectors[user.uid]
        
        js['is_retired'] = bitvectors[user.uid][0]
        

        # bitstring = ""
        # for func, name, inputs in funcArray:
        #     for inpt in inputs:
        #         filtr = func(inpt[1:])
        #         print user.username, user, name, inpt[0], FacebookUser.query.filter(filtr).count()

        js = del_none(js)
        # print json.dumps(js, default=default)
        f.write('{"index":{"_index":"alpaca","_type":"user","_id":%i}} \n' % js['uid'])
        json.dump(js, f, default=default)
        f.write('\n')

    f.close()

if __name__ == "__main__":
    try:
        jsonify(*sys.argv[1:])
    except IndexError:
        print "usage: python jsonify.py filename limit"