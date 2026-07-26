from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Stammdaten, Arten, Stufen, Regionen, Farben

stammdaten_bp = Blueprint('stammdaten', __name__)


@stammdaten_bp.route('', methods=['GET'])
def get_stammdaten():
    """Alle Stammdaten abrufen, optional mit Details"""
    mit_details = request.args.get('details', '0')
    
    query = Stammdaten.query
    
    # Filter options
    art_id = request.args.get('art_id')
    if art_id:
        query = query.filter_by(art_id=art_id)
    
    stufe_id = request.args.get('stufe_id')
    if stufe_id:
        query = query.filter_by(stufe_id=stufe_id)
    
    herkunft_id = request.args.get('herkunft_id')
    if herkunft_id:
        query = query.filter_by(herkunft_id=herkunft_id)
    
    farbe_id = request.args.get('farbe_id')
    if farbe_id:
        query = query.filter_by(farbe_id=farbe_id)
    
    jahrgang = request.args.get('jahrgang')
    if jahrgang:
        query = query.filter_by(jahrgang=jahrgang)
    
    # Search by name
    search = request.args.get('search')
    if search:
        query = query.filter(Stammdaten.name.ilike(f'%{search}%'))
    
    stammdaten_liste = query.order_by(Stammdaten.name).all()
    
    if mit_details == '1':
        return jsonify([sd.to_dict_with_details() for sd in stammdaten_liste])
    return jsonify([sd.to_dict() for sd in stammdaten_liste])


@stammdaten_bp.route('/<int:id>', methods=['GET'])
def get_stammdatum(id):
    """Einzelnes Stammdatum abrufen"""
    sd = Stammdaten.query.get(id)
    if sd is None:
        return jsonify({'error': 'Stammdaten nicht gefunden'}), 404
    return jsonify(sd.to_dict_with_details())


@stammdaten_bp.route('', methods=['POST'])
def create_stammdatum():
    """Neues Stammdatum erstellen"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('anzahl'):
        return jsonify({'error': 'Name und Anzahl sind erforderlich'}), 400
    
    # Validate foreign keys
    art = Arten.query.get(data.get('art_id'))
    if not art:
        return jsonify({'error': 'Ungültige Art-ID'}), 400
    
    stufe = Stufen.query.get(data.get('stufe_id'))
    if not stufe:
        return jsonify({'error': 'Ungültige Stufen-ID'}), 400
    
    herkunft = Regionen.query.get(data.get('herkunft_id'))
    if not herkunft:
        return jsonify({'error': 'Ungültige Herkunft-ID'}), 400
    
    if data.get('farbe_id') and not Farben.query.get(data.get('farbe_id')):
        return jsonify({'error': 'Ungültige Farben-ID'}), 400
    
    # Parse kaufdatum if provided
    kaufdatum = None
    if data.get('kaufdatum'):
        try:
            kaufdatum = data['kaufdatum']
        except ValueError:
            return jsonify({'error': 'Ungültiges Datum-Format für kaufdatum'}), 400
    
    neues_stammdatum = Stammdaten(
        name=data['name'],
        art_id=data['art_id'],
        stufe_id=data['stufe_id'],
        herkunft_id=data['herkunft_id'],
        jahrgang=data.get('jahrgang'),
        rebsorte=data.get('rebsorte'),
        farbe_id=data.get('farbe_id'),
        inhalt=data.get('inhalt'),
        kaufdatum=kaufdatum,
        preis=data.get('preis'),
        anzahl=data['anzahl']
    )
    
    db.session.add(neues_stammdatum)
    db.session.commit()
    
    return jsonify(neues_stammdatum.to_dict_with_details()), 201


@stammdaten_bp.route('/<int:id>', methods=['PUT'])
def update_stammdatum(id):
    """Bestehendes Stammdatum aktualisieren"""
    sd = Stammdaten.query.get(id)
    if sd is None:
        return jsonify({'error': 'Stammdaten nicht gefunden'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Keine Daten übermittelt'}), 400
    
    # Validate foreign keys if provided
    if 'art_id' in data and not Arten.query.get(data['art_id']):
        return jsonify({'error': 'Ungültige Art-ID'}), 400
    
    if 'stufe_id' in data and not Stufen.query.get(data['stufe_id']):
        return jsonify({'error': 'Ungültige Stufen-ID'}), 400
    
    if 'herkunft_id' in data and not Regionen.query.get(data['herkunft_id']):
        return jsonify({'error': 'Ungültige Herkunft-ID'}), 400
    
    if 'farbe_id' in data and data['farbe_id'] and not Farben.query.get(data['farbe_id']):
        return jsonify({'error': 'Ungültige Farben-ID'}), 400
    
    # Update fields
    erlaubte_felder = [
        'name', 'art_id', 'stufe_id', 'herkunft_id', 'jahrgang',
        'rebsorte', 'farbe_id', 'inhalt', 'kaufdatum', 'preis', 'anzahl'
    ]
    
    for feld in erlaubte_felder:
        if feld in data:
            setattr(sd, feld, data[feld])
    
    db.session.commit()
    
    return jsonify(sd.to_dict_with_details())


@stammdaten_bp.route('/<int:id>', methods=['DELETE'])
def delete_stammdatum(id):
    """Stammdatum löschen"""
    sd = Stammdaten.query.get(id)
    if sd is None:
        return jsonify({'error': 'Stammdaten nicht gefunden'}), 404
    
    # Check if still in use
    from app.models import Bestand
    if Bestand.query.filter_by(stammdaten_id=id).first():
        return jsonify({'error': 'Stammdaten werden noch im Bestand verwendet'}), 400
    
    db.session.delete(sd)
    db.session.commit()
    
    return jsonify({'message': 'Stammdaten erfolgreich gelöscht'}), 200


@stammdaten_bp.route('/import', methods=['POST'])
def import_stammdaten():
    """Mehrere Stammdaten importieren (CSV/JSON)"""
    data = request.get_json()
    if not data or not isinstance(data, list):
        return jsonify({'error': 'Daten müssen ein Array sein'}), 400
    
    ergebnis = {
        'erfolgreich': [],
        'fehler': []
    }
    
    for idx, datum in enumerate(data):
        try:
            if not datum.get('name') or not datum.get('anzahl'):
                ergebnis['fehler'].append({
                    'index': idx,
                    'error': 'Name und Anzahl sind erforderlich'
                })
                continue
            
            # Validate foreign keys
            art = Arten.query.get(datum.get('art_id'))
            if not art:
                ergebnis['fehler'].append({
                    'index': idx,
                    'error': 'Ungültige Art-ID'
                })
                continue
            
            stufe = Stufen.query.get(datum.get('stufe_id'))
            if not stufe:
                ergebnis['fehler'].append({
                    'index': idx,
                    'error': 'Ungültige Stufen-ID'
                })
                continue
            
            herkunft = Regionen.query.get(datum.get('herkunft_id'))
            if not herkunft:
                ergebnis['fehler'].append({
                    'index': idx,
                    'error': 'Ungültige Herkunft-ID'
                })
                continue
            
            kaufdatum = datum.get('kaufdatum')
            
            neues_stammdatum = Stammdaten(
                name=datum['name'],
                art_id=datum['art_id'],
                stufe_id=datum['stufe_id'],
                herkunft_id=datum['herkunft_id'],
                jahrgang=datum.get('jahrgang'),
                rebsorte=datum.get('rebsorte'),
                farbe_id=datum.get('farbe_id'),
                inhalt=datum.get('inhalt'),
                kaufdatum=kaufdatum,
                preis=datum.get('preis'),
                anzahl=datum['anzahl']
            )
            
            db.session.add(neues_stammdatum)
            ergebnis['erfolgreich'].append(neues_stammdatum.to_dict_with_details())
            
        except Exception as e:
            ergebnis['fehler'].append({
                'index': idx,
                'error': str(e)
            })
            db.session.rollback()
    
    if ergebnis['erfolgreich']:
        db.session.commit()
    
    return jsonify(ergebnis), 200 if ergebnis['erfolgreich'] else 400