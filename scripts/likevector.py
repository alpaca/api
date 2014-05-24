from __future__ import division
from socialanalyzer import queries
from app.models import FacebookUser
from sqlalchemy import and_
import operator
import pickle


FILTER_FUNS = {
    'age': lambda x: queries.age(age=[int(x.split('-')[0]),
                                      int(x.split('-')[-1])])
}
# allCats = ["Animal breed", "Appliances", "Automobiles and parts", "Actor/director", "Amateur sports team", "Animal", "Attractions/things to do", "Anatomical structure", "Airport", "Album", "App page", "Automotive", "Bags/luggage", "Biotechnology", "Brand/company type", "Building materials", "Camera/photo", "Cars", "Cause", "Chef", "Chemicals", "City", "Clothing", "Coach", "Color", "Comedian", "Commercial equipment", "Company", "Computers", "Computers/internet website", "Country", "Degree", "Designer", "Electronics", "Energy/utility", "Engineering/construction", "Entertainer", "Entertainment website", "Entrepreneur", "Episode", "Event planning/event services", "Farming/agriculture", "Fictional character", "Field of study", "Furniture", "Games/toys", "Geographical feature", "High school status", "Hotel", "Industrials", "Insurance company", "Interest", "Island", "Jewelry/watches", "Journalist", "Just for fun", "Kitchen/cooking", "Lake", "Landmark", "Language", "Lawyer", "Legal/law", "Life event", "Literary editor", "Local business", "Local/travel website", "Magazine", "Media/news/publishing", "Medical procedure", "Middle school", "Mining/materials", "Monarch", "Mountain", "News personality", "News/media website", "Non-governmental organization (ngo)", "Non-profit organization", "Office supplies", "Organization", "Other", "Outdoor gear/sporting goods", "Patio/garden", "Personal blog", "Personal website", "Pet", "Pet services", "Pet supplies", "Phone/tablet", "Photographer", "Playlist", "Political ideology", "Political organization", "Political party", "Politician", "Producer", "Product/service", "Profession", "Professional services", "Public figure", "Public places", "Publisher", "Radio station", "Real estate", "Record label", "Recreation/sports website", "Baby goods/kids goods", "Religion", "Restaurant/cafe", "Retail and consumer merchandise", "River", "Science website", "Shopping/retail", "Small business", "Society/culture website", "Spas/beauty/personal care", "State/province/region", "Studio", "Teens/kids website", "Telecommunication", "Tools/equipment", "Tours/sightseeing", "Transit stop", "Transport/freight", "Transportation", "Travel/leisure", "Video game", "Vitamins/supplements", "Website", "Wine/spirits", "Work position", "Work project", "Work status", "Writer", "Year", "Aerospace/defense", "Art", "Artist", "Arts/entertainment/nightlife", "Arts/humanities website", "Athlete", "Author", "Bank/financial institution", "Bank/financial services", "Bar", "Book", "Book genre", "Book series", "Book store", "Business person", "Business services", "Business/economy website", "Church/religious organization", "Club", "Community", "Community organization", "Community/government", "Computers/technology", "Concentration or major", "Concert tour", "Concert venue", "Consulting/business services", "Course", "Dancer", "Diseases", "Doctor", "Drink", "Drugs", "Education", "Education website", "Education/work status", "Food", "Food/beverages", "Food/grocery", "Government official", "Government organization", "Government website", "Health/beauty", "Health/medical/pharmaceuticals", "Health/medical/pharmacy", "Health/wellness website", "Home decor", "Home improvement", "Home/garden website", "Hospital/clinic", "Household supplies", "Internet/software", "Library", "Movie", "Movie character", "Movie genre", "Movie theater", "Museum/art gallery", "Music", "Music award", "Music chart", "Music video", "Musical genre", "Musical instrument", "Musician/band", "Neighborhood", "Professional sports team", "Reference website", "Regional website", "School", "School sports team", "Software", "Song", "Sport", "Sports event", "Sports league", "Sports venue", "Sports/recreation/activities", "Teacher", "Tv", "Tv channel", "Tv genre", "Tv network", "Tv show", "Tv/movie award", "University"] 
# parallelCatVals = [0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0]
allCatDict = {'Animal breed' : 0, 'Appliances' : 0, 'Automobiles and parts' : 0, 'Actor/director' : 0, 'Amateur sports team' : 0, 'Animal' : 0, 'Attractions/things to do' : 0, 'Anatomical structure' : 0, 'Airport' : 0, 'Album' : 0, 'App page' : 0, 'Automotive' : 0, 'Bags/luggage' : 0, 'Biotechnology' : 0, 'Brand/company type' : 0, 'Building materials' : 0, 'Camera/photo' : 0, 'Cars' : 0, 'Cause' : 0, 'Chef' : 0, 'Chemicals' : 0, 'City' : 0, 'Clothing' : 0, 'Coach' : 0, 'Color' : 0, 'Comedian' : 0, 'Commercial equipment' : 0, 'Company' : 0, 'Computers' : 0, 'Computers/internet website' : 0, 'Country' : 0, 'Degree' : 0, 'Designer' : 0, 'Electronics' : 0, 'Energy/utility' : 0, 'Engineering/construction' : 0, 'Entertainer' : 0, 'Entertainment website' : 0, 'Entrepreneur' : 0, 'Episode' : 0, 'Event planning/event services' : 0, 'Farming/agriculture' : 0, 'Fictional character' : 0, 'Field of study' : 0, 'Furniture' : 0, 'Games/toys' : 0, 'Geographical feature' : 0, 'High school status' : 0, 'Hotel' : 0, 'Industrials' : 0, 'Insurance company' : 0, 'Interest' : 0, 'Island' : 0, 'Jewelry/watches' : 0, 'Journalist' : 0, 'Just for fun' : 0, 'Kitchen/cooking' : 0, 'Lake' : 0, 'Landmark' : 0, 'Language' : 0, 'Lawyer' : 0, 'Legal/law' : 0, 'Life event' : 0, 'Literary editor' : 0, 'Local business' : 0, 'Local/travel website' : 0, 'Magazine' : 0, 'Media/news/publishing' : 0, 'Medical procedure' : 0, 'Middle school' : 0, 'Mining/materials' : 0, 'Monarch' : 0, 'Mountain' : 0, 'News personality' : 0, 'News/media website' : 0, 'Non-governmental organization (ngo)' : 0, 'Non-profit organization' : 0, 'Office supplies' : 0, 'Organization' : 0, 'Other' : 0, 'Outdoor gear/sporting goods' : 0, 'Patio/garden' : 0, 'Personal blog' : 0, 'Personal website' : 0, 'Pet' : 0, 'Pet services' : 0, 'Pet supplies' : 0, 'Phone/tablet' : 0, 'Photographer' : 0, 'Playlist' : 0, 'Political ideology' : 0, 'Political organization' : 0, 'Political party' : 0, 'Politician' : 0, 'Producer' : 0, 'Product/service' : 0, 'Profession' : 0, 'Professional services' : 0, 'Public figure' : 0, 'Public places' : 0, 'Publisher' : 0, 'Radio station' : 0, 'Real estate' : 0, 'Record label' : 0, 'Recreation/sports website' : 0, 'Baby goods/kids goods' : 0, 'Religion' : 0, 'Restaurant/cafe' : 0, 'Retail and consumer merchandise' : 0, 'River' : 0, 'Science website' : 0, 'Shopping/retail' : 0, 'Small business' : 0, 'Society/culture website' : 0, 'Spas/beauty/personal care' : 0, 'State/province/region' : 0, 'Studio' : 0, 'Teens/kids website' : 0, 'Telecommunication' : 0, 'Tools/equipment' : 0, 'Tours/sightseeing' : 0, 'Transit stop' : 0, 'Transport/freight' : 0, 'Transportation' : 0, 'Travel/leisure' : 0, 'Video game' : 0, 'Vitamins/supplements' : 0, 'Website' : 0, 'Wine/spirits' : 0, 'Work position' : 0, 'Work project' : 0, 'Work status' : 0, 'Writer' : 0, 'Year' : 0, 'Aerospace/defense' : 0, 'Art' : 0, 'Artist' : 0, 'Arts/entertainment/nightlife' : 0, 'Arts/humanities website' : 0, 'Athlete' : 0, 'Author' : 0, 'Bank/financial institution' : 0, 'Bank/financial services' : 0, 'Bar' : 0, 'Book' : 0, 'Book genre' : 0, 'Book series' : 0, 'Book store' : 0, 'Business person' : 0, 'Business services' : 0, 'Business/economy website' : 0, 'Church/religious organization' : 0, 'Club' : 0, 'Community' : 0, 'Community organization' : 0, 'Community/government' : 0, 'Computers/technology' : 0, 'Concentration or major' : 0, 'Concert tour' : 0, 'Concert venue' : 0, 'Consulting/business services' : 0, 'Course' : 0, 'Dancer' : 0, 'Diseases' : 0, 'Doctor' : 0, 'Drink' : 0, 'Drugs' : 0, 'Education' : 0, 'Education website' : 0, 'Education/work status' : 0, 'Food' : 0, 'Food/beverages' : 0, 'Food/grocery' : 0, 'Government official' : 0, 'Government organization' : 0, 'Government website' : 0, 'Health/beauty' : 0, 'Health/medical/pharmaceuticals' : 0, 'Health/medical/pharmacy' : 0, 'Health/wellness website' : 0, 'Home decor' : 0, 'Home improvement' : 0, 'Home/garden website' : 0, 'Hospital/clinic' : 0, 'Household supplies' : 0, 'Internet/software' : 0, 'Library' : 0, 'Movie' : 0, 'Movie character' : 0, 'Movie genre' : 0, 'Movie theater' : 0, 'Museum/art gallery' : 0, 'Music' : 0, 'Music award' : 0, 'Music chart' : 0, 'Music video' : 0, 'Musical genre' : 0, 'Musical instrument' : 0, 'Musician/band' : 0, 'Neighborhood' : 0, 'Professional sports team' : 0, 'Reference website' : 0, 'Regional website' : 0, 'School' : 0, 'School sports team' : 0, 'Software' : 0, 'Song' : 0, 'Sport' : 0, 'Sports event' : 0, 'Sports league' : 0, 'Sports venue' : 0, 'Sports/recreation/activities' : 0, 'Teacher' : 0, 'Tv' : 0, 'Tv channel' : 0, 'Tv genre' : 0, 'Tv network' : 0, 'Tv show' : 0, 'Tv/movie award' : 0, 'University' : 0}


