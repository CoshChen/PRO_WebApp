from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_desc = db.Column(db.String(50), unique=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(150), unique=True)
    prov_id = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    pros = db.relationship('Pro')
    

class Pro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hrsn_1 = db.Column(db.Integer)
    hrsn_2 = db.Column(db.Integer)
    hrsn_3 = db.Column(db.Integer)
    hrsn_4 = db.Column(db.Integer)
    hrsn_5 = db.Column(db.Integer)
    hrsn_6 = db.Column(db.Integer)
    med_1 = db.Column(db.Integer)
    med_2 = db.Column(db.Integer)
    med_3 = db.Column(db.Integer)
    med_4 = db.Column(db.Integer)
    
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

