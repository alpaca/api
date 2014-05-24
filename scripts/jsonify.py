import sys; sys.path.append("..")
from app import environment
from app.models import *
import sys, json
import os, pickle

from sqlalchemy import and_, or_

from bitvectorify import bitvectorify

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

def removew(d):
    for k, v in d.iteritems():
        if isinstance(v, dict):
            removew(v)
        elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
            d[k] = [removew(item) for item in v]
        elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], str):
            d[k] = [item.replace(" ", "_").replace("-", "_").replace("(","").replace(")", "") for item in v]
        d[k.replace(" ", "_").replace("-", "_").replace("(","").replace(")", "")] = d.pop(k)
    return d

def jsonify(fname, limit=None):

    # if bitvectors pickle doesn't exist
    # create it, otherwise load from picle

    if not os.path.isfile('../data/bitvectors.pickle.save'):
        dict_bitvectors = bitvectorify()
        pickle.dump(dict_bitvectors, open('../data/bitvectors.pickle.save', 'wb'))
    else:
        dict_bitvectors = pickle.load(open( "../data/bitvectors.pickle.save", "rb" ))

    # bitvectors = dict((key, value['string']) for (key, value) in dict_bitvectors.items())

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

        if js['contact_time']:
            js['contact_time'] = js['contact_time'].replace(" ", "_").replace("-", "_").replace("(","").replace(")", "")

        # customize json

        for loc in js.get('locations'):
            loc['longlat'] = (float(loc['longitude']), float(loc['latitude']))

        # import pdb; pdb.set_trace()

        for page in js.get('pages'):
            if page['type']:
                page['type'] = page['type'].replace(" ", "_").replace("-", "_").replace("(","").replace(")", "")

        # Remove stupid bitstring
        del dict_bitvectors[user.uid]['string']

        # Replace bitvector dict with a list of the True values
        for k, v in dict_bitvectors[user.uid].iteritems():
            dict_bitvectors[user.uid][k] = [key for (key, value) in dict_bitvectors[user.uid][k].items() if value==True]

        if dict_bitvectors[user.uid]['Current City'] == []:
            dict_bitvectors[user.uid]['Current City'].append('Out of Illinois')

        if dict_bitvectors[user.uid]['Hometown'] == []:
            dict_bitvectors[user.uid]['Hometown'].append('Out of Illinois')

        if dict_bitvectors[user.uid]['College'] == []:
            dict_bitvectors[user.uid]['College'].append('Out of Illinois')

        if dict_bitvectors[user.uid]['High School'] == []:
            dict_bitvectors[user.uid]['High School'].append('Out of Illinois')

        dict_bitvectors[user.uid]['Age'] = filter(lambda thing: thing != "Unknown", dict_bitvectors[user.uid]['Age'])

        # Merge user dict with bitvector dict
        js.update(dict_bitvectors[user.uid])

        # Remove whitespace
        print removew(js)

        js = del_none(js)
        # print json.dumps(js, default=default)
        f.write('{"index":{"_index":"alpaca","_type":"user","_id":%i}} \n' % js['uid'])
        json.dump(js, f, default=default)
        f.write('\n')

        # import pdb; pdb.set_trace()

    f.close()

if __name__ == "__main__":

    try:
        args = sys.argv[1:]
    except IndexError:
        print "usage: python jsonify.py filename limit"

    jsonify(*args)