def like_percentages():

    users = FacebookUser.query.all()
    allUserVectors = {}

    for user in users:

        if user.pages != [] and user.pages != None:
            # print user.uid
            likeSum = 0
            # Reset dict
            tempDict = allCatDict.fromkeys(allCatDict, 0)

            for page in user.pages:
                if page.type in tempDict:
                    tempDict[page.type] += 1
                    # print '\t', page.type, ' : ', tempDict[page.type]
                    likeSum += 1
            # print 'SUM :: ', likeSum
            #could use a map here if i knew how
            for ctrg, val in tempDict.items():
                if val != 0:
                    # print '\t\t', ctrg, ' : ', val
                    tempDict[ctrg] = (val/likeSum) * 100
                    # print '\t\t', 'post-op ', ctrg, ' : ', tempDict[ctrg]

            
            allUserVectors[user.uid] = tempDict

    pickle.dump(allUserVectors, open('allUserVectors.pickle', 'wb'))

    return allUserVectors

    



def like_vector(usrDct):
    likeFile = open("likeVectors.txt", 'w')
    for usr in usrDct:
        print usr, ' : '
        lkVec = ''
        for key, val in usrDct[usr].items():
             lkVec += str(val) + ', '
             if val != 0:
                print key, ' : ', val

        likeFile.write(str(usr) + " : " + lkVec + "\n")



