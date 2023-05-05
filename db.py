class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Sring, unique=True)
    password = db.Column(db.Sring)
    email = db.Column(db.Sring, unique=True)