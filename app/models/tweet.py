from . import db

class Tweet(db.Model):
    __tablename__ = 'tweets'
    id = db.Column(db.Integer,primary_key=True)
    timestamp = db.Column(db.Integer)
    user = db.Column(db.BigInteger, db.ForeignKey("twitter_users.id"), nullable=False)
    content = db.Column(db.Text)

    def __init__(self,id,timestamp,screen_name,content):
        self.id = id
        self.timestamp = timestamp
        self.user = screen_name
        self.content = content

    def __repr__(self):
        return "Tweet " + str(self.id) + ": " + (self.content if self.content else "")
    def __str__(self):
        return "Tweet " + str(self.id) + ": " + (self.content if self.content else "")