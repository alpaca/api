from . import db

class User(db.Model):
    userid = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    pw_hash = db.Column(db.String(80))

    def __init__(self,userid,username,pw_hash):
        self.userid = userid
        self.username = username
        self.pw_hash = pw_hash

    def __repr__(self):
        return "User " + str(self.userid) + ": " + (self.username if self.username else "")