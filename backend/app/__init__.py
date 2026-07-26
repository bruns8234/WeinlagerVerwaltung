import os
from flask import Flask
from flask_cors import CORS

from app.extensions import db, migrate
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.api.stammdaten import stammdaten_bp
    from app.api.lagerplaetze import lagerplaetze_bp
    from app.api.master_data import master_data_bp
    from app.api.lagerung import lagerung_bp
    from app.api.reporting import reporting_bp
    from app.api.backup import backup_bp

    app.register_blueprint(stammdaten_bp, url_prefix='/api/stammdaten')
    app.register_blueprint(lagerplaetze_bp, url_prefix='/api/lagerplaetze')
    app.register_blueprint(master_data_bp, url_prefix='/api/master')
    app.register_blueprint(lagerung_bp, url_prefix='/api/lagerung')
    app.register_blueprint(reporting_bp, url_prefix='/api/reporting')
    app.register_blueprint(backup_bp, url_prefix='/api/backup')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'WeinlagerVerwaltung API is running'}

    return app