import csv, datetime

from app.models import *
from app.models import db

users = []

with open('data.csv', 'rU') as csvfile:
  reader = csv.DictReader(csvfile)
  users = [ dict([(key,val.strip()) for key,val in row.iteritems()]) for row in reader]
  print users[0].keys()

call_time = "9:00 PM"

count = 0

for user in users:
  if not user['Birthdate'] or not user['Birthdate'][0:2] != "00": continue
  birthdate = datetime.datetime.strptime(user['Birthdate'], "%m%d%Y")
  user['Birthdate'] = birthdate
  name = user['FirstName'].split(" ")[0] + " " + user['LastName']
  fbuser = FacebookUser.query.filter(FacebookUser.name.ilike(name)).first()

  # Try with middle name
  if not fbuser:
  	name = user['FirstName'] + " " + user['LastName']
  	fbuser = FacebookUser.query.filter(FacebookUser.name.ilike(name)).first()

  fbusername = fbuser.username if fbuser else ""
  print name.ljust(50) + fbusername.ljust(20) + "Current total: " + str(count)

  if fbuser:
  	count += 1
  	fbuser.nu = 1

  db.session.commit()

print "Number of users found: ", count

  # if birthdate > datetime.datetime.now() - 