from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Arten, Farben, Stufen, Regionen, Stammdaten, Bestand

master_data_bp = Blueprint('master_data', __name__)

# =============================================================================
# Arten
# =============================================================================

@master_data_bp.route('/arten', methods=['GET'])
def get_arten():
    """Alle Arten abrufen"""
    arten = Arten.query.order_by(Arten.art).all()
    return jsonify([a.to_dict() for a in arten])


@master_data_bp.route('/arten/<int:id>', methods=['GET'])
def get_art(id):
    """Einzelne Art abrufen"""
    art = Arten.query.get(id)
    if art is None:
        return jsonify({'error': 'Art nicht gefunden'}), 404
    return jsonify(art.to_dict())


@master_data_bp.route('/arten', methods=['POST'])
def create_art():
    """Neue Art erstellen"""
    data = request.get_json()
    if not data or not data.get('art'):
        return jsonify({'error': 'Art-Bezeichnung ist erforderlich'}), 400
    
    existing = Arten.query.filter_by(art=data['art']).first()
    if existing:
        return jsonify({'error': 'Art existiert bereits'}), 400
    
    neue_art = Arten(
        art=data['art'],
        info=data.get('info')
    )
    
    db.session.add(neue_art)
    db.session.commit()
    
    return jsonify(neue_art.to_dict()), 201