# def like_breakdown(user_lst):
#     cats = {}
#     for idx, user in enumerate(user_lst):
#         # import pdb; pdb.set_trace()
#         for page in user.pages:
#             if page.type in cats:
#                 cats[page.type] += 1
#             else:
#                 cats[page.type] = 1
#         print "User %i" % idx
#         # import pdb; pdb.set_trace()
#     return cats


# def get_users(users, **kwargs):
#     filters = []
#     for key in kwargs:
#         fn = FILTER_FUNS[key]
#         filters.append(fn(kwargs[key]))
#     return users.filter(
#         and_(
#             *filters
#         )).all()


# def dic_to_sorted(cats):
#     sorted_cats = sorted(cats.iteritems(), key=operator.itemgetter(1),
#                          reverse=True)
#     total = sum([int(x[1]) for x in sorted_cats])
#     out_str = ''
#     for pair in sorted_cats:
#         out_str += str(pair[0]) + ' : ' + str(pair[1]) + ' (' + \
#             str(int(pair[1])*100/total) + '%)\n'
#     return out_str


if __name__ == "__main__":
    # users = FacebookUser.query
    # filtered_users = get_users(users, age='20-30')
    # categories = like_breakdown(filtered_users)
    likeDict = like_percentages()
    like_vector(likeDict)



    # print dic_to_sorted(categories)
