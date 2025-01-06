from flask import Flask
from app.config import Config
from .models import db
from flask_migrate import Migrate
from app.routes.traduction_routes import traduction_bp
from app.routes.user_routes import user_bp
from app.routes.video_routes import video_bp
from app.routes.dictionary_routes import dictionary_bp
from app.routes.profile_routes import profile_bp
from app.routes.mail_routes import mailer_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar la base de datos y migraciones
    db.init_app(app)
    migrate = Migrate(app, db)

    # Registrar los Blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(traduction_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(dictionary_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(mailer_bp)

    return app
