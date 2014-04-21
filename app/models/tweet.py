from . import db, BaseModel

class Tweet(db.Model, BaseModel):
    __tablename__ = 'tweets'
    id = db.Column(db.BigInteger,primary_key=True)
    timestamp = db.Column(db.BigInteger)
    user = db.Column(db.String(120), db.ForeignKey("twitter_users.screen_name"), nullable=False)
    content = db.Column(db.Text)

    def __init__(self,id,timestamp,screen_name,content,created_at=None,updated_at=None):
        self.id = id
        self.timestamp = timestamp
        self.user = screen_name
        self.content = content
        BaseModel.__init__(self,created_at,updated_at)

    def __repr__(self):
        return "Tweet " + str(self.id) + ": " + (self.content if self.content else "")
    def __str__(self):
        return "Tweet " + str(self.id) + ": " + (self.content if self.content else "")