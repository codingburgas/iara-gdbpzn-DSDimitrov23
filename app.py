import os
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'iara_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

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

with app.app_context():
    db.create_all()
    if not Vessel.query.filter_by(cfr="BGR001").first():
        vessel = Vessel(cfr="BGR001", name="Black Sea Hunter", captain="Ivan Ivanov")
        db.session.add(vessel)
        db.session.commit()

@app.route("/")
@app.route("/dashboard")
def index():
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/map")
def map_page():
    return render_template("map.html")

@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Exists"}), 400
    user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "OK"}), 201

@app.route("/api/login", methods=["POST"])
def login_user():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        return jsonify({"message": "OK", "username": user.username}), 200
    return jsonify({"error": "Invalid"}), 401

@app.route("/api/check_permit/<string:cfr>")
def check_permit(cfr):
    v = Vessel.query.filter_by(cfr=cfr.upper()).first()
    if not v: return jsonify({"error": "Not found"}), 404
    return jsonify({"vessel": v.name, "captain": v.captain, "expires": v.valid_until})

@app.route("/api/issue_ticket", methods=["POST"])
def issue_ticket():
    data = request.json
    t = FishingTicket(ticket_type=data['type'], price=float(data['price']))
    db.session.add(t)
    db.session.commit()
    return jsonify({"message": "OK"}), 201

@app.route("/api/save_catch", methods=["POST"])
def save_catch():
    data = request.json
    new_catch = Catch(fish_type=data['fish_type'], location=data['location'])
    db.session.add(new_catch)
    db.session.commit()
    return jsonify({"message": "Saved"}), 201

if __name__ == "__main__":
    app.run(debug=True)