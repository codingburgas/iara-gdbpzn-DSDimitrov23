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

class Vessel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cfr = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    captain = db.Column(db.String(100))
    tonnage = db.Column(db.Float)
    valid_until = db.Column(db.String(20), default="2026-12-31")
    active = db.Column(db.Boolean, default=True)

class FishingTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_type = db.Column(db.String(100))
    price = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    if not Vessel.query.filter_by(cfr="BGR001").first():
        new_vessel = Vessel(
            cfr="BGR001", 
            name="Black Sea Hunter", 
            captain="Ivan Ivanov",
            tonnage=15.5
        )
        db.session.add(new_vessel)
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

@app.route("/api/check_permit/<string:cfr>")
def check_permit(cfr):
    vessel = Vessel.query.filter_by(cfr=cfr.upper()).first()
    if not vessel:
        return jsonify({"error": "Корабът не е намерен"}), 404
    
    return jsonify({
        "status": "Valid", 
        "vessel": vessel.name, 
        "captain": vessel.captain,
        "expires": vessel.valid_until
    })

@app.route("/api/issue_ticket", methods=["POST"])
def issue_ticket():
    data = request.json
    try:
        new_ticket = FishingTicket(
            ticket_type=data['type'],
            price=float(data['price'])
        )
        db.session.add(new_ticket)
        db.session.commit()
        return jsonify({"message": "Успешно записан билет!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)