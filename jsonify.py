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

def removew(d):
    for k, v in d.iteritems():
        if isinstance(v, dict):
            removew(v)
        elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
            d[k] = [removew(item) for item in v]
        elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], str):
            d[k] = [item.replace(" ", "_").replace("-", "_") for item in v]
        d[k.replace(" ", "_").replace("-", "_")] = d.pop(k)
    return d

def jsonify(fname, limit=None):

    # if bitvectors pickle doesn't exist
    # create it, otherwise load from picle

    if not os.path.isfile('bitvectors.pickle'):
        dict_bitvectors = bitvectorify()
        pickle.dump(dict_bitvectors, open('bitvectors.pickle', 'wb'))
    else:
        dict_bitvectors = pickle.load(open( "bitvectors.pickle", "rb" ))

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

    # empCat = ['retired', 'Intern', 'Entry_level', 'Management', 'Senior_Leadership', 'Owner_or_Founder', 'Fortune_1000', 'Family_Focused', 'Student', 'Public_Servant', 'Campaign_and_Politics', 'Religious_affiliation', 'Medical',  'Law', 'lawfirms', 'Tech', 'Unknown' ]
    # ageCat = ['15_24', '25_34', '35_44', '45_54', '55_64', '65_Over', 'Unknown']
    # sexCat = ['male', 'female', 'other', 'unknown']
    # currentcityCat = ['10th_District', 'Illinois', 'Unknown'] 
    # hometownCat = ['10th_District', 'Illinois', 'Unknown']
    # collegeCat = ['10th_District', 'Illinois', 'Unknown']
    # highschoolCat = ['10th_District', 'Illinois', 'Unknown']

    for user in FacebookUser.query.filter(filtr).limit(limit):
        js = user.to_json()

        # customize json

        for loc in js.get('locations'):
            loc['latlong'] = (loc['longitude'], loc['latitude'])

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
        jsonify(*sys.argv[1:])
    except IndexError:
        print "usage: python jsonify.py filename limit"
        raise


        # js['employment_cat']['retired'] = int(bitvectors[user.uid][0])
        # js['employment_cat']['Intern'] = int(bitvectors[user.uid][1])
        # js['employment_cat']['Entry-level'] = int(bitvectors[user.uid][2])
        # js['employment_cat']['Management'] = int(bitvectors[user.uid][3])
        # js['employment_cat']['Senior_Leadership'] = int(bitvectors[user.uid][4])
        # js['employment_cat']['Owner/Founder'] = int(bitvectors[user.uid][5])
        # js['employment_cat']['Fortune 1000'] = int(bitvectors[user.uid][6])
        # js['employment_cat']['Family-Focused'] = int(bitvectors[user.uid][7])
        # js['employment_cat']['Student'] = int(bitvectors[user.uid][8])
        # js['employment_cat']['Public_Servant'] = int(bitvectors[user.uid][9])
        # js['employment_cat']['Campaign/Politics'] = int(bitvectors[user.uid][10])
        # js['employment_cat']['Religious-affiliation'] = int(bitvectors[user.uid][11])
        # js['employment_cat']['Medical'] = int(bitvectors[user.uid][12])
        # js['employment_cat']['Law'] = int(bitvectors[user.uid][13])
        # js['employment_cat']['lawfirms'] = int(bitvectors[user.uid][14])
        # js['employment_cat']['Tech'] = int(bitvectors[user.uid][15])
        # js['employment_cat']['Unknown'] = int(bitvectors[user.uid][16])
        # js['age']['15-24'] = int(bitvectors[user.uid][17])
        # js['age']['25-34'] = int(bitvectors[user.uid][18])
        # js['age']['35-44'] = int(bitvectors[user.uid][19])
        # js['age']['45-54'] = int(bitvectors[user.uid][20])
        # js['age']['55-64'] = int(bitvectors[user.uid][21])
        # js['age']['65+'] = int(bitvectors[user.uid][22])
        # js['age']['Unknown'] = int(bitvectors[user.uid][23])
        # js['sex_cat']['male'] = int(bitvectors[user.uid][24])
        # js['sex_cat']['female'] = int(bitvectors[user.uid][25])
        # js['sex_cat']['other'] = int(bitvectors[user.uid][26])
        # js['sex_cat']['unknown'] = int(bitvectors[user.uid][27])
        # js['currentcity_cat']['10th District'] = int(bitvectors[user.uid][28])
        # js['currentcity_cat']['Illinois'] = int(bitvectors[user.uid][29])
        # js['currentcity_cat']['Unknown'] = int(bitvectors[user.uid][30])
        # js['hometown_cat']['10th District'] = int(bitvectors[user.uid][31])
        # js['hometown_cat']['Illinois'] = int(bitvectors[user.uid][32])
        # js['hometown_cat']['Unknown'] = int(bitvectors[user.uid][33])
        # js['highschool_cat']['10th District'] = int(bitvectors[user.uid][34])        
        # js['highschool_cat']['Illinois'] = int(bitvectors[user.uid][35])
        # js['highschool_cat']['Unknown'] = int(bitvectors[user.uid][36])
        # js['college_cat']['10th District'] = int(bitvectors[user.uid][37])
        # js['college_cat']['Illinois'] = int(bitvectors[user.uid][38])
        # js['college_cat']['Unknown'] = int(bitvectors[user.uid][39])