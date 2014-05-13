from app.models import db, FacebookUser, Location
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderServiceError

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
							new_loc = Location(	name=existing_loc.name,
												type = tp,
												address=existing_loc.address,
												zipcode=existing_loc.zipcode,
												latitude=existing_loc.latitude,
												longitude=existing_loc.longitude,
												uid=user.uid)
						else:
							addr,zipcode,lat,lng = get_coords_for_place(name)
							new_loc = Location(	name=name.lower(),
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

	for location in locations:
		addr,_ = geolocator.reverse((location.latitude,location.longitude))
		try:
			zipcode = regex.findall()[0].split(' ')[1].rstrip(',')
			location.zipcode = zipcode
			db.session.merge(location)
			db.session.commit()
		except KeyError:
			pass

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