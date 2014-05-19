from app.models import *
import sys


def jsonify(fname):
	out = []
	for user in FacebookUser.query:
		js = user.to_json()
		out.append(js)
		print js

	with open(fname,'w') as f:
		f.write(unicode(out))

	return out

if __name__ == "__main__":
	try:
		jsonify(sys.argv[1])
	except IndexError:
		print "Incorrect Usage"