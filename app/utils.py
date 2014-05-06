import json
from datetime import datetime

def get_model_properties(model):
	from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Date, Text, Boolean, Float
	properties = {}
	pkeys = []
	for col in model.get_columns():
		if col.foreign_key:
			properties[col.name] = Column(col.name, eval(col.type), ForeignKey(col.foreign_key_reference), primary_key=col.primary_key, unique=col.unique)
		else:
			properties[col.name] = Column(col.name, eval(col.type), primary_key=col.primary_key, unique=col.unique)
		if col.primary_key:
			pkeys.append(col.name)
	properties['__tablename__'] = model.__tablename__

	def init_fn(self,**kwargs):
		dupes = type(self).query # all FB users
		for key in pkeys: # uid
			# FacebookUser(uid=1000)
			# dupes.filter_by(uid=1000)
			dupes = dupes.filter_by(**{key: kwargs[key]})

		#import pdb; pdb.set_trace()
		dupe = None if len(dupes.all()) == 0 else dupes.first()
		created_at = dupe.created_at if dupe else datetime.now()

		super(type(self), self).__init__(created_at=created_at,updated_at=datetime.now())
		for k in kwargs:
			if dupe and not kwargs[k]:
				setattr(self,k,getattr(dupe,k))
			else:
				setattr(self,k,kwargs[k])

	properties['__init__'] = init_fn
	return properties

# def serialize_session(session):
#     attrs = ['headers', 'cookies', 'auth', 'proxies', 'hooks', 'params', 'verify']

#     session_data = {}

#     for attr in attrs:
#         session_data[attr] = getattr(session, attr)

#     return json.dumps(session_data)

# def deserialize_session(data):
#     session_data = json.loads(data)

#     if 'auth' in session_data:
#         session_data['auth'] = tuple(session_data['auth'])

#     if 'cookies' in session_data:
#         session_data['cookies'] = dict((key.encode(), val) for key, val in
#                 session_data['cookies'].items())

#     return req.session(**session_data)