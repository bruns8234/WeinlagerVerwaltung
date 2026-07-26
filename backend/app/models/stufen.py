from app.extensions import db

class Stufen(db.Model):
    """Liste der Qualitätsstufen"""
    __tablename__ = 'stufen'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stufe = db.Column(db.String(32), nullable=False, unique=True)
    stufenfolge = db.Column(db.Integer, nullable=False)
    
    # Relationships
    stammdaten = db.relationship('Stammdaten', backref='stufe_ref', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'stufe': self.stufe,
            'stufenfolge': self.stufenfolge
        }
    
    def __repr__(self):
        return f'<Stufen {self.stufe} (Rang: {self.stufenfolge})>'