@master_data_bp.route('/arten/<int:id>', methods=['PUT'])
def update_art(id):
    """Art aktualisieren"""
    art = Arten.query.get(id)
    if art is None:
        return jsonify({'error': 'Art nicht gefunden'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Keine Daten übermittelt'}), 400
    
    if 'art' in data:
        existing = Arten.query.filter_by(art=data['art']).first()
        if existing and existing.id != id:
            return jsonify({'error': 'Art existiert bereits'}), 400
        art.art = data['art']
    
    if 'info' in data:
        art.info = data['info']
    
    db.session.commit()
    return jsonify(art.to_dict())


@master_data_bp.route('/arten/<int:id>', methods=['DELETE'])
def delete_art(id):
    """Art löschen"""
    art = Arten.query.get(id)
    if art is None:
        return jsonify({'error': 'Art nicht gefunden'}), 404
    
    if Stammdaten.query.filter_by(art_id=id).first():
        return jsonify({'error': 'Art wird noch in Stammdaten verwendet'}), 400
    
    db.session.delete(art)
    db.session.commit()
    
    return jsonify({'message': 'Art erfolgreich gelöscht'}), 200


# =============================================================================
# Farben
# =============================================================================

@master_data_bp.route('/farben', methods=['GET'])
def get_farben():
    """Alle Farben abrufen"""
    farben = Farben.query.order_by(Farben.bezeichnung).all()
    return jsonify([f.to_dict() for f in farben])


@master_data_bp.route('/farben/<int:id>', methods=['GET'])
def get_farbe(id):
    """Einzelne Farbe abrufen"""
    farbe = Farben.query.get(id)
    if farbe is None:
        return jsonify({'error': 'Farbe nicht gefunden'}), 404
    return jsonify(farbe.to_dict())


@master_data_bp.route('/farben', methods=['POST'])
def create_farbe():
    """Neue Farbe erstellen"""
    data = request.get_json()
    if not data or not data.get('bezeichnung'):
        return jsonify({'error': 'Bezeichnung ist erforderlich'}), 400
    
    existing = Farben.query.filter_by(bezeichnung=data['bezeichnung']).first()
    if existing:
        return jsonify({'error': 'Farbe existiert bereits'}), 400
    
    neue_farbe = Farben(bezeichnung=data['bezeichnung'])
    db.session.add(neue_farbe)
    db.session.commit()
    
    return jsonify(neue_farbe.to_dict()), 201


@master_data_bp.route('/farben/<int:id>', methods=['PUT'])
def update_farbe(id):
    """Farbe aktualisieren"""
    farbe = Farben.query.get(id)
    if farbe is None:
        return jsonify({'error': 'Farbe nicht gefunden'}), 404
    
    data = request.get_json()
    if not data or 'bezeichnung' not in data:
        return jsonify({'error': 'Bezeichnung ist erforderlich'}), 400
    
    existing = Farben.query.filter_by(bezeichnung=data['bezeichnung']).first()
    if existing and existing.id != id:
        return jsonify({'error': 'Farbe existiert bereits'}), 400
    
    farbe.bezeichnung = data['bezeichnung']
    db.session.commit()
    
    return jsonify(farbe.to_dict())


@master_data_bp.route('/farben/<int:id>', methods=['DELETE'])
def delete_farbe(id):
    """Farbe löschen"""
    farbe = Farben.query.get(id)
    if farbe is None:
        return jsonify({'error': 'Farbe nicht gefunden'}), 404
    
    if Stammdaten.query.filter_by(farbe_id=id).first():
        return jsonify({'error': 'Farbe wird noch in Stammdaten verwendet'}), 400
    
    db.session.delete(farbe)
    db.session.commit()
    
    return jsonify({'message': 'Farbe erfolgreich gelöscht'}), 200


# =============================================================================
# Stufen
# =============================================================================

@master_data_bp.route('/stufen', methods=['GET'])
def get_stufen():
    """Alle Stufen abrufen"""
    stufen = Stufen.query.order_by(Stufen.stufenfolge.desc()).all()
    return jsonify([s.to_dict() for s in stufen])


@master_data_bp.route('/stufen/<int:id>', methods=['GET'])
def get_stufe(id):
    """Einzelne Stufe abrufen"""
    stufe = Stufen.query.get(id)
    if stufe is None:
        return jsonify({'error': 'Stufe nicht gefunden'}), 404
    return jsonify(stufe.to_dict())


@master_data_bp.route('/stufen', methods=['POST'])
def create_stufe():
    """Neue Stufe erstellen"""
    data = request.get_json()
    if not data or not data.get('stufe') or 'stufenfolge' not in data:
        return jsonify({'error': 'Stufe und Stufenfolge sind erforderlich'}), 400
    
    existing = Stufen.query.filter_by(stufe=data['stufe']).first()
    if existing:
        return jsonify({'error': 'Stufe existiert bereits'}), 400
    
    neue_stufe = Stufen(
        stufe=data['stufe'],
        stufenfolge=data['stufenfolge']
    )
    
    db.session.add(neue_stufe)
    db.session.commit()
    
    return jsonify(neue_stufe.to_dict()), 201


@master_data_bp.route('/stufen/<int:id>', methods=['PUT'])
def update_stufe(id):
    """Stufe aktualisieren"""
    stufe = Stufen.query.get(id)
    if stufe is None:
        return jsonify({'error': 'Stufe nicht gefunden'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Keine Daten übermittelt'}), 400
    
    if 'stufe' in data:
        existing = Stufen.query.filter_by(stufe=data['stufe']).first()
        if existing and existing.id != id:
            return jsonify({'error': 'Stufe existiert bereits'}), 400
        stufe.stufe = data['stufe']
    
    if 'stufenfolge' in data:
        stufe.stufenfolge = data['stufenfolge']
    
    db.session.commit()
    return jsonify(stufe.to_dict())


@master_data_bp.route('/stufen/<int:id>', methods=['DELETE'])
def delete_stufe(id):
    """Stufe löschen"""
    stufe = Stufen.query.get(id)
    if stufe is None:
        return jsonify({'error': 'Stufe nicht gefunden'}), 404
    
    if Stammdaten.query.filter_by(stufe_id=id).first():
        return jsonify({'error': 'Stufe wird noch in Stammdaten verwendet'}), 400
    
    db.session.delete(stufe)
    db.session.commit()
    
    return jsonify({'message': 'Stufe erfolgreich gelöscht'}), 200


# =============================================================================
# Regionen
# =============================================================================

@master_data_bp.route('/regionen', methods=['GET'])
def get_regionen():
    """Alle Regionen abrufen"""
    regionen = Regionen.query.order_by(Regionen.land, Regionen.region).all()
    return jsonify([r.to_dict() for r in regionen])


@master_data_bp.route('/regionen/<int:id>', methods=['GET'])
def get_region(id):
    """Einzelne Region abrufen"""
    region = Regionen.query.get(id)
    if region is None:
        return jsonify({'error': 'Region nicht gefunden'}), 404
    return jsonify(region.to_dict())


@master_data_bp.route('/regionen', methods=['POST'])
def create_region():
    """Neue Region erstellen"""
    data = request.get_json()
    if not data or not data.get('land'):
        return jsonify({'error': 'Land ist erforderlich'}), 400
    
    neue_region = Regionen(
        land=data['land'],
        region=data.get('region')
    )
    
    db.session.add(neue_region)
    db.session.commit()
    
    return jsonify(neue_region.to_dict()), 201


@master_data_bp.route('/regionen/<int:id>', methods=['PUT'])
def update_region(id):
    """Region aktualisieren"""
    region = Regionen.query.get(id)
    if region is None:
        return jsonify({'error': 'Region nicht gefunden'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Keine Daten übermittelt'}), 400
    
    if 'land' in data:
        region.land = data['land']
    if 'region' in data:
        region.region = data['region']
    
    db.session.commit()
    return jsonify(region.to_dict())


@master_data_bp.route('/regionen/<int:id>', methods=['DELETE'])
def delete_region(id):
    """Region löschen"""
    region = Regionen.query.get(id)
    if region is None:
        return jsonify({'error': 'Region nicht gefunden'}), 404
    
    if Stammdaten.query.filter_by(herkunft_id=id).first():
        return jsonify({'error': 'Region wird noch in Stammdaten verwendet'}), 400
    
    db.session.delete(region)
    db.session.commit()
    
    return jsonify({'message': 'Region erfolgreich gelöscht'}), 200