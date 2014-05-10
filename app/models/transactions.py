from . import db

class Transaction(db.Model):
	__tablename__ = 'transactions'

	id = db.Column(db.BigInteger, primary_key=True)
	timestamp = db.Column(db.DateTime)
	transact_type = db.Column(db.String, nullable=False)
	ref = db.Column(db.String, nullable=False)
	func = db.Column(db.String)
	data = db.Column(db.Text)