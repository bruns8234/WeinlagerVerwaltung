from app.extensions import db
from datetime import datetime

class Bestand(db.Model):
    """Aktueller Lagerbestand"""
    __tablename__ = 'bestand'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stammdaten_id = db.Column(db.Integer, db.ForeignKey('stammdaten.id'), nullable=False)
    lagerplatz_id = db.Column(db.Integer, db.ForeignKey('lagerplaetze.id'), nullable=False)
    erstellt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    geaendert = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: Each storage location can only have one item
    __table_args__ = (
        db.UniqueConstraint('lagerplatz_id', name='uq_lagerplatz_bestand'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'stammdaten_id': self.stammdaten_id,
            'lagerplatz_id': self.lagerplatz_id,
            'erstellt': self.erstellt.isoformat() if self.erstellt else None,
            'geaendert': self.geaendert.isoformat() if self.geaendert else None
        }
    
    def to_dict_with_details(self):
        data = self.to_dict()
        data['stammdaten'] = self.stammdaten_ref.to_dict_with_details() if self.stammdaten_ref else None
        data['lagerplatz'] = self.lagerplatz_ref.to_dict() if self.lagerplatz_ref else None
        return data
    
    def __repr__(self):
        return f'<Bestand Stammdaten#{self.stammdaten_id} -> Lagerplatz#{self.lagerplatz_id}>'