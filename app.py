import os
from flask import Flask, jsonify, render_template, request
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
    fullname = db.Column(db.String(100), default="—")
    phone = db.Column(db.String(20), default="—")
    role = db.Column(db.String(50), default="Любител Рибар")
    vessel = db.Column(db.String(50), default="—")
    permit = db.Column(db.String(50), default="—")
    member_since = db.Column(db.String(30), default="Май 2026")

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
        sample_vessel = Vessel(cfr="BGR001", name="Black Sea Hunter", captain="Ivan Ivanov", valid_until="2026-12-31")
        db.session.add(sample_vessel)
        db.session.commit()

@app.route("/")
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
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        fullname=data.get('fullname', '—') if data.get('fullname') else '—',
        phone=data.get('phone', '—') if data.get('phone') else '—',
        role=data.get('role', 'Любител Рибар'),
        vessel=data.get('vessel', '—') if data.get('vessel') else '—',
        permit=data.get('permit', '—') if data.get('permit') else '—'
    )
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

@app.route("/api/user/<string:username>")
def get_user_details(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "username": user.username,
        "email": user.email,
        "fullname": user.fullname,
        "phone": user.phone,
        "role": user.role,
        "vessel": user.vessel,
        "permit": user.permit,
        "member_since": user.member_since
    })

@app.route("/api/user/<string:username>/edit", methods=["POST"])
def edit_user_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Not found"}), 404
    data = request.json
    user.fullname = data.get('fullname', user.fullname)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    db.session.commit()
    return jsonify({"message": "OK"})

@app.route("/api/user/<string:username>/password", methods=["POST"])
def change_password(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Not found"}), 404
    data = request.json
    user.password = data.get('password')
    db.session.commit()
    return jsonify({"message": "OK"})

@app.route("/api/check_permit/<string:cfr>")
def check_permit(cfr):
    v = Vessel.query.filter_by(cfr=cfr.upper()).first()
    if not v: 
        return jsonify({"error": "Not found"}), 404
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
    c = Catch(fish_type=data['fish_type'], location=data['location'])
    db.session.add(c)
    db.session.commit()
    return jsonify({"message": "OK"}), 201

if __name__ == "__main__":
    app.run(debug=True)