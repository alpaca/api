# -*- coding: utf-8 -*-

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

    return properties

def convert_result(sqlalchemymodel, socialscrapermodel):
    for col in socialscrapermodel.get_columns():
        if not getattr(sqlalchemymodel, col.name):
            setattr(sqlalchemymodel, col.name, getattr(socialscrapermodel, col.name))

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