from . import db
from sqlalchemy import Table
from sqlalchemy.orm import mapper

def generate_contrib_model(fields):
    fnames = [f['name'] for f in fields]
    class Contributor(object):
        __tablename__ = "contributors"

        def __init__(self,csvname,**kwargs):
            self.csvname = csvname

            for k in kwargs:
                if k in fnames:
                    setattr(self,k,kwargs[k])
    
    columns = []
    for f in fields:
        columns.append(db.Column(f['name'],eval("db.%s" % f['db_type']), primary_key=f['primary_key']))

    for f in ['facebook_username','twitter_username','linkedin_username']:
        columns.append(db.Column(f,db.String, unique=True))

    metadata = db.metadata
    table = Table(Contributor.__tablename__, metadata, *columns)
    properties = {}
    for column in columns:
        properties[column.name] = column

    mapper(Contributor, table, properties=properties)

    return Contributor