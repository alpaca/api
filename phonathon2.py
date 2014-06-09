import csv, datetime

from app.models import *
from app.models import db

def page_to_ask(page):

    if page.username == "NorthwesternAthletics":
        return "Their interest in NU Sports."
    elif page.username == "nufootball":
        return "Their interest NU Sports & Wildcats Football."
    elif page.username == "KelloggSchool":
        return "Their interest in Kellogg."
    elif page.username == "northwesternalumni":
        return "Their support for the Alumni Program."
    elif page.username == "MedillNU":
        return "Their enthusiasm for Medill."
    elif page.username == "feinbergschoolofmedicine":
        return "Their interest in Feinberg."
    elif page.username == "NUDanceMarathon":
        return "Their interest in Student Events, for example, DM or Dillo."
    elif page.username == "northwesternmbb":
        return "Their interest in NU Sports and NU Basketball."
    elif page.username == "thedailynorthwestern":
        return "Their interest in Student Publications like the Daily."
    elif page.username == "DilloDay":
        return "Their interest in Student Events, for example, DM or Dillo."
    elif page.username == "TGSNU":
        return "Their time with NU Graduate Studies."
    elif page.username == "mccormickengineering":
        return "Their interest McCormick."

augmented_users = []
users = []

with open('data.csv', 'rU') as csvfile:
    reader = csv.DictReader(csvfile)
    users = [ dict([(key,val.strip()) for key,val in row.iteritems()]) for row in reader]
    print users[0].keys()

    call_time = "9:00 PM"

    count = 0

    for user in users:

        # Try with only first name, last name
        name = user['FirstName'].split(" ")[0] + " " + user['LastName']
        fbuser = FacebookUser.query.filter(FacebookUser.name.ilike(name)).first()

        # Try with first name, middle name, last name
        if not fbuser:
            name = user['FirstName'] + " " + user['LastName']
            fbuser = FacebookUser.query.filter(FacebookUser.name.ilike(name)).first()

        # FBUSER

        asks = []

        if fbuser and fbuser.pages:
            pages = fbuser.pages #map(lambda page: page.name, user.pages)

            for page in pages:
                ask = page_to_ask(page)
                if ask: 
                    asks.append(ask)

        if user['Alloc1']:
            asks.append("They've previously donated to %s." % user['Alloc1'])
        
        if user['Activity1']:
            asks.append("They were involved with %s." % user['Activity1'])

        GradDate = datetime.datetime.strptime(user['GradDate1'], "%m%Y")
        
        if GradDate.year in [2010, 2005, 2000, 1995, 1990, 1985, 1980]:
            asks.append("It's a notable reunion year for the class of %i." % GradDate.year)

        # if user['Major1']:
        #     asks.append("Ask about studying %s" % user['Major1'])

        # if user['School']:
        #     asks.append("Ask about being in %s" % user['School'])

        final_output = "Here are some things to ask about\n" + "\n".join(asks)
        user['Asks'] = str(asks)

        print final_output

        augmented_users.append(user)

        print "-------------------------------------------"

with open('data2.csv','w') as csvfile:
    writer = csv.DictWriter(csvfile,augmented_users[0].keys())
    for user in augmented_users:
        writer.writerow(user)
        print user