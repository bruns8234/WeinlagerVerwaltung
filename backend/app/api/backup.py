from flask import Blueprint, request, jsonify, Response
from app.extensions import db
from app.models import Stammdaten, Bestand, Arten, Farben, Stufen, Regionen, Lagerplaetze
import json
import io
from datetime import datetime

backup_bp = Blueprint('backup', __name__)


@backup_bp.route('/export/alles', methods=['GET'])
def export_alles():
    """
    Exportiert alle Daten als JSON-Backup.
    
    Returns:
    - Alle Stammdaten (Arten, Farben, Stufen, Regionen)
    - Alle Weine (Stammdaten)
    - Alle Lagerplätze
    - Alle Bestände
    """
    backup = {
        'version': '1.0',
        'erstellt': datetime.utcnow().isoformat(),
        'daten': {
            'arten': [],
            'farben': [],
            'stufen': [],
            'regionen': [],
            'stammdaten': [],
            'lagerplaetze': [],
            'bestand': []
        }
    }
    
    # Arten exportieren
    for art in Arten.query.all():
        backup['daten']['arten'].append(art.to_dict())
    
    # Farben exportieren
    for farbe in Farben.query.all():
        backup['daten']['farben'].append(farbe.to_dict())
    
    # Stufen exportieren
    for stufe in Stufen.query.all():
        backup['daten']['stufen'].append(stufe.to_dict())
    
    # Regionen exportieren
    for region in Regionen.query.all():
        backup['daten']['regionen'].append(region.to_dict())
    
    # Stammdaten (Weine) exportieren
    for wein in Stammdaten.query.all():
        backup['daten']['stammdaten'].append(wein.to_dict())
    
    # Lagerplätze exportieren
    for platz in Lagerplaetze.query.all():
        backup['daten']['lagerplaetze'].append(platz.to_dict())
    
    # Bestand exportieren
    for b in Bestand.query.all():
        backup['daten']['bestand'].append(b.to_dict())
    
    output = io.BytesIO()
    output.write(json.dumps(backup, indent=2, ensure_ascii=False).encode('utf-8'))
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename=weinlager_backup_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'}
    )


@backup_bp.route('/import/alles', methods=['POST'])
def import_alles():
    """
    Importiert ein vollständiges JSON-Backup.
    
    Erwartet:
    - JSON-Body mit der gleichen Struktur wie der Export
    - Query-Parameter 'replace' (true/false) bestimmt ob bestehende Daten gelöscht werden
    """
    data = request.get_json()
    
    if not data or 'daten' not in data:
        return jsonify({'error': 'Ungültiges Backup-Format'}), 400
    
    replace = request.args.get('replace', 'false').lower() == 'true'
    
    # Optional: Bestehende Daten löschen
    if replace:
        Bestand.query.delete()
        Stammdaten.query.delete()
        Lagerplaetze.query.delete()
        Regionen.query.delete()
        Stufen.query.delete()
        Farben.query.delete()
        Arten.query.delete()
        db.session.commit()
    
    fehler = []
    imported = {
        'arten': 0,
        'farben': 0,
        'stufen': 0,
        'regionen': 0,
        'stammdaten': 0,
        'lagerplaetze': 0,
        'bestand': 0
    }
    
    # Arten importieren
    for art_data in data['daten'].get('arten', []):
        try:
            art = Arten(**{k: v for k, v in art_data.items() if k != 'id'})
            db.session.add(art)
            imported['arten'] += 1
        except Exception as e:
            fehler.append(f'Art import fehlgeschlagen: {str(e)}')
    
    db.session.commit()
    
    # Farben importieren
    for farbe_data in data['daten'].get('farben', []):
        try:
            farbe = Farben(**{k: v for k, v in farbe_data.items() if k != 'id'})
            db.session.add(farbe)
            imported['farben'] += 1
        except Exception as e:
            fehler.append(f'Farbe import fehlgeschlagen: {str(e)}')
    
    db.session.commit()
    
    # Stufen importieren
    for stufe_data in data['daten'].get('stufen', []):
        try:
            stufe = Stufen(**{k: v for k, v in stufe_data.items() if k != 'id'})
            db.session.add(stufe)
            imported['stufen'] += 1
        except Exception as e:
            fehler.append(f'Stufe import fehlgeschlagen: {str(e)}')
    
    db.session.commit()
    
    # Regionen importieren
    for region_data in data['daten'].get('regionen', []):
        try:
            region = Regionen(**{k: v for k, v in region_data.items() if k != 'id'})
            db.session.add(region)
            imported['regionen'] += 1
        except Exception as e:
            fehler.append(f'Region import fehlgeschlagen: {str(e)}')
    
    db.session.commit()
    
    # Stammdaten importieren
    for wein_data in data['daten'].get('stammdaten', []):
        try:
            wein = Stammdaten(**{k: v for k, v in wein_data.items() if k != 'id'})
            db.session.add(wein)
            imported['stammdaten'] += 1
        except Exception as e:
            fehler.append(f'Wein import fehlgeschlagen: {str(e)}')
    
    db.session.commit()
    
    # Lagerplätze importieren
    for platz_data in data['daten'].get('lagerplaetze', []):
        try:
            platz = Lagerplaetze(**{k: v for k, v in platz_data.items() if k != 'id'})
            db.session.add(platz)
            imported['lagerplaetze'] += 1
        except Exception as e:
            fehler.append(f'Lagerplatz import fehlgeschlagen: {str(e)}')
    
    db.session.commit()
    
    # Bestand importieren
    for bestand_data in data['daten'].get('bestand', []):
        try:
            bestand = Bestand(**{k: v for k, v in bestand_data.items() if k != 'id'})
            db.session.add(bestand)
            imported['bestand'] += 1
        except Exception as e:
            fehler.append(f'Bestand import fehlgeschlagen: {str(e)}')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'imported': imported,
        'fehler': fehler
    })


@backup_bp.route('/export/stammdaten/json', methods=['GET'])
def export_stammdaten_json():
    """Exportiert nur die Stammdaten als JSON."""
    daten = {
        'arten': [a.to_dict() for a in Arten.query.all()],
        'farben': [f.to_dict() for f in Farben.query.all()],
        'stufen': [s.to_dict() for s in Stufen.query.all()],
        'regionen': [r.to_dict() for r in Regionen.query.all()]
    }
    
    output = io.BytesIO()
    output.write(json.dumps(daten, indent=2, ensure_ascii=False).encode('utf-8'))
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=stammdaten.json'}
    )


@backup_bp.route('/import/stammdaten/json', methods=['POST'])
def import_stammdaten_json():
    """Importiert Stammdaten aus JSON."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Keine Daten gefunden'}), 400
    
    imported = {'arten': 0, 'farben': 0, 'stufen': 0, 'regionen': 0}
    fehler = []
    
    for art_data in data.get('arten', []):
        try:
            # Prüfen ob bereits existiert
            existing = Arten.query.filter_by(art=art_data.get('art')).first()
            if not existing:
                art = Arten(**art_data)
                db.session.add(art)
                imported['arten'] += 1
        except Exception as e:
            fehler.append(f'Art: {str(e)}')
    
    for farbe_data in data.get('farben', []):
        try:
            existing = Farben.query.filter_by(bezeichnung=farbe_data.get('bezeichnung')).first()
            if not existing:
                farbe = Farben(**farbe_data)
                db.session.add(farbe)
                imported['farben'] += 1
        except Exception as e:
            fehler.append(f'Farbe: {str(e)}')
    
    for stufe_data in data.get('stufen', []):
        try:
            existing = Stufen.query.filter_by(stufe=stufe_data.get('stufe')).first()
            if not existing:
                stufe = Stufen(**stufe_data)
                db.session.add(stufe)
                imported['stufen'] += 1
        except Exception as e:
            fehler.append(f'Stufe: {str(e)}')
    
    for region_data in data.get('regionen', []):
        try:
            existing = Regionen.query.filter_by(
                land=region_data.get('land'),
                region=region_data.get('region')
            ).first()
            if not existing:
                region = Regionen(**region_data)
                db.session.add(region)
                imported['regionen'] += 1
        except Exception as e:
            fehler.append(f'Region: {str(e)}')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'imported': imported,
        'fehler': fehler
    })