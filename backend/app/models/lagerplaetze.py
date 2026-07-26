from app.extensions import db

class Lagerplaetze(db.Model):
    """Liste aller vorhandenen Lagerplätze"""
    __tablename__ = 'lagerplaetze'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    regal = db.Column(db.Integer, nullable=False)
    boden = db.Column(db.Integer, nullable=False)
    fach = db.Column(db.Integer, nullable=False)
    
    # Unique constraint: Each storage location can only exist once
    __table_args__ = (
        db.UniqueConstraint('regal', 'boden', 'fach', name='uq_regal_boden_fach'),
    )
    
    # Relationships
    bestand = db.relationship('Bestand', backref='lagerplatz_ref', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'regal': self.regal,
            'boden': self.boden,
            'fach': self.fach
        }
    
    def __repr__(self):
        return f'<Lagerplatz R{self.regal}/B{self.boden}/F{self.fach}>'