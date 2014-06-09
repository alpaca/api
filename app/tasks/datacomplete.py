from app.models import db, FacebookUser, Location
from sqlalchemy import and_, or_, not_
from sqlalchemy.exc import IntegrityError
from geopy.geocoders import GoogleV3,GeoNames
from geopy.exc import GeocoderServiceError
from socialanalyzer.queries import *

# import heatmap

import ast, re

def find_fb_place_addrs():
    users = FacebookUser.query.filter(
                    or_(
                        FacebookUser.college.isnot(None), 
                        FacebookUser.highschool.isnot(None)
                    )
                ).all()
    TYPES = ['college','highschool','currentcity','hometown']
    for user in users:
        print '[%s, %s, %s, %s]' % (user.college,user.highschool,user.currentcity,user.hometown,)
        for idx,obj in enumerate([user.college,user.highschool,user.currentcity,user.hometown]):
            tp = TYPES[idx]
            try:
                if obj:
                    if obj == user.currentcity or obj == user.hometown:
                        obj = '{"' + obj + '":""}' # trolol
                    for name in ast.literal_eval(obj).keys():
                        loc_record = Location.query.filter_by(name=name.lower()).all()
                        if len(loc_record) > 0:
                            existing_loc = loc_record[0]
                            new_loc = Location( name=existing_loc.name,
                                                type = tp,
                                                address=existing_loc.address,
                                                zipcode=existing_loc.zipcode,
                                                latitude=existing_loc.latitude,
                                                longitude=existing_loc.longitude,
                                                uid=user.uid)
                        else:
                            addr,zipcode,lat,lng = get_coords_for_place(name)
                            new_loc = Location( name=name.lower(),
                                                type = tp,
                                                address=addr,
                                                zipcode=zipcode,
                                                latitude=lat,
                                                longitude=lng,
                                                uid=user.uid)
                        
                        db.session.merge(new_loc)
                        print new_loc.address
            except GeocoderServiceError as ge:
                print "Caught %s" % str(ge)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print "Warning: Caught Integrity error (most likely someone who has the same college in the 'college' section, twice or more)"

# name = db.Column(db.String, primary_key=True)
# address = db.Column(db.String, nullable=False)
# zipcode = db.Column(db.Integer)
# latitude = db.Column(db.Float)
# longitude = db.Column(db.Float)

def get_zipcode_for_cities():
    locations_hometown = Location.query.filter_by(type='hometown').all()
    locations_curcity = Location.query.filter_by(type='currentcity').all()
    locations = locations_hometown + locations_curcity

    geolocator = GoogleV3()
    regex = re.compile(r'[A-Z]{2} [0-9]{5},')

    for idx,location in enumerate(locations):
        if location.zipcode == 0:
            try:
                point = (location.latitude,location.longitude)
                loc = geolocator.reverse(point)[0]
                addr = loc.address
                # print addr
                zipcode = regex.findall(addr)[0].split(' ')[1].rstrip(',')
                location.zipcode = zipcode
                print zipcode
                db.session.merge(location)
                db.session.commit()
            except KeyError:
                print "caught KeyError"
            except IndexError:
                print "caught IndexError"
            except TypeError:
                print "caught TypeError"
        else:
            print "zipcode already exists: %i" % idx

def get_coords_for_place(place):
    regex = re.compile("[A-Z]{2} [0-9]{5},")

    geolocator = GoogleV3()
    try:
        address, (lat,lng) = geolocator.geocode(place)
    except TypeError:
        return 'None', 0, 0, 0
    try:
        zipcode = regex.findall(address)[0].split(' ')[-1].rstrip(',')
    except IndexError:
        zipcode = 0
    return address, zipcode, lat, lng

def mark_donors(fname):
    uids = []
    with open(fname,'r') as f:
        for line in f:
            uids.append(int(line.rstrip(' \n').lstrip(' \n')))

    for user in FacebookUser.query:
        user.donor = 1 if user.uid in uids else 0
    db.session.commit()
    return

def mark_nu(fname):
    uids = []
    with open(fname,'r') as f:
        for line in f:
            uids.append(int(line.rstrip(' \n').lstrip(' \n')))

    for user in FacebookUser.query:
        user.nu = 1 if user.uid in uids else 0
    db.session.commit()
    return

def gen_Contact_Times():

    # employer_categories = readEmploy()

    empCat = dict( (x[0],x[1:]) for x in readEmploy2() )

    #Filters
    reallyOld = age([65, 1000])
    young = age([0, 24])
    normalAge = age([25,64])
    retired = employerInList(empCat['Retired'])
    employed = not_(employer(unknown=True))
    student = employerInList(empCat['Student'])
    internship = employerInList(empCat['Intern (position)'])
    religion = employerInList(empCat['Religious-affiliated (position)'])

    for user in FacebookUser.query:
        user.contact_time = ''
        #if old or retired
        if user.test_filter(reallyOld) or user.test_filter(retired):
            user.contact_time = '8am-2pm'
        #if student or young
        elif user.test_filter(student) or user.test_filter(young):
            user.contact_time = '5-10pm'
        #if a normal age
        elif user.test_filter(normalAge):
            user.contact_time = '8-9am or 4-9pm'
        #if employed and not a student or intern
        elif user.test_filter(employed) and not (user.test_filter(student) or user.test_filter(internship)):
            user.contact_time = '8-9am or 4-7pm'
        #Default
        else:
            user.contact_time = '8am-9pm'
        #if religious
        if user.test_filter(religion):
            user.contact_time += 'not on sunday or saturday'

        print user.uid, user.contact_time

    db.session.commit()
    return
# def make_heatmap():
#     lower = (35.4748172441,-93.7086556875)
#     upper = (40.4703178606,-84.0625583187)
#     pts = []
#     locs = Location.query.filter_by(type='hometown').all()
#     for l in locs:
#         if l.latitude > lower[0] and l.latitude < upper[0]:
#             if l.longitude > lower[1] and l.longitude < upper[1]:
#                 pts.append((l.latitude,l.longitude))

#     hm = heatmap.Heatmap()
#     img = hm.heatmap(pts, area = (lower,upper), dotsize=60, scheme='pgaitch')
#     img.save("heatmap.png")