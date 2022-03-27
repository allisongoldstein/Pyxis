from app import login
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Card(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    word = db.Column(db.String(64), index=True, unique=True)
    translation = db.Column(db.String(1000), index=True)
    status = db.Column(db.String(64), index=True)
    nextReviewDate = db.Column(db.Date, index=True)
    lastInterval = db.Column(db.Integer)
    variants = db.relationship("Variant", backref='card', lazy=True)

    def __repr__(self):
        return '<Card {}>'.format(self.word)
    
class Target(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    source = db.Column(db.String(100), index=True)
    content = db.Column(db.String(1000), index=True)
    category = db.Column(db.String(200), index=True)
    notes = db.Column(db.String(400), index=True)
    uniqueWordCount = db.Column(db.Integer)

    def __repr__(self):
        return '<Target {}>'.format(self.source)

class Temp(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    listString = db.Column(db.String(2000), index=True)
    targetID = db.Column(db.Integer, db.ForeignKey('target.id'), index=True)

class Ignore(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    ignWord = db.Column(db.String(20), index=True)

class Variant(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    varWord = db.Column(db.String(20), index=True)
    standardID = db.Column(db.Integer, db.ForeignKey('card.id'))

class Appearance(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    wordID = db.Column(db.Integer, db.ForeignKey('card.id'), index=True)
    targetID = db.Column(db.Integer, db.ForeignKey('target.id'), index=True)

db.create_all()
db.session.commit()