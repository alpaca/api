from app.models import *
import sys, json
import os, pickle

from sqlalchemy import and_, or_

from queries2 import funArray as funcArray

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

def jsonify(fname, limit=None):

    # if bitvectors pickle doesn't exist
    # create it, otherwise load from picle

    if not os.path.isfile('bitvectors.pickle'):
        bitvectors = bitvectorify()
        pickle.dump(bitvectors, open('bitvectors.pickle', 'wb'))
    else:
        bitvectors = pickle.load(open( "bitvectors.pickle", "rb" ))

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

        js['employment'] = {}
        js['age'] = {}
        js['sex'] = {}
        js['current city'] = {}
        js['hometown'] = {}
        js['high school'] = {}
        js['college'] = {}
        js['employment']['retired'] = int(bitvectors[user.uid][0])
        js['employment']['Intern'] = int(bitvectors[user.uid][1])
        js['employment']['Entry-level'] = int(bitvectors[user.uid][2])
        js['employment']['Management'] = int(bitvectors[user.uid][3])
        js['employment']['Senior Leadership (position)'] = int(bitvectors[user.uid][4])
        js['employment']['Owner/Founder'] = int(bitvectors[user.uid][5])
        js['employment']['Fortune 1000'] = int(bitvectors[user.uid][6])
        js['employment']['Family-Focused'] = int(bitvectors[user.uid][7])
        js['employment']['Student'] = int(bitvectors[user.uid][8])
        js['employment']['Public Servant'] = int(bitvectors[user.uid][9])
        js['employment']['Campaign/Politics'] = int(bitvectors[user.uid][10])
        js['employment']['Religious-affiliation'] = int(bitvectors[user.uid][11])
        js['employment']['Medical'] = int(bitvectors[user.uid][12])
        js['employment']['Law (position)'] = int(bitvectors[user.uid][13])
        js['employment']['-- (lawfirms) --'] = int(bitvectors[user.uid][14])
        js['employment']['Tech'] = int(bitvectors[user.uid][15])
        js['employment']['Postal Workers'] = int(bitvectors[user.uid][16])
        js['employment']['American PW Union'] = int(bitvectors[user.uid][17])
        js['employment']['Unknown'] = int(bitvectors[user.uid][18])
        js['age']['15-24'] = int(bitvectors[user.uid][19])
        js['age']['25-34'] = int(bitvectors[user.uid][20])
        js['age']['35-44'] = int(bitvectors[user.uid][21])
        js['age']['45-54'] = int(bitvectors[user.uid][22])
        js['age']['55-64'] = int(bitvectors[user.uid][23])
        js['age']['65+'] = int(bitvectors[user.uid][24])
        js['age']['Unknown'] = int(bitvectors[user.uid][25])
        js['sex']['male'] = int(bitvectors[user.uid][26])
        js['sex']['female'] = int(bitvectors[user.uid][27])
        js['sex']['other'] = int(bitvectors[user.uid][28])
        js['sex']['unknown'] = int(bitvectors[user.uid][29])
        js['current city']['10th District'] = int(bitvectors[user.uid][30])
        js['current city']['Illinois'] = int(bitvectors[user.uid][31])
        js['current city']['Unknown'] = int(bitvectors[user.uid][32])
        js['hometown']['10th District'] = int(bitvectors[user.uid][33])
        js['hometown']['Illinois'] = int(bitvectors[user.uid][34])
        js['hometown']['Unknown'] = int(bitvectors[user.uid][35])
        js['high school']['10th District'] = int(bitvectors[user.uid][36])
        js['high school']['Illinois'] = int(bitvectors[user.uid][37])
        js['high school']['Unknown'] = int(bitvectors[user.uid][38])
        js['college']['10th District'] = int(bitvectors[user.uid][39])
        js['college']['Illinois'] = int(bitvectors[user.uid][40])
        js['college']['Unknown'] = int(bitvectors[user.uid][41])

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