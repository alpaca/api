from app.models import FacebookUser

users = FacebookUser.query.all()
users = map(lambda x: x.username, users)
with open("schneider.txt", "r") as f: