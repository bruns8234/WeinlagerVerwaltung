from app.extensions import db
from datetime import datetime

class Arten(db.Model):
    """Liste aller Getränkearten (Wein, Sekt, usw.)"""
    __tablename__ = 'arten'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    art = db.Column(db.String(20), nullable=False, unique=True)
    info = db.Column(db.String(80), nullable=True)
    
    # Relationships
    stammdaten = db.relationship('Stammdaten', backref='art_ref', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'art': self.art,
            'info': self.info
        }
    
    def __repr__(self):
        return f'<Arten {self.art}>'