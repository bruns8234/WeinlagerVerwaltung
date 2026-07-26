from flask import Blueprint, request, jsonify, Response
from app.extensions import db
from app.models import Stammdaten, Bestand, Arten, Farben, Stufen, Regionen, Lagerplaetze
from sqlalchemy import func
import csv
import io

reporting_bp = Blueprint('reporting', __name__)


@reporting_bp.route('/uebersicht', methods=['GET'])
def uebersicht():
    """
    Weinübersicht: Alle Weine mit aktuellen Beständen.
    
    Query-Parameter:
    - suchbegriff: Freitextsuche über alle Textfelder
    - art_id: Filter nach Art
    - farbe_id: Filter nach Farbe
    - stufe_id: Filter nach Stufe
    - sort_by: Sortierfeld (default: 'weinname')
    - sort_order: 'asc' oder 'desc' (default: 'asc')
    """
    query = db.session.query(
        Stammdaten,
        func.sum(Bestand.anzahl).label('gesamt_flaschen')
    ).outerjoin(Bestand, Stammdaten.id == Bestand.stammdaten_id)
    
    # Filter
    suchbegriff = request.args.get('suchbegriff', '')
    if suchbegriff:
        suchpattern = f'%{suchbegriff}%'
        query = query.filter(
            db.or_(
                Stammdaten.weinname.like(suchpattern),
                Stammdaten.weininfo.like(suchpattern),
                Stammdaten.anmerkung.like(suchpattern)
            )
        )
    
    art_id = request.args.get('art_id')
    if art_id:
        query = query.filter(Stammdaten.art_id == art_id)
    
    farbe_id = request.args.get('farbe_id')
    if farbe_id:
        query = query.filter(Stammdaten.farbe_id == farbe_id)
    
    stufe_id = request.args.get('stufe_id')
    if stufe_id:
        query = query.filter(Stammdaten.stufe_id == stufe_id)
    
    # Sortierung
    sort_by = request.args.get('sort_by', 'weinname')
    sort_order = request.args.get('sort_order', 'asc')
    
    sort_fields = {
        'weinname': Stammdaten.weinname,
        'art': Arten.art,
        'farbe': Farben.bezeichnung,
        'stufe': Stufen.stufe,
        'erntejahr': Stammdaten.erntejahr,
        'gesamt_flaschen': func.sum(Bestand.anzahl)
    }
    
    sort_field = sort_fields.get(sort_by, Stammdaten.weinname)
    
    if sort_order == 'desc':
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())
    
    query = query.group_by(Stammdaten.id)
    results = query.all()
    
    weine = []
    for stammdaten, gesamt_flaschen in results:
        art = Arten.query.get(stammdaten.art_id) if stammdaten.art_id else None
        farbe = Farben.query.get(stammdaten.farbe_id) if stammdaten.farbe_id else None
        stufe = Stufen.query.get(stammdaten.stufe_id) if stammdaten.stufe_id else None
        region = Regionen.query.get(stammdaten.herkunft_id) if stammdaten.herkunft_id else None
        
        weine.append({
            'id': stammdaten.id,
            'weinname': stammdaten.weinname,
            'weininfo': stammdaten.weininfo,
            'erntejahr': stammdaten.erntejahr,
            'ernteinfo': stammdaten.ernteinfo,
            'anmerkung': stammdaten.anmerkung,
            'art': art.to_dict() if art else None,
            'farbe': farbe.to_dict() if farbe else None,
            'stufe': stufe.to_dict() if stufe else None,
            'herkunft': region.to_dict() if region else None,
            'gesamt_flaschen': gesamt_flaschen or 0
        })
    
    return jsonify(weine)


@reporting_bp.route('/lagerstatus', methods=['GET'])
def lagerstatus():
    """
    Lagerstatus: Visualisierung des Lagerbestands.
    
    Returns:
    - Regale mit ihren Lagerplätzen
    - Belegungsstatus jedes Platzes
    - Weininfo bei belegten Plätzen
    """
    regale = db.session.query(Lagerplaetze.regal).distinct().order_by(Lagerplaetze.regal).all()
    
    ergebnis = []
    for regal_tuple in regale:
        regal_name = regal_tuple.regal
        plaetze = Lagerplaetze.query.filter_by(regal=regal_name)\
            .order_by(Lagerplaetze.reihe, Lagerplaetze.position).all()
        
        regal_data = {
            'regal': regal_name,
            'plaetze': []
        }
        
        for platz in plaetze:
            bestand = Bestand.query.filter_by(lagerplatz_id=platz.id).first()
            
            platz_info = {
                'id': platz.id,
                'reihe': platz.reihe,
                'position': platz.position,
                'belegt': bestand is not None,
                'max_anzahl': platz.max_anzahl,
                'wein': None
            }
            
            if bestand and bestand.stammdaten_ref:
                sm = bestand.stammdaten_ref
                art = Arten.query.get(sm.art_id) if sm.art_id else None
                farbe = Farben.query.get(sm.farbe_id) if sm.farbe_id else None
                
                platz_info['wein'] = {
                    'stammdaten_id': sm.id,
                    'weinname': sm.weinname,
                    'erntejahr': sm.erntejahr,
                    'art': art.art if art else None,
                    'farbe': farbe.bezeichnung if farbe else None,
                    'anzahl': bestand.anzahl,
                    'bestand_id': bestand.id
                }
            
            regal_data['plaetze'].append(platz_info)
        
        ergebnis.append(regal_data)
    
    return jsonify(ergebnis)


@reporting_bp.route('/export/csv', methods=['GET'])
def export_csv():
    """
    Exportiere Weinübersicht als CSV.
    """
    query = db.session.query(
        Stammdaten,
        func.sum(Bestand.anzahl).label('gesamt_flaschen')
    ).outerjoin(Bestand, Stammdaten.id == Bestand.stammdaten_id).group_by(Stammdaten.id)
    
    results = query.all()
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # Header
    writer.writerow([
        'Weinname', 'Art', 'Farbe', 'Stufe', 'Erntejahr',
        'Ernteinfo', 'Herkunft', 'Gesamtflaschen', 'Anmerkung'
    ])
    
    for stammdaten, gesamt_flaschen in results:
        art = Arten.query.get(stammdaten.art_id) if stammdaten.art_id else None
        farbe = Farben.query.get(stammdaten.farbe_id) if stammdaten.farbe_id else None
        stufe = Stufen.query.get(stammdaten.stufe_id) if stammdaten.stufe_id else None
        region = Regionen.query.get(stammdaten.herkunft_id) if stammdaten.herkunft_id else None
        
        herkunft_text = ''
        if region:
            parts = []
            if region.land:
                parts.append(region.land)
            if region.region:
                parts.append(region.region)
            herkunft_text = ', '.join(parts)
        
        writer.writerow([
            stammdaten.weinname,
            art.art if art else '',
            farbe.bezeichnung if farbe else '',
            stufe.stufe if stufe else '',
            stammdaten.erntejahr or '',
            stammdaten.ernteinfo or '',
            herkunft_text,
            gesamt_flaschen or 0,
            stammdaten.anmerkung or ''
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=wein_uebersicht.csv'}
    )


@reporting_bp.route('/export/lager/csv', methods=['GET'])
def export_lager_csv():
    """
    Exportiere Lagerstatus als CSV.
    """
    regale = db.session.query(Lagerplaetze.regal).distinct().order_by(Lagerplaetze.regal).all()
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # Header
    writer.writerow([
        'Regal', 'Reihe', 'Position', 'Belegt', 'Weinname',
        'Erntejahr', 'Art', 'Farbe', 'Flaschen', 'Max'
    ])
    
    for regal_tuple in regale:
        regal_name = regal_tuple.regal
        plaetze = Lagerplaetze.query.filter_by(regal=regal_name)\
            .order_by(Lagerplaetze.reihe, Lagerplaetze.position).all()
        
        for platz in plaetze:
            bestand = Bestand.query.filter_by(lagerplatz_id=platz.id).first()
            
            if bestand and bestand.stammdaten_ref:
                sm = bestand.stammdaten_ref
                art = Arten.query.get(sm.art_id) if sm.art_id else None
                farbe = Farben.query.get(sm.farbe_id) if sm.farbe_id else None
                
                writer.writerow([
                    regal_name,
                    platz.reihe,
                    platz.position,
                    'Ja',
                    sm.weinname,
                    sm.erntejahr or '',
                    art.art if art else '',
                    farbe.bezeichnung if farbe else '',
                    bestand.anzahl,
                    platz.max_anzahl
                ])
            else:
                writer.writerow([
                    regal_name,
                    platz.reihe,
                    platz.position,
                    'Nein',
                    '', '', '', '', '',
                    platz.max_anzahl
                ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=lager_status.csv'}
    )