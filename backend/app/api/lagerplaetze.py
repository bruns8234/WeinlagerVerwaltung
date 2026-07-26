from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Lagerplaetze, Bestand

lagerplaetze_bp = Blueprint('lagerplaetze', __name__)


@lagerplaetze_bp.route('', methods=['GET'])
def get_lagerplaetze():
    """Alle Lagerplätze abrufen, optional mit Belegungsstatus"""
    mit_bestand = request.args.get('mit_bestand', '0')
    
    lagerplaetze = Lagerplaetze.query.order_by(
        Lagerplaetze.regal, 
        Lagerplaetze.boden, 
        Lagerplaetze.fach
    ).all()
    
    if mit_bestand == '1':
        ergebnis = []
        for lp in lagerplaetze:
            lp_data = lp.to_dict()
            bestand = Bestand.query.filter_by(lagerplatz_id=lp.id).first()
            if bestand:
                lp_data['belegt'] = True
                lp_data['bestand'] = bestand.to_dict_with_details()
            else:
                lp_data['belegt'] = False
            ergebnis.append(lp_data)
        return jsonify(ergebnis)
    
    return jsonify([lp.to_dict() for lp in lagerplaetze])


@lagerplaetze_bp.route('/<int:id>', methods=['GET'])
def get_lagerplatz(id):
    """Einzelnen Lagerplatz abrufen mit Belegungsinfo"""
    lp = Lagerplaetze.query.get(id)
    if lp is None:
        return jsonify({'error': 'Lagerplatz nicht gefunden'}), 404
    
    data = lp.to_dict()
    bestand = Bestand.query.filter_by(lagerplatz_id=id).first()
    if bestand:
        data['belegt'] = True
        data['bestand'] = bestand.to_dict_with_details()
    else:
        data['belegt'] = False
    
    return jsonify(data)


@lagerplaetze_bp.route('', methods=['POST'])
def create_lagerplatz():
    """Neuen Lagerplatz erstellen"""
    data = request.get_json()
    
    if not data or not data.get('regal') or not data.get('boden') or not data.get('fach'):
        return jsonify({'error': 'Regal, Boden und Fach sind erforderlich'}), 400
    
    # Check for duplicate
    existing = Lagerplaetze.query.filter_by(
        regal=data['regal'],
        boden=data['boden'],
        fach=data['fach']
    ).first()
    
    if existing:
        return jsonify({'error': 'Lagerplatz existiert bereits'}), 400
    
    neuer_lagerplatz = Lagerplaetze(
        regal=data['regal'],
        boden=data['boden'],
        fach=data['fach']
    )
    
    db.session.add(neuer_lagerplatz)
    db.session.commit()
    
    return jsonify(neuer_lagerplatz.to_dict()), 201


@lagerplaetze_bp.route('/<int:id>', methods=['PUT'])
def update_lagerplatz(id):
    """Bestehenden Lagerplatz aktualisieren"""
    lp = Lagerplaetze.query.get(id)
    if lp is None:
        return jsonify({'error': 'Lagerplatz nicht gefunden'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Keine Daten übermittelt'}), 400
    
    # Check for duplicate if regal/boden/fach changed
    if any(key in data for key in ['regal', 'boden', 'fach']):
        regal = data.get('regal', lp.regal)
        boden = data.get('boden', lp.boden)
        fach = data.get('fach', lp.fach)
        
        existing = Lagerplaetze.query.filter_by(
            regal=regal, boden=boden, fach=fach
        ).first()
        
        if existing and existing.id != id:
            return jsonify({'error': 'Lagerplatz existiert bereits'}), 400
    
    # Cannot update if occupied
    if Bestand.query.filter_by(lagerplatz_id=id).first():
        return jsonify({'error': 'Lagerplatz ist belegt, zuerst auslagern'}), 400
    
    for feld in ['regal', 'boden', 'fach']:
        if feld in data:
            setattr(lp, feld, data[feld])
    
    db.session.commit()
    
    return jsonify(lp.to_dict())


@lagerplaetze_bp.route('/<int:id>', methods=['DELETE'])
def delete_lagerplatz(id):
    """Lagerplatz löschen"""
    lp = Lagerplaetze.query.get(id)
    if lp is None:
        return jsonify({'error': 'Lagerplatz nicht gefunden'}), 404
    
    # Check if occupied
    if Bestand.query.filter_by(lagerplatz_id=id).first():
        return jsonify({'error': 'Lagerplatz ist belegt, zuerst auslagern'}), 400
    
    db.session.delete(lp)
    db.session.commit()
    
    return jsonify({'message': 'Lagerplatz erfolgreich gelöscht'}), 200


@lagerplaetze_bp.route('/regale', methods=['GET'])
def get_regale():
    """Liste aller vorhandenen Regale"""
    regale = db.session.query(Lagerplaetze.regal).distinct().order_by(Lagerplaetze.regal).all()
    return jsonify([{'regal': r.regal} for r in regale])


@lagerplaetze_bp.route('/uebersicht', methods=['GET'])
def get_uebersicht():
    """Übersicht aller Regale mit Boden und Fach-Informationen"""
    regale = db.session.query(Lagerplaetze.regal).distinct().order_by(Lagerplaetze.regal).all()
    
    ergebnis = []
    for regal_tuple in regale:
        regal = regal_tuple.regal
        boden_liste = db.session.query(Lagerplaetze.boden).distinct().filter_by(
            regal=regal
        ).order_by(Lagerplaetze.boden).all()
        
        boden_data = []
        for boden_tuple in boden_liste:
            boden = boden_tuple.boden
            faecher = Lagerplaetze.query.filter_by(
                regal=regal, boden=boden
            ).order_by(Lagerplaetze.fach).all()
            
            fach_data = []
            for fach in faecher:
                fach_info = fach.to_dict()
                bestand = Bestand.query.filter_by(lagerplatz_id=fach.id).first()
                fach_info['belegt'] = bestand is not None
                if bestand:
                    fach_info['stammdaten_name'] = bestand.stammdaten_ref.name if bestand.stammdaten_ref else None
                    fach_info['stammdaten_jahrgang'] = bestand.stammdaten_ref.jahrgang if bestand.stammdaten_ref else None
                fach_data.append(fach_info)
            
            boden_data.append({
                'boden': boden,
                'faecher': fach_data
            })
        
        ergebnis.append({
            'regal': regal,
            'boeden': boden_data
        })
    
    return jsonify(ergebnis)