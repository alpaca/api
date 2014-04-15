from . import db

class TwitterUser(db.Model):
    __tablename__ = 'twitter_users'
    id = db.Column(db.BigInteger, primary_key=True)
    screen_name = db.Column(db.String(80), unique=True)

    def __init__(self,user_id,screen_name):
        self.id = user_id
        self.screen_name = screen_name

    def __repr__(self):
        return "User " + str(self.id) + ": " + (self.screen_name if self.screen_name else "")
    def __str__(self):
        return "User " + str(self.id) + ": " + (self.screen_name if self.screen_name else "")