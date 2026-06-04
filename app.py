import os
from flask import Flask
from flask_cors import CORS
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, Vessel
from routes import bp as main_bp


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    db.init_app(app)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        if not Vessel.query.filter_by(cfr="BGR001").first():
            sample_vessel = Vessel(cfr="BGR001", name="Black Sea Hunter", captain="Ivan Ivanov", valid_until="2026-12-31")
            db.session.add(sample_vessel)
            db.session.commit()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
