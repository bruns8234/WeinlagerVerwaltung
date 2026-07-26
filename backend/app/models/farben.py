from app.extensions import db

class Farben(db.Model):
    """Liste der Weinfarben (rot, rosé, usw.)"""
    __tablename__ = 'farben'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bezeichnung = db.Column(db.String(16), nullable=False, unique=True)
    
    # Relationships
    stammdaten = db.relationship('Stammdaten', backref='farbe_ref', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bezeichnung': self.bezeichnung
        }
    
    def __repr__(self):
        return f'<Farben {self.bezeichnung}>'