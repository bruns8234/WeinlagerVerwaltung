import os
from datetime import timedelta

class Config:
    # Datenbank-URI über Umgebungsvariable konfigurierbar
    # Beispiele:
    #   SQLite:      sqlite:///weinalager.db
    #   PostgreSQL:  postgresql://user:pass@localhost/weinalager
    #   MariaDB:     mysql+pymysql://user:pass@localhost/weinalager
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///weinalager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret Key für Session-Verwaltung
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JSON-Formatierung
    JSON_SORT_KEYS = False
    JSON_AS_ASCII = False
    
    # Pagination
    ITEMS_PER_PAGE = 50