import sys; sys.path.append("..")

from __future__ import division
import os, pickle, json, requests, pdb
import psycopg2

try:
	conn=psycopg2.connect("dbname='alpaca_api_development' user='postgres' host='localhost' password='postgres'")
except:
    print "I am unable to connect to the database."


cur = conn.cursor()
try: 
	cur.execute("""Select id,contributed_by from boe_dem_donors;""")
# boe_contributors = Dem_Donors.query.from_statement("Select contributed_by from boe_dem_donors").all()
except:
	print "Can't select contributed_by"

data = cur.fetchall() # array of tuples of uid,name

for uid,name in data:
	thing = name.split(',') 
	if not len(thing) == 2: continue
	
	(last, first) = thing

	new_name = ("%s %s") % (first, last)
	new_name = new_name.lstrip().replace("'", " ")

	# print new_name

	# pdb.set_trace()

	try: 
		cur.execute("""UPDATE boe_dem_donors SET contributed_by='%s' WHERE id=%i;""" % (new_name, uid))
		# print "updated!"
	except:
		print "Can't update contributed_by"


conn.commit()
cur.close()