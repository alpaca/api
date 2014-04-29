import os,sys
from time import time
from datetime import datetime
from urlparse import urlparse, parse_qs
from facebook import GraphAPI

import pdb

"""
The previous_url does not mean anything on the first request. It returns a blank data object.
"""

@celery.task()
def feed(username):
	def get_previous(previous_url):
		previous_url_parameters = parse_qs(urlparse(previous_url).query)
		return int(previous_url_parameters['since'][0])

	def get_next(next_url):
		next_url_parameters = parse_qs(urlparse(next_url).query)
		return int(next_url_parameters['until'][0])

	# ryan.berthold
	# user = "1cupcakelady" #sys.argv[1]

	graph = GraphAPI(os.getenv('FACEBOOK_APP_TOKEN'))
	profile = graph.get_object(username)

	print profile

	until = int(time())
	while True:

		print "Getting Feed Until: " + datetime.utcfromtimestamp(until).strftime('%Y-%m-%d %H:%M:%S')
		profile = graph.get_object(username + "/feed", until=str(until))
		if profile['data'] == []:
			print "End of Results"
			break
		since = get_previous(profile['paging']['previous'])
		until = get_next(profile['paging']['next'])

		print profile['data']

		for item in profile['data']:
			print item.get('type') + ": " + item.get('story', '') + item.get('message', '')