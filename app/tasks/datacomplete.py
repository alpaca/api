from app.models import db, FacebookUser, Location
from sqlalchemy import or_
from geopy.geocoders import GoogleV3

import ast, re

def find_fb_place_addrs():
	users = FacebookUser.query.filter(
                    or_(
                        FacebookUser.college.isnot(None), 
                        FacebookUser.highschool.isnot(None)
                    )
                ).all()
	for user in users:
		print '[%s, %s]' % (user.college,user.highschool)
		for idx,obj in enumerate([user.college,user.highschool]):
			if obj:
				print obj
				for name in ast.literal_eval(obj).keys():
					loc_record = Location.query.filter_by(name=name.lower()).all()
					if len(loc_record) > 0:
						existing_loc = loc_record[0]
						new_loc = Location(	name=existing_loc.name,
											type = 'college' if idx == 0 else 'highschool',
											address=existing_loc.address,
											zipcode=existing_loc.zipcode,
											latitude=existing_loc.latitude,
											longitude=existing_loc.longitude,
											uid=user.uid)
					else:
						addr,zipcode,lat,lng = get_coords_for_place(name)
						new_loc = Location(	name=name.lower(),
											type = 'college' if idx == 0 else 'highschool',
											address=addr,
											zipcode=zipcode,
											latitude=lat,
											longitude=lng,
											uid=user.uid)
					
					db.session.merge(new_loc)
					print new_loc.address
		db.session.commit()

# name = db.Column(db.String, primary_key=True)
# address = db.Column(db.String, nullable=False)
# zipcode = db.Column(db.Integer)
# latitude = db.Column(db.Float)
# longitude = db.Column(db.Float)

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