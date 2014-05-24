from __future__ import division
from app.models import *
from app.models import db
from sqlalchemy import func

# for user in db.session.query(FacebookUser.username, func.count(FacebookUser.username)).group_by(FacebookUser.username):
#     if user[1] == 1: continue
#     dupes = FacebookUser.query.filter_by(username=user[0]).all()
#     scores = []
#     for dupe in dupes:
#         scores.append(len(filter(lambda x: x, dupe.__dict__.values())) / len(dupe.__dict__.values()))
#     fucker = dupes[scores.index(min(scores))]
#     db.session.delete(fucker)
#     db.session.commit()

for page in db.session.query(FacebookPage.username, func.count(FacebookPage.username)).group_by(FacebookPage.username):
    if page[1] == 1: continue
    dupes = FacebookPage.query.filter_by(username=page[0]).all()
    print page, dupes
    fucker = dupes[0]
    db.session.delete(fucker)
    db.session.commit()

# len(filter(lambda x: x[1] > 1, db.session.query(FacebookPage.username, func.count(FacebookPage.username)).group_by(FacebookPage.username).all()))

