import os
from flask import Flask
from flask_cors import CORS
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from models import db, Vessel
from routes import bp as main_bp


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    db.init_app(app)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        if not Vessel.query.filter_by(cfr="BGR001").first():
            sample_vessel = Vessel(
                cfr="BGR001",
                name="Black Sea Hunter",
                captain="Ivan Ivanov",
                valid_until="2026-12-31"
            )
            db.session.add(sample_vessel)
            db.session.commit()

    return app


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app = create_app()
    app.run(debug=debug_mode)
