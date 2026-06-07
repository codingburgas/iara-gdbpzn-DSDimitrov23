from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import now_date_str

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fullname = db.Column(db.String(100), default="—")
    phone = db.Column(db.String(20), default="—")
    role = db.Column(db.String(50), default="Любител Рибар")
    vessel = db.Column(db.String(50), default="—")
    permit = db.Column(db.String(50), default="—")
    member_since = db.Column(db.String(30), default=now_date_str)

class Vessel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cfr = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    captain = db.Column(db.String(100))
    valid_until = db.Column(db.String(20), default="2026-12-31")
    active = db.Column(db.Boolean, default=True)

class FishingTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_type = db.Column(db.String(100))
    price = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Catch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fish_type = db.Column(db.String(50))
    location = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Permit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(100))
    vessel_cfr = db.Column(db.String(20))
    permit_no = db.Column(db.String(50), unique=True)
    valid_from = db.Column(db.String(20), default=now_date_str)
    valid_until = db.Column(db.String(20), default='2026-12-31')
    active = db.Column(db.Boolean, default=True)

class Inspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inspector = db.Column(db.String(100))
    target_type = db.Column(db.String(30))
    target_id = db.Column(db.String(80))
    location = db.Column(db.String(150))
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Fine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    issued_to = db.Column(db.String(150))
    paid = db.Column(db.Boolean, default=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
