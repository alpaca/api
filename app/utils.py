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