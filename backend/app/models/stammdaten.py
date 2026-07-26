from app.extensions import db
from datetime import datetime

class Stammdaten(db.Model):
    """Stammdaten aller eingelagerten Flaschen"""
    __tablename__ = 'stammdaten'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    art_id = db.Column(db.Integer, db.ForeignKey('arten.id'), nullable=False)
    stufe_id = db.Column(db.Integer, db.ForeignKey('stufen.id'), nullable=False)
    herkunft_id = db.Column(db.Integer, db.ForeignKey('regionen.id'), nullable=False)
    jahrgang = db.Column(db.Integer, nullable=True)
    rebsorte = db.Column(db.String(128), nullable=True)
    farbe_id = db.Column(db.Integer, db.ForeignKey('farben.id'), nullable=True)
    inhalt = db.Column(db.Numeric(5, 2), nullable=True)
    kaufdatum = db.Column(db.Date, nullable=True)
    preis = db.Column(db.Numeric(10, 2), nullable=True)
    anzahl = db.Column(db.Integer, nullable=False)
    
    # Relationships
    bestand = db.relationship('Bestand', backref='stammdaten_ref', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'art_id': self.art_id,
            'stufe_id': self.stufe_id,
            'herkunft_id': self.herkunft_id,
            'jahrgang': self.jahrgang,
            'rebsorte': self.rebsorte,
            'farbe_id': self.farbe_id,
            'inhalt': float(self.inhalt) if self.inhalt else None,
            'kaufdatum': self.kaufdatum.isoformat() if self.kaufdatum else None,
            'preis': float(self.preis) if self.preis else None,
            'anzahl': self.anzahl
        }
    
    def to_dict_with_details(self):
        data = self.to_dict()
        data['art'] = self.art_ref.art if self.art_ref else None
        data['stufe'] = self.stufe_ref.stufe if self.stufe_ref else None
        data['herkunft_land'] = self.region_ref.land if self.region_ref else None
        data['herkunft_region'] = self.region_ref.region if self.region_ref else None
        data['farbe'] = self.farbe_ref.bezeichnung if self.farbe_ref else None
        return data
    
    def __repr__(self):
        return f'<Stammdaten {self.name} ({self.jahrgang})>'