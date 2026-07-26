from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Stammdaten, Lagerplaetze, Bestand

lagerung_bp = Blueprint('lagerung', __name__)


@lagerung_bp.route('/einlagern', methods=['POST'])
def einlagern():
    """
    Wein einlagern: Flasche(n) an einen Lagerplatz legen.
    
    Erwartetes JSON:
    {
        "stammdaten_id": 1,
        "lagerplatz_id": 1,
        "anzahl": 6,
        "hinweis": "Optional"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Keine Daten übermittelt'}), 400
    
    stammdaten_id = data.get('stammdaten_id')
    lagerplatz_id = data.get('lagerplatz_id')
    anzahl = data.get('anzahl', 1)
    hinweis = data.get('hinweis', '')
    
    if not stammdaten_id or not lagerplatz_id:
        return jsonify({'error': 'stammdaten_id und lagerplatz_id sind erforderlich'}), 400
    
    if anzahl < 1:
        return jsonify({'error': 'Anzahl muss mindestens 1 sein'}), 400
    
    # Stammdaten prüfen
    stammdaten = Stammdaten.query.get(stammdaten_id)
    if stammdaten is None:
        return jsonify({'error': 'Stammdaten nicht gefunden'}), 404
    
    # Lagerplatz prüfen
    lagerplatz = Lagerplaetze.query.get(lagerplatz_id)
    if lagerplatz is None:
        return jsonify({'error': 'Lagerplatz nicht gefunden'}), 404
    
    # Prüfen ob Lagerplatz bereits belegt ist
    existing_bestand = Bestand.query.filter_by(lagerplatz_id=lagerplatz_id).first()
    if existing_bestand:
        return jsonify({
            'error': 'Lagerplatz ist bereits belegt',
            'bestehend': existing_bestand.to_dict_with_details()
        }), 400
    
    # Neuen Bestand erstellen
    neuer_bestand = Bestand(
        stammdaten_id=stammdaten_id,
        lagerplatz_id=lagerplatz_id,
        anzahl=anzahl,
        hinweis=hinweis
    )
    
    db.session.add(neuer_bestand)
    db.session.commit()
    
    return jsonify({
        'message': f'{anzahl} Flasche(n) erfolgreich eingelagert',
        'bestand': neuer_bestand.to_dict_with_details()
    }), 201


@lagerung_bp.route('/auslagern/<int:bestand_id>', methods=['DELETE'])
def auslagern(bestand_id):
    """
    Wein auslagern: Bestand vom Lagerplatz entfernen.
    
    Optional im Body:
    {
        "anzahl": 2  # Nur teilweise auslagern
    }
    """
    bestand = Bestand.query.get(bestand_id)
    if bestand is None:
        return jsonify({'error': 'Bestand nicht gefunden'}), 404
    
    data = request.get_json() or {}
    anzahl_auslagern = data.get('anzahl', bestand.anzahl)
    
    if anzahl_auslagern < 1:
        return jsonify({'error': 'Anzahl muss mindestens 1 sein'}), 400
    
    if anzahl_auslagern > bestand.anzahl:
        return jsonify({
            'error': f'Nur {bestand.anzahl} Flasche(n) vorhanden'
        }), 400
    
    stammdaten_info = bestand.stammdaten_ref.to_dict() if bestand.stammdaten_ref else None
    lagerplatz_info = bestand.lagerplatz_ref.to_dict() if bestand.lagerplatz_ref else None
    
    if anzahl_auslagern >= bestand.anzahl:
        # Komplette Auslagerung - Bestand löschen
        db.session.delete(bestand)
        db.session.commit()
        
        return jsonify({
            'message': f'{bestand.anzahl} Flasche(n) komplett ausgelagert',
            'stammdaten': stammdaten_info,
            'lagerplatz': lagerplatz_info
        }), 200
    else:
        # Partielle Auslagerung - Anzahl reduzieren
        bestand.anzahl -= anzahl_auslagern
        db.session.commit()
        
        return jsonify({
            'message': f'{anzahl_auslagern} Flasche(n) ausgelagert',
            'restbestand': bestand.anzahl,
            'bestand': bestand.to_dict_with_details()
        }), 200


@lagerung_bp.route('/umlagern/<int:bestand_id>', methods=['PUT'])
def umlagern(bestand_id):
    """
    Wein umlagern: Bestand von einem Lagerplatz an einen anderen verschieben.
    
    Erwartetes JSON:
    {
        "lagerplatz_id": 5
    }
    """
    bestand = Bestand.query.get(bestand_id)
    if bestand is None:
        return jsonify({'error': 'Bestand nicht gefunden'}), 404
    
    data = request.get_json()
    if not data or 'lagerplatz_id' not in data:
        return jsonify({'error': 'neue lagerplatz_id ist erforderlich'}), 400
    
    neuer_lagerplatz_id = data['lagerplatz_id']
    
    # Gleicher Lagerplatz?
    if neuer_lagerplatz_id == bestand.lagerplatz_id:
        return jsonify({'message': 'Bestand ist bereits an diesem Lagerplatz'}), 200
    
    # Neuen Lagerplatz prüfen
    neuer_lagerplatz = Lagerplaetze.query.get(neuer_lagerplatz_id)
    if neuer_lagerplatz is None:
        return jsonify({'error': 'Neuer Lagerplatz nicht gefunden'}), 404
    
    # Prüfen ob neuer Lagerplatz bereits belegt ist
    existing_bestand = Bestand.query.filter_by(lagerplatz_id=neuer_lagerplatz_id).first()
    if existing_bestand:
        return jsonify({
            'error': 'Neuer Lagerplatz ist bereits belegt',
            'belegt_mit': existing_bestand.to_dict_with_details()
        }), 400
    
    alter_lagerplatz = bestand.lagerplatz_ref.to_dict() if bestand.lagerplatz_ref else None
    
    # Umlagern
    bestand.lagerplatz_id = neuer_lagerplatz_id
    db.session.commit()
    
    return jsonify({
        'message': 'Bestand erfolgreich umgelagert',
        'alter_lagerplatz': alter_lagerplatz,
        'neuer_lagerplatz': neuer_lagerplatz.to_dict(),
        'bestand': bestand.to_dict_with_details()
    }), 200


@lagerung_bp.route('/bestaende', methods=['GET'])
def get_bestaende():
    """
    Alle Bestände abrufen.
    
    Query-Parameter:
    - stammdaten_id: Filter nach Wein
    - lagerplatz_id: Filter nach Lagerplatz
    - leer: '1' = nur belegte Plätze anzeigen
    """
    query = Bestand.query
    
    stammdaten_id = request.args.get('stammdaten_id')
    if stammdaten_id:
        query = query.filter_by(stammdaten_id=stammdaten_id)
    
    lagerplatz_id = request.args.get('lagerplatz_id')
    if lagerplatz_id:
        query = query.filter_by(lagerplatz_id=lagerplatz_id)
    
    bestaende = query.order_by(Bestand.erstellt_am.desc()).all()
    
    return jsonify([b.to_dict_with_details() for b in bestaende])


@lagerung_bp.route('/statistik', methods=['GET'])
def get_statistik():
    """
    Lagerstatistik:
    - Gesamtzahl Bestände
    - Gesamtzahl Flaschen
    - Belegte/leere Lagerplätze
    - Kapazitätsauslastung
    """
    from sqlalchemy import func
    
    gesamt_bestaende = Bestand.query.count()
    gesamt_flaschen = db.session.query(func.sum(Bestand.anzahl)).scalar() or 0
    gesamt_lagerplaetze = Lagerplaetze.query.count()
    belegte_lagerplaetze = db.session.query(func.count(func.distinct(Bestand.lagerplatz_id))).scalar() or 0
    leere_lagerplaetze = gesamt_lagerplaetze - belegte_lagerplaetze
    auslastung = (belegte_lagerplaetze / gesamt_lagerplaetze * 100) if gesamt_lagerplaetze > 0 else 0
    
    # Flaschen pro Regal
    flaschen_pro_regal = []
    regale = db.session.query(Lagerplaetze.regal).distinct().order_by(Lagerplaetze.regal).all()
    for regal_tuple in regale:
        regal = regal_tuple.regal
        lp_ids = [lp.id for lp in Lagerplaetze.query.filter_by(regal=regal).all()]
        flaschen = db.session.query(func.sum(Bestand.anzahl)).filter(
            Bestand.lagerplatz_id.in_(lp_ids)
        ).scalar() or 0
        flaschen_pro_regal.append({
            'regal': regal,
            'flaschen': flaschen
        })
    
    return jsonify({
        'gesamt_bestaende': gesamt_bestaende,
        'gesamt_flaschen': gesamt_flaschen,
        'gesamt_lagerplaetze': gesamt_lagerplaetze,
        'belegte_lagerplaetze': belegte_lagerplaetze,
        'leere_lagerplaetze': leere_lagerplaetze,
        'auslastung_prozent': round(auslastung, 1),
        'flaschen_pro_regal': flaschen_pro_regal
    })