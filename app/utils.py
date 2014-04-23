def get_model_properties(model):
	from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Date, Text, Boolean, Float
	properties = {}
	for col in model.get_columns():
		if col.foreign_key:
			properties[col.name] = Column(col.name, eval(col.type), ForeignKey(col.foreign_key_reference), primary_key=col.primary_key, unique=col.unique)
		else:
			properties[col.name] = Column(col.name, eval(col.type), primary_key=col.primary_key, unique=col.unique)
	properties['__tablename__'] = model.__tablename__
	return properties