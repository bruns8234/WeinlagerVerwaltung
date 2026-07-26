from app.extensions import db

class Regionen(db.Model):
    """Liste aller Herkunftsorte"""
    __tablename__ = 'regionen'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    land = db.Column(db.String(32), nullable=False)
    region = db.Column(db.String(48), nullable=True)
    
    # Relationships
    stammdaten = db.relationship('Stammdaten', backref='region_ref', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'land': self.land,
            'region': self.region
        }
    
    def __repr__(self):
        return f'<Regionen {self.land}, {self.region}>'