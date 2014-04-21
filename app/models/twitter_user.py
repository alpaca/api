from . import db, BaseModel

class TwitterUser(db.Model, BaseModel):
    __tablename__ = 'twitter_users'
    id = db.Column(db.BigInteger, primary_key=True)
    screen_name = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self,user_id,screen_name,created_at=None,updated_at=None):
        self.id = user_id
        self.screen_name = screen_name
        BaseModel.__init__(self,created_at,updated_at)

    def __repr__(self):
        return "User " + str(self.id) + ": " + (self.screen_name if self.screen_name else "")
    def __str__(self):
        return "User " + str(self.id) + ": " + (self.screen_name if self.screen_name else "")