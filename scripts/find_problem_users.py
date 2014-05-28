import sys; sys.path.append("..")
from app.models import db, FacebookPagesUsers
from sqlalchemy import func, select

x = select([FacebookPagesUsers.__table__.c.uid, func.count(FacebookPagesUsers.__table__.c.uid)]).group_by(FacebookPagesUsers.__table__.c.uid).having(func.count(FacebookPagesUsers.__table__.c.uid) == 1)
result = db.session.execute(x)
users = [x for x in result]
print users
print len(users)