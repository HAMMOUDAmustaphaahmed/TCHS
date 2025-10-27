from flask import send_file
from flask import send_from_directory
from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time, timedelta
import hashlib
import pytz
import json
from filter_functions import (
    SeasonContext, 
    season_required,
    filter_adherents,
    filter_paiements,
    filter_presences,
    filter_seances,
    generate_season_code,
    get_season_codes
)
from functools import wraps

# Initialize the Flask application
app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'your_secret_key'  # Remplacez par une clé sécurisée

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/tchs'  # Update with your DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


UPLOAD_FOLDER = './bon_de_recette'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ajouter ces fonctions au début de votre fichier app.py après les imports

from functools import wraps
from flask import session, redirect, url_for, flash

def get_current_saison():
    """
    Récupère l'année de saison depuis la session
    Retourne None si pas défini
    """
    year = session.get('year')
    return int(year) if year is not None else None

def require_saison(f):
    """
    Décorateur pour s'assurer qu'une saison est sélectionnée
    Redirige vers login si aucune saison n'est définie
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'year' not in session:
            flash("Veuillez sélectionner une année de saison.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def filter_adherents_by_saison(query=None):
    """
    Filtre les adhérents par la saison en cours
    
    Args:
        query: Query SQLAlchemy existante (optionnel)
    
    Returns:
        Query filtrée par code_saison
    """
    year = get_current_saison()
    if query is None:
        query = Adherent.query
    
    if year:
        # Générer les codes saison possibles pour cette année
        code_saison_annuel = f"S{year}"
        code_saison_ete = f"E{year}"
        
        query = query.filter(
            or_(
                Adherent.code_saison == code_saison_annuel,
                Adherent.code_saison == code_saison_ete
            )
        )
    
    return query

def filter_paiements_by_saison(query=None):
    """
    Filtre les paiements par la saison en cours
    
    Args:
        query: Query SQLAlchemy existante (optionnel)
    
    Returns:
        Query filtrée par code_saison
    """
    year = get_current_saison()
    if query is None:
        query = Paiement.query
    
    if year:
        code_saison_annuel = f"S{year}"
        code_saison_ete = f"E{year}"
        
        query = query.filter(
            or_(
                Paiement.code_saison == code_saison_annuel,
                Paiement.code_saison == code_saison_ete
            )
        )
    
    return query

def filter_seances_by_saison(query=None):
    """
    Filtre les séances par la saison en cours
    
    Args:
        query: Query SQLAlchemy existante (optionnel)
    
    Returns:
        Query filtrée par date (saison commence le 1er octobre)
    """
    year = get_current_saison()
    if query is None:
        query = Seance.query
    
    if year:
        # Saison commence le 1er octobre de year-1 et se termine le 31 août de year
        date_debut = date(year - 1, 10, 1)
        date_fin = date(year, 8, 31)
        
        query = query.filter(
            and_(
                Seance.date >= date_debut,
                Seance.date <= date_fin
            )
        )
    
    return query

def filter_autres_paiements_by_saison(query=None):
    """
    Filtre les autres paiements par la saison en cours
    
    Args:
        query: Query SQLAlchemy existante (optionnel)
    
    Returns:
        Query filtrée par code_saison
    """
    year = get_current_saison()
    if query is None:
        query = AutresPaiements.query
    
    if year:
        code_saison_annuel = f"S{year}"
        code_saison_ete = f"E{year}"
        
        query = query.filter(
            or_(
                AutresPaiements.code_saison == code_saison_annuel,
                AutresPaiements.code_saison == code_saison_ete
            )
        )
    
    return query

def get_saison_date_range():
    """
    Retourne la plage de dates pour la saison actuelle
    
    Returns:
        tuple: (date_debut, date_fin) ou (None, None) si pas de saison
    """
    year = get_current_saison()
    if year:
        date_debut = date(year - 1, 10, 1)  # 1er octobre année précédente
        date_fin = date(year, 8, 31)        # 31 août année actuelle
        return (date_debut, date_fin)
    return (None, None)

def get_saison_label():
    """
    Retourne le label de la saison actuelle
    
    Returns:
        str: "2024/2025" ou None si pas de saison
    """
    year = get_current_saison()
    if year:
        return f"{year - 1}/{year}"
    return None


# EXEMPLES D'UTILISATION DANS VOS ROUTES:

# Exemple 1: Route simple avec filtrage
@app.route('/exemple_adherents')
@require_saison  # S'assure qu'une saison est sélectionnée
def exemple_adherents():
    # Récupérer tous les adhérents de la saison
    adherents = filter_adherents_by_saison().all()
    
    # Récupérer le label de la saison pour l'affichage
    saison_label = get_saison_label()
    
    return render_template('exemple.html', 
                         adherents=adherents,
                         saison=saison_label)


# Exemple 2: Route avec query personnalisée
@app.route('/exemple_paiements')
@require_saison
def exemple_paiements():
    # Créer une query personnalisée
    query = Paiement.query.filter(Paiement.montant_paye > 0)
    
    # Appliquer le filtre de saison
    paiements = filter_paiements_by_saison(query).all()
    
    return render_template('paiements.html', paiements=paiements)


# Exemple 3: Route avec statistiques
@app.route('/exemple_stats')
@require_saison
def exemple_stats():
    # Statistiques pour la saison en cours
    total_adherents = filter_adherents_by_saison().count()
    
    total_paiements = db.session.query(
        func.sum(Paiement.montant_paye)
    ).select_from(
        filter_paiements_by_saison()
    ).scalar() or 0
    
    # Récupérer la plage de dates
    date_debut, date_fin = get_saison_date_range()
    
    return render_template('stats.html',
                         total_adherents=total_adherents,
                         total_paiements=total_paiements,
                         date_debut=date_debut,
                         date_fin=date_fin)


# Exemple 4: API avec filtrage
@app.route('/api/adherents_saison')
@require_saison
def api_adherents_saison():
    adherents = filter_adherents_by_saison().all()
    
    return jsonify({
        'saison': get_saison_label(),
        'count': len(adherents),
        'adherents': [a.to_dict() for a in adherents]
    })


# Home page
@app.route('/')
def home():
    return render_template('signin.html')
@app.route('/page')
def page():
    return render_template('landing_page1.html')




@app.route('/presentation')
def presentation():
    return render_template('presentation.html')


@app.route('/api/current-season')
def get_current_season():
    """Get current season information from session"""
    if 'saison_code' not in session:
        # Calculate default season based on current date
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # If we're in October or later, use next year
        year = current_year + 1 if current_month >= 10 else current_year
        # If we're in July-September, use E, otherwise S
        season_type = 'E' if 7 <= current_month <= 9 else 'S'
        season_code = f"{season_type}{year}"
        
        return jsonify({
            'success': True,
            'saison_code': season_code,
            'saison_type': season_type,
            'saison_year': year
        })
    
    return jsonify({
        'success': True,
        'saison_code': session.get('saison_code'),
        'saison_type': session.get('saison_type'),
        'saison_year': session.get('saison')
    })

@app.route('/admin')
@season_required
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    # Create season context for both Paiement and Adherent
    payment_season = SeasonContext(Paiement)
    adherent_season = SeasonContext(Adherent)
    
    # Get current season code from session
    current_season_code = session.get('saison_code')
    if not current_season_code:
        flash("Veuillez sélectionner une saison.", "warning")
        return redirect(url_for('login'))
    
    # Apply season filters using session's season code
    paiements = payment_season.filter_query(
        Paiement.query.filter(Paiement.code_saison == current_season_code)
    ).all()
    
    adherents = adherent_season.filter_query(
        Adherent.query.filter(Adherent.code_saison == current_season_code)
    ).all()
    
    # Calculate statistics
    total_collecte = sum(float(p.montant_paye or 0) for p in paiements)
    total_reste = sum(float(p.montant_reste or 0) for p in paiements)
    
    paiements_count = len(paiements)
    moyenne_paiement = total_collecte / paiements_count if paiements_count > 0 else 0
    
    # Get recent payments for current season
    paiements_recent = payment_season.filter_query(
        Paiement.query.filter(Paiement.code_saison == current_season_code)
        .order_by(Paiement.date_paiement.desc())
    ).limit(5).all()

    return render_template('admin.html',
        total_collecte=float(total_collecte),
        total_reste=float(total_reste),
        moyenne_paiement=float(moyenne_paiement),
        paiements_count=int(paiements_count),
        paiements_recent=paiements_recent,
        saison_code=current_season_code,
        saison_type=session.get('saison_type'),
        saison_year=session.get('saison'))



@app.route('/api/adherents-data')
def get_adherents_data():
    try:
        season_code = request.args.get('saison') or session.get('saison_code')
        if not season_code:
            return jsonify({
                'success': False,
                'error': 'No season selected'
            }), 400

        # Create season context
        season = SeasonContext(Adherent)
        
        all_adherents = season.filter_query(
            Adherent.query.filter(Adherent.code_saison == season_code)
        ).all()

        adherents_list = []
        types_abonnement = set()
        groupes = set()

        for a in all_adherents:
            adherent_data = {
                'id': a.adherent_id,
                'matricule': a.matricule,
                'nom': a.nom,
                'prenom': a.prenom,
                'type_abonnement': a.type_abonnement or 'N/D',
                'groupe': a.groupe or 'Non spécifié',
                'paye': a.paye
            }
            adherents_list.append(adherent_data)
            
            if a.type_abonnement:
                types_abonnement.add(a.type_abonnement)
            if a.groupe:
                groupes.add(a.groupe)

        return jsonify({
            'success': True,
            'adherents': adherents_list,
            'types_abonnement': sorted(list(types_abonnement)),
            'groupes': sorted(list(groupes)),
            'saison_code': season_code,
            'total': len(adherents_list)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/paiements-indicators')
@season_required
def get_paiements_indicators():
    try:
        current_season_code = session.get('saison_code')
        if not current_season_code:
            return jsonify({'error': 'Aucune saison sélectionnée'}), 400

        types_filter = request.args.getlist('types[]')
        groupes_filter = request.args.getlist('groupes[]')

        # Base query with season filter
        base_query = db.session.query(
            Paiement, Adherent.nom, Adherent.prenom, Adherent.type_abonnement,
            Adherent.groupe, Adherent.paye
        ).join(
            Adherent, 
            Paiement.matricule_adherent == Adherent.matricule
        ).filter(Paiement.code_saison == current_season_code)

        if types_filter:
            base_query = base_query.filter(Adherent.type_abonnement.in_(types_filter))
        if groupes_filter:
            base_query = base_query.filter(Adherent.groupe.in_(groupes_filter))

        paiements_data = base_query.all()

        paiements_list = []
        statistics = {'complets': 0, 'partiels': 0, 'impayes': 0, 'montant_total': 0}
        reglement_stats = {}
        type_abonnement_payment_stats = {}
        type_abonnement_montants = {}

        for paiement, nom, prenom, type_abonnement, groupe, adherent_paye in paiements_data:
            type_abonnement = type_abonnement or 'Non spécifié'
            groupe = groupe or 'Non spécifié'
            
            montant_reste = float(paiement.montant_reste or 0)
            montant_paye = float(paiement.montant_paye or 0)
            montant_total = float(paiement.montant or 0)

            # Determine payment status
            if montant_reste <= 0 and montant_paye >= montant_total:
                status_paiement = 'complet'
                statistics['complets'] += 1
            elif montant_paye > 0:
                status_paiement = 'partiel'
                statistics['partiels'] += 1
            else:
                status_paiement = 'impaye'
                statistics['impayes'] += 1

            statistics['montant_total'] += montant_paye

            # Update payment type stats
            type_reglement = paiement.type_reglement or 'Non spécifié'
            reglement_stats[type_reglement] = reglement_stats.get(type_reglement, 0) + 1

            # CORRECTION: Initialiser les stats avec les bonnes clés (singulier)
            if type_abonnement not in type_abonnement_payment_stats:
                type_abonnement_payment_stats[type_abonnement] = {'complet': 0, 'partiel': 0, 'impaye': 0}
                type_abonnement_montants[type_abonnement] = {'complet': 0, 'partiel': 0, 'impaye': 0}

            # CORRECTION: Utiliser les mêmes clés que dans l'initialisation
            type_abonnement_payment_stats[type_abonnement][status_paiement] += 1

            # Update amounts by subscription type and status
            if status_paiement == 'complet':
                type_abonnement_montants[type_abonnement]['complet'] += montant_paye
            elif status_paiement == 'partiel':
                type_abonnement_montants[type_abonnement]['partiel'] += montant_paye
            else:  # impaye
                type_abonnement_montants[type_abonnement]['impaye'] += montant_total

            paiements_list.append({
                'id_paiement': paiement.id_paiement,
                'matricule_adherent': paiement.matricule_adherent,
                'nom_adherent': f"{nom} {prenom}".strip(),
                'date_paiement': paiement.date_paiement.isoformat() if paiement.date_paiement else None,
                'montant': montant_total,
                'montant_paye': montant_paye,
                'montant_reste': montant_reste,
                'type_reglement': type_reglement,
                'type_abonnement': type_abonnement,
                'groupe': groupe,
                'status_paiement': status_paiement,
                'adherent_paye_status': adherent_paye
            })

        # Get recent payments
        paiements_recents = sorted(
            [p for p in paiements_list if p['date_paiement']],
            key=lambda x: x['date_paiement'], 
            reverse=True
        )[:10]

        return jsonify({
            'success': True,
            'paiements': paiements_list,
            'statistics': statistics,
            'reglement_stats': reglement_stats,
            'type_abonnement_payment_stats': type_abonnement_payment_stats,
            'type_abonnement_montants': type_abonnement_montants,
            'paiements_recents': paiements_recents,
            'saison_code': current_season_code
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    try:
        current_season_code = session.get('saison_code')
        if not current_season_code:
            return jsonify({'error': 'Aucune saison sélectionnée'}), 400

        types_filter = request.args.getlist('types[]')
        groupes_filter = request.args.getlist('groupes[]')

        # Base query with season filter
        base_query = db.session.query(
            Paiement, Adherent.nom, Adherent.prenom, Adherent.type_abonnement,
            Adherent.groupe, Adherent.paye
        ).join(
            Adherent, 
            Paiement.matricule_adherent == Adherent.matricule
        ).filter(Paiement.code_saison == current_season_code)

        if types_filter:
            base_query = base_query.filter(Adherent.type_abonnement.in_(types_filter))
        if groupes_filter:
            base_query = base_query.filter(Adherent.groupe.in_(groupes_filter))

        paiements_data = base_query.all()

        paiements_list = []
        statistics = {'complets': 0, 'partiels': 0, 'impayes': 0, 'montant_total': 0}
        reglement_stats = {}
        type_abonnement_payment_stats = {}
        type_abonnement_montants = {}

        for paiement, nom, prenom, type_abonnement, groupe, adherent_paye in paiements_data:
            type_abonnement = type_abonnement or 'Non spécifié'
            groupe = groupe or 'Non spécifié'
            
            montant_reste = float(paiement.montant_reste or 0)
            montant_paye = float(paiement.montant_paye or 0)
            montant_total = float(paiement.montant or 0)

            # Determine payment status
            if montant_reste <= 0 and montant_paye >= montant_total:
                status_paiement = 'complet'
                statistics['complets'] += 1
            elif montant_paye > 0:
                status_paiement = 'partiel'
                statistics['partiels'] += 1
            else:
                status_paiement = 'impaye'
                statistics['impayes'] += 1

            statistics['montant_total'] += montant_paye

            # Update payment type stats
            type_reglement = paiement.type_reglement or 'Non spécifié'
            reglement_stats[type_reglement] = reglement_stats.get(type_reglement, 0) + 1

            # Update subscription type stats
            if type_abonnement not in type_abonnement_payment_stats:
                type_abonnement_payment_stats[type_abonnement] = {'complets': 0, 'partiels': 0, 'impayes': 0}
                type_abonnement_montants[type_abonnement] = {'complets': 0, 'partiels': 0, 'impayes': 0}

            type_abonnement_payment_stats[type_abonnement][status_paiement] += 1

            # Update amounts by subscription type and status
            if status_paiement == 'complet':
                type_abonnement_montants[type_abonnement]['complets'] += montant_paye
            elif status_paiement == 'partiel':
                type_abonnement_montants[type_abonnement]['partiels'] += montant_paye
            else:  # impaye
                type_abonnement_montants[type_abonnement]['impayes'] += montant_total

            paiements_list.append({
                'id_paiement': paiement.id_paiement,
                'matricule_adherent': paiement.matricule_adherent,
                'nom_adherent': f"{nom} {prenom}".strip(),
                'date_paiement': paiement.date_paiement.isoformat() if paiement.date_paiement else None,
                'montant': montant_total,
                'montant_paye': montant_paye,
                'montant_reste': montant_reste,
                'type_reglement': type_reglement,
                'type_abonnement': type_abonnement,
                'groupe': groupe,
                'status_paiement': status_paiement,
                'adherent_paye_status': adherent_paye
            })

        # Get recent payments
        paiements_recents = sorted(
            [p for p in paiements_list if p['date_paiement']],
            key=lambda x: x['date_paiement'], 
            reverse=True
        )[:10]

        return jsonify({
            'success': True,
            'paiements': paiements_list,
            'statistics': statistics,
            'reglement_stats': reglement_stats,
            'type_abonnement_payment_stats': type_abonnement_payment_stats,
            'type_abonnement_montants': type_abonnement_montants,
            'paiements_recents': paiements_recents,
            'saison_code': current_season_code
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/financial-indicators')
@season_required
def get_financial_indicators():
    try:
        current_season_code = session.get('saison_code')
        if not current_season_code:
            return jsonify({'error': 'Aucune saison sélectionnée'}), 400

        types_filter = request.args.getlist('types[]')
        groupes_filter = request.args.getlist('groupes[]')

        # Base query with season filter
        base_query = Paiement.query.filter(Paiement.code_saison == current_season_code)

        # If filters are applied, join with Adherent table
        if types_filter or groupes_filter:
            base_query = base_query.join(Adherent, Paiement.matricule_adherent == Adherent.matricule)
            if types_filter:
                base_query = base_query.filter(Adherent.type_abonnement.in_(types_filter))
            if groupes_filter:
                base_query = base_query.filter(Adherent.groupe.in_(groupes_filter))

        paiements = base_query.all()

        total_collecte = sum(float(p.montant_paye or 0) for p in paiements)
        total_reste = sum(float(p.montant_reste or 0) for p in paiements)

        return jsonify({
            'success': True, 
            'total_collecte': total_collecte, 
            'total_reste': total_reste,
            'saison_code': current_season_code,
            'saison_type': session.get('saison_type'),
            'saison_year': session.get('saison')
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
from sqlalchemy import func, or_

# Route pour l'emploi du temps de préparation physique
@app.route('/emploi_prep_physique', methods=['GET'])
def emploi_prep_physique():
    if 'user_id' not in session or session.get('role') != 'entraineur':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    username = session.get('username')
    if not username:
        flash("Session invalide.", "danger")
        return redirect(url_for('login'))
    
    try:
        nom, prenom = username.split('.')
    except ValueError:
        flash("Format du nom d'utilisateur invalide.", "danger")
        return redirect(url_for('login'))
    
    entraineur = Entraineur.query.filter_by(nom=nom, prenom=prenom).first()
    if not entraineur:
        flash("Entraîneur introuvable.", "danger")
        return redirect(url_for('login'))
    
    nom_complet_entraineur = f"{nom} {prenom}"
    
    # Gestion de la navigation par semaine
    week_offset = request.args.get('week_offset', 0, type=int)
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)
    
    # Récupérer TOUTES les séances de préparation physique pour la semaine courante
    seances_prep = Seance.query.filter(
        Seance.date >= start_of_week.date(),
        Seance.date <= end_of_week.date(),
        Seance.type_seance == 'prep_physique'
    ).all()
    
    # Création des jours de la semaine
    jours_semaine = []
    jours_noms = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    for i in range(7):
        jour_date = start_of_week + timedelta(days=i)
        jours_semaine.append({
            'nom': jours_noms[i],
            'date': jour_date,
            'date_str': jour_date.strftime('%Y-%m-%d')
        })
    
    # Création des créneaux horaires (de 8h à 22h par heure)
    creneaux_horaires = []
    for heure in range(8, 22):  # De 8h à 21h (22h non inclus)
        creneaux_horaires.append({
            'start': time(heure, 0),
            'end': time(heure + 1, 0)
        })
    
    # Préparer une structure de données pour faciliter l'accès aux séances
    seances_par_jour_et_heure = {}
    for seance in seances_prep:
        date_str = seance.date.strftime('%Y-%m-%d')
        heure_debut = seance.heure_debut.strftime('%H:%M')
        key = f"{date_str}_{heure_debut}"
        
        seance_info = {
            'seance_id': seance.seance_id,
            'date': seance.date,
            'heure_debut': seance.heure_debut,
            'heure_fin': seance.heure_fin,
            'groupe': seance.groupe,
            'entraineur': seance.entraineur,
            'type_seance': seance.type_seance,
            'adherents_matricules': seance.adherents_matricules
        }
        seances_par_jour_et_heure[key] = seance_info
    
    return render_template(
        'emploi_prep_physique.html',
        start_of_week=start_of_week,
        end_of_week=end_of_week,
        week_offset=week_offset,
        entraineur=entraineur,
        jours_semaine=jours_semaine,
        creneaux_horaires=creneaux_horaires,
        seances_par_jour_et_heure=seances_par_jour_et_heure,
        nom_complet_entraineur=nom_complet_entraineur,
        type_seance_global='prep_physique'  # ← AJOUT: Envoyer le type global
    )


from flask import flash, redirect, render_template, request, session, url_for
from datetime import datetime, timedelta, time

@app.route('/entraineur', methods=['GET', 'POST'])
def entraineur():
    # Vérification des permissions
    if 'user_id' not in session or session.get('role') != 'entraineur':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    username = session.get('username')
    if not username:
        flash("Session invalide.", "danger")
        return redirect(url_for('login'))
    
    try:
        nom, prenom = username.split('.')
    except ValueError:
        flash("Format du nom d'utilisateur invalide.", "danger")
        return redirect(url_for('login'))
    
    # Normaliser le nom et prénom pour la requête
    nom = nom.strip()
    prenom = prenom.strip()

    entraineur = Entraineur.query.filter_by(nom=nom, prenom=prenom).first()
    if not entraineur:
        flash("Entraîneur introuvable.", "danger")
        return redirect(url_for('login'))
    
    # Construire le nom complet normalisé
    nom_complet_entraineur = f"{nom} {prenom}".replace('\u00A0', ' ').strip()

    # Debug pour vérifier le nom complet envoyé au template

    # Gestion de la navigation
    week_offset = request.args.get('week_offset', 0, type=int)
    day_offset = request.args.get('day_offset', 0, type=int)
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    day_offset = max(0, min(6, day_offset))
    current_day = start_of_week + timedelta(days=day_offset)

    # Récupérer toutes les séances du jour
    seances_tous = Seance.query.filter(Seance.date == current_day.date()).all()

    # Préparer la structure pour le template
    seances_par_terrain_et_heure = {}
    for seance in seances_tous:
        terrain = seance.terrain
        heure_debut = seance.heure_debut.strftime('%H:%M')
        key = f"{terrain}_{heure_debut}"

        # Normalisation et debug de chaque entraîneur enregistré
        entraineur_seance_norm = seance.entraineur.replace('\u00A0', ' ').strip()

        seances_par_terrain_et_heure[key] = {
            'id': seance.seance_id,
            'date': seance.date,
            'heure_debut': seance.heure_debut,
            'heure_fin': seance.heure_fin,
            'groupe': seance.groupe,
            'entraineur': entraineur_seance_norm,
            'terrain': seance.terrain,
            'type_seance': seance.type_seance or 'entrainement',
            'adherents_matricules': seance.adherents_matricules
        }

    # Créneaux horaires
    creneaux = [
        {'start': time(8, 0), 'end': time(9, 30)},
        {'start': time(9, 30), 'end': time(11, 0)},
        {'start': time(11, 0), 'end': time(12, 30)},
        {'start': time(12, 30), 'end': time(14, 0)},
        {'start': time(14, 0), 'end': time(15, 30)},
        {'start': time(15, 30), 'end': time(17, 0)},
        {'start': time(17, 0), 'end': time(18, 30)},
        {'start': time(18, 30), 'end': time(20, 0)},
    ]

    return render_template(
        'entraineur.html',
        current_day=current_day,
        week_offset=week_offset,
        day_offset=day_offset,
        entraineur=entraineur,
        seances_par_terrain_et_heure=seances_par_terrain_et_heure,
        creneaux=creneaux,
        nom_complet_entraineur=nom_complet_entraineur,
        type_seance_global='entrainement'
    )


# Route pour sauvegarder les présences
@app.route('/api/save_presences', methods=['POST'])
def save_presences():
    if 'user_id' not in session:
        return jsonify({"error": "Non autorisé"}), 403
    
    try:
        data = request.get_json()
        groupe = data.get('groupe')
        date_str = data.get('date')
        heure_str = data.get('heure')
        seance_type = data.get('seance_type', 'entrainement')  # Récupérer le type
        presences_data = data.get('presences', {})
        
        
        # Convertir la date et l'heure
        date_seance = datetime.strptime(date_str, '%Y-%m-%d').date()
        heure_debut = datetime.strptime(heure_str, '%H:%M').time()
        
        # Récupérer l'entraîneur
        username = session.get('username')
        nom, prenom = username.split('.')
        entraineur_nom = f"{nom} {prenom}"
        
        # Récupérer la séance avec le type
        seance = Seance.query.filter_by(
            date=date_seance,
            heure_debut=heure_debut,
            groupe=groupe,
            entraineur=entraineur_nom,
            type_seance=seance_type  # Ajout du filtre par type
        ).first()
        
        if not seance:
            # Si pas trouvé, essayer sans le type (pour compatibilité)
            seance = Seance.query.filter_by(
                date=date_seance,
                heure_debut=heure_debut,
                groupe=groupe,
                entraineur=entraineur_nom
            ).first()
            
            if not seance:
                return jsonify({"error": "Séance non trouvée"}), 404
            
        
        # 1. SAUVEGARDER LA PRÉSENCE DE L'ENTRAÎNEUR
        trainer_presence = presences_data.get('trainer_presence')
        if trainer_presence is not None:
            presence_entraineur_existante = PresenceEntraineur.query.filter_by(
                entraineur_nom=entraineur_nom,
                seance_id=seance.seance_id,
                date_seance=date_seance,
                heure_debut=heure_debut
            ).first()
            
            if presence_entraineur_existante:
                presence_entraineur_existante.est_present = trainer_presence
            else:
                nouvelle_presence_entraineur = PresenceEntraineur(
                    entraineur_nom=entraineur_nom,
                    seance_id=seance.seance_id,
                    date_seance=date_seance,
                    heure_debut=heure_debut,
                    est_present=trainer_presence,
                    commentaire=seance_type
                )
                db.session.add(nouvelle_presence_entraineur)
        
        # 2. SAUVEGARDER LES PRÉSENCES DES ADHÉRENTS (format matricules séparés par virgules)
        adherents_data = presences_data.get('adherents', [])
        
        # Préparer les listes de matricules par statut de présence
        matricules_presents = []
        matricules_absents = []
        
        for adherent_data in adherents_data:
            matricule = adherent_data.get('matricule')
            presence = adherent_data.get('presence')
            
            if presence == 'O':
                matricules_presents.append(str(matricule))
            else:
                matricules_absents.append(str(matricule))
        
       
        
        # Sauvegarder les présents (une seule entrée avec tous les matricules)
        if matricules_presents:
            matricules_presents_str = ','.join(matricules_presents)
            
            presence_existante_present = Presence.query.filter_by(
                groupe_nom=groupe,
                entraineur_nom=entraineur_nom,
                date_seance=date_seance,
                heure_debut=heure_debut,
                seance_id=seance.seance_id,
                est_present='O'
            ).first()
            
            if presence_existante_present:
                presence_existante_present.adherent_matricule = matricules_presents_str
            else:
                nouvelle_presence_present = Presence(
                    groupe_nom=groupe,
                    adherent_matricule=matricules_presents_str,
                    entraineur_nom=entraineur_nom,
                    date_seance=date_seance,
                    heure_debut=heure_debut,
                    est_present='O',
                    seance_id=seance.seance_id,
                    seance_type=seance_type
                )
                db.session.add(nouvelle_presence_present)
        
        # Sauvegarder les absents (une seule entrée avec tous les matricules)
        if matricules_absents:
            matricules_absents_str = ','.join(matricules_absents)
            
            presence_existante_absent = Presence.query.filter_by(
                groupe_nom=groupe,
                entraineur_nom=entraineur_nom,
                date_seance=date_seance,
                heure_debut=heure_debut,
                seance_id=seance.seance_id,
                est_present='N'
            ).first()
            
            if presence_existante_absent:
                presence_existante_absent.adherent_matricule = matricules_absents_str
            else:
                nouvelle_presence_absent = Presence(
                    groupe_nom=groupe,
                    adherent_matricule=matricules_absents_str,
                    entraineur_nom=entraineur_nom,
                    date_seance=date_seance,
                    heure_debut=heure_debut,
                    est_present='N',
                    seance_id=seance.seance_id,
                    seance_type=seance_type
                )
                db.session.add(nouvelle_presence_absent)
        
        # Supprimer les entrées si aucun présent/absent
        if not matricules_presents:
            Presence.query.filter_by(
                groupe_nom=groupe,
                entraineur_nom=entraineur_nom,
                date_seance=date_seance,
                heure_debut=heure_debut,
                seance_id=seance.seance_id,
                est_present='O'
            ).delete()
        
        if not matricules_absents:
            Presence.query.filter_by(
                groupe_nom=groupe,
                entraineur_nom=entraineur_nom,
                date_seance=date_seance,
                heure_debut=heure_debut,
                seance_id=seance.seance_id,
                est_present='N'
            ).delete()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Présences enregistrées - {len(matricules_presents)} présents, {len(matricules_absents)} absents"
        })
    
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_adherents_groupe/<string:nom_groupe>', methods=['GET'])
def get_adherents_groupe(nom_groupe):
    if 'user_id' not in session:
        return jsonify({"error": "Non autorisé"}), 403
    
    try:
        # Récupérer le code saison de la session
        current_season_code = session.get('saison_code')
        if not current_season_code:
            return jsonify({"error": "Aucune saison sélectionnée"}), 400
        
        print(f"Recherche groupe: '{nom_groupe}' pour la saison: {current_season_code}")
        
        # Essayer de chercher par ID d'abord
        try:
            groupe_id = int(nom_groupe)
            groupe = Groupe.query.get(groupe_id)
            if groupe:
                nom_groupe = groupe.nom_groupe
                print(f"Groupe trouvé par ID: {nom_groupe}")
        except ValueError:
            pass
        
        # Chercher les adhérents avec filtre de saison ET statut actif
        adherents = Adherent.query.filter_by(
            groupe=nom_groupe,
            code_saison=current_season_code,
            status='Actif'
        ).order_by(Adherent.nom, Adherent.prenom).all()
        
        print(f"Adhérents trouvés: {len(adherents)} pour la saison {current_season_code}")
        
        for a in adherents:
            print(f"  - {a.matricule}: {a.nom} {a.prenom} (Saison: {a.code_saison})")
        
        adherents_list = [{
            'matricule': a.matricule,
            'nom': a.nom,
            'prenom': a.prenom,
            'groupe': a.groupe,
            'code_saison': a.code_saison
        } for a in adherents]
        
        return jsonify({
            "success": True,
            "adherents": adherents_list,
            "groupe_recherche": nom_groupe,
            "saison_code": current_season_code
        })
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400


# Route pour récupérer les statistiques des présences par type de séance
@app.route('/api/stats_presences', methods=['GET'])
def get_stats_presences():
    if 'user_id' not in session:
        return jsonify({"error": "Non autorisé"}), 403
    
    try:
        username = session.get('username')
        nom, prenom = username.split('.')
        entraineur_nom = f"{nom} {prenom}"
        
        # Récupérer les statistiques des présences par type de séance
        stats_query = db.session.query(
            Seance.type_seance,
            func.count(Presence.id_presence).label('total_presences'),
            func.count(distinct(Presence.adherent_matricule)).label('adherents_uniques'),
            func.sum(case([(Presence.est_present == 'O', 1)], else_=0)).label('presents'),
            func.sum(case([(Presence.est_present == 'N', 1)], else_=0)).label('absents')
        ).join(
            Seance, Presence.seance_id == Seance.seance_id
        ).filter(
            Seance.entraineur == entraineur_nom
        ).group_by(
            Seance.type_seance
        ).all()
        
        stats_list = []
        for stat in stats_query:
            stats_list.append({
                'type_seance': stat.type_seance,
                'total_presences': stat.total_presences,
                'adherents_uniques': stat.adherents_uniques,
                'presents': stat.presents or 0,
                'absents': stat.absents or 0,
                'taux_presence': round((stat.presents or 0) / max(stat.total_presences, 1) * 100, 2)
            })
        
        return jsonify({
            "success": True,
            "stats": stats_list
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route pour récupérer l'emploi du temps d'une semaine complète
@app.route('/api/emploi_temps_semaine', methods=['GET'])
def get_emploi_temps_semaine():
    if 'user_id' not in session:
        return jsonify({"error": "Non autorisé"}), 403
    
    try:
        username = session.get('username')
        nom, prenom = username.split('.')
        entraineur_nom = f"{nom} {prenom}"
        
        # Paramètres de la semaine
        week_offset = request.args.get('week_offset', 0, type=int)
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        end_of_week = start_of_week + timedelta(days=6)
        
        # Récupérer toutes les séances de la semaine
        seances_semaine = Seance.query.filter(
            Seance.date >= start_of_week.date(),
            Seance.date <= end_of_week.date()
        ).all()
        
        # Organiser par jour et type
        planning_semaine = {}
        for i in range(7):  # 7 jours de la semaine
            jour = start_of_week + timedelta(days=i)
            jour_str = jour.strftime('%Y-%m-%d')
            planning_semaine[jour_str] = {
                'date': jour_str,
                'jour_nom': jour.strftime('%A'),
                'seances': []
            }
        
        # Ajouter les séances
        for seance in seances_semaine:
            jour_str = seance.date.strftime('%Y-%m-%d')
            if jour_str in planning_semaine:
                seance_info = {
                    'id': seance.seance_id,
                    'heure_debut': seance.heure_debut.strftime('%H:%M'),
                    'heure_fin': seance.heure_fin.strftime('%H:%M'),
                    'groupe': seance.groupe,
                    'entraineur': seance.entraineur,
                    'terrain': seance.terrain,
                    'type_seance': seance.type_seance or 'entrainement',
                    'est_ma_seance': seance.entraineur.lower() == entraineur_nom.lower()
                }
                planning_semaine[jour_str]['seances'].append(seance_info)
        
        # Trier les séances par heure pour chaque jour
        for jour_data in planning_semaine.values():
            jour_data['seances'].sort(key=lambda x: x['heure_debut'])
        
        return jsonify({
            "success": True,
            "planning": planning_semaine,
            "semaine_debut": start_of_week.strftime('%Y-%m-%d'),
            "semaine_fin": end_of_week.strftime('%Y-%m-%d')
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Modèle pour les présences des entraîneurs (optionnel)
class PresenceEntraineur(db.Model):
    __tablename__ = 'presence_entraineurs'
    
    id_presence = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entraineur_nom = db.Column(db.String(100), nullable=False)
    seance_id = db.Column(db.Integer, db.ForeignKey('seances.seance_id'), nullable=False)
    date_seance = db.Column(db.Date, nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    est_present = db.Column(db.Enum('O', 'N'), nullable=False, default='N')
    commentaire = db.Column(db.Text, nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PresenceEntraineur {self.entraineur_nom} - {self.date_seance}>'

# Ajouter ces méthodes au modèle Presence
class Presence(db.Model):
    __tablename__ = 'presence'
    
    id_presence = db.Column(db.Integer, primary_key=True, autoincrement=True)
    groupe_nom = db.Column(db.String(100), nullable=False)
    adherent_matricule = db.Column(db.Text, nullable=False)  # Stocke "1,12,15"
    entraineur_nom = db.Column(db.String(100), nullable=False)
    date_seance = db.Column(db.Date, nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    est_present = db.Column(db.Enum('O', 'N'), nullable=False, default='N')
    seance_id = db.Column(db.Integer, db.ForeignKey('seances.seance_id'), nullable=False)
    seance_type = db.Column(db.Enum('entrainement', 'prep_physique'), nullable=False, default='entrainement')
    
    def get_matricules_list(self):
        """Convertit la chaîne de matricules en liste Python"""
        if self.adherent_matricule:
            return [m.strip() for m in self.adherent_matricule.split(',') if m.strip()]
        return []
    
    def set_matricules_list(self, matricules_list):
        """Convertit une liste Python en chaîne séparée par des virgules"""
        self.adherent_matricule = ','.join([str(m).strip() for m in matricules_list if str(m).strip()])
    
    def count_matricules(self):
        """Retourne le nombre de matricules"""
        return len(self.get_matricules_list())
    
    def contains_matricule(self, matricule):
        """Vérifie si un matricule est présent"""
        return str(matricule) in self.get_matricules_list()


@app.route('/locations_terrains', methods=['GET', 'POST'])
def locations_terrains():
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    search_query = request.args.get('search', '')
    locations = LocationTerrain.query.filter(
        LocationTerrain.locateur.ilike(f"%{search_query}%")
    ).all()

    if request.method == 'POST':
        try:
            numero_terrain = int(request.form['numero_terrain'])
            date_loc = datetime.strptime(request.form['date_location'], '%Y-%m-%d').date()
            heure_debut = datetime.strptime(request.form['heure_debut'], '%H:%M').time()
            heure_fin = datetime.strptime(request.form['heure_fin'], '%H:%M').time()
            locateur = request.form['locateur']
            montant = float(request.form['montant'])

            # Validation des heures
            if heure_debut < time(8,0) or heure_fin > time(20,0):
                return redirect(url_for('locations_terrains'))

            if heure_debut >= heure_fin:
                return redirect(url_for('locations_terrains'))

            # Vérification des conflits avec les séances
            conflit_seances = Seance.query.filter(
                Seance.terrain == numero_terrain,
                Seance.date == date_loc,
                or_(
                    and_(Seance.heure_debut <= heure_debut, Seance.heure_fin > heure_debut),
                    and_(Seance.heure_debut < heure_fin, Seance.heure_fin >= heure_fin)
                )
            ).first()

            # Vérification des conflits avec les autres locations
            conflit_locations = LocationTerrain.query.filter(
                LocationTerrain.numero_terrain == numero_terrain,
                LocationTerrain.date_location == date_loc,
                or_(
                    and_(LocationTerrain.heure_debut <= heure_debut, LocationTerrain.heure_fin > heure_debut),
                    and_(LocationTerrain.heure_debut < heure_fin, LocationTerrain.heure_fin >= heure_fin)
                )
            ).first()

            if conflit_seances or conflit_locations:
                return redirect(url_for('locations_terrains'))

            nouvelle_location = LocationTerrain(
                numero_terrain=numero_terrain,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                date_location=date_loc,
                locateur=locateur,
                montant_location=montant
            )

            db.session.add(nouvelle_location)
            db.session.commit()

        except Exception as e:
            db.session.rollback()

        return redirect(url_for('locations_terrains'))

    return render_template('locations_terrains.html', locations=locations)

@app.route('/editer_location/<int:id>', methods=['POST'])
def editer_location(id):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    location = LocationTerrain.query.get_or_404(id)
    
    try:
        ancien_terrain = location.numero_terrain
        ancienne_date = location.date_location
        ancien_debut = location.heure_debut
        ancien_fin = location.heure_fin
        
        location.numero_terrain = int(request.form['numero_terrain'])
        location.date_location = datetime.strptime(request.form['date_location'], '%Y-%m-%d').date()
        location.heure_debut = datetime.strptime(request.form['heure_debut'], '%H:%M').time()
        location.heure_fin = datetime.strptime(request.form['heure_fin'], '%H:%M').time()
        location.locateur = request.form['locateur']
        location.montant_location = float(request.form['montant'])

        # Validation des heures
        if location.heure_debut < time(8,0) or location.heure_fin > time(20,0):
            flash("Les heures doivent être entre 08:00 et 20:00", "danger")
            return redirect(url_for('locations_terrains'))

        if location.heure_debut >= location.heure_fin:
            flash("L'heure de fin doit être après l'heure de début", "danger")
            return redirect(url_for('locations_terrains'))

        # Vérification des conflits
        if (ancien_terrain != location.numero_terrain or 
            ancienne_date != location.date_location or 
            ancien_debut != location.heure_debut or 
            ancien_fin != location.heure_fin):
            
            conflit_seances = Seance.query.filter(
                Seance.terrain == location.numero_terrain,
                Seance.date == location.date_location,
                or_(
                    and_(Seance.heure_debut <= location.heure_debut, Seance.heure_fin > location.heure_debut),
                    and_(Seance.heure_debut < location.heure_fin, Seance.heure_fin >= location.heure_fin)
                )
            ).first()

            conflit_locations = LocationTerrain.query.filter(
                LocationTerrain.id_location != id,
                LocationTerrain.numero_terrain == location.numero_terrain,
                LocationTerrain.date_location == location.date_location,
                or_(
                    and_(LocationTerrain.heure_debut <= location.heure_debut, LocationTerrain.heure_fin > location.heure_debut),
                    and_(LocationTerrain.heure_debut < location.heure_fin, LocationTerrain.heure_fin >= location.heure_fin)
                )
            ).first()

            if conflit_seances or conflit_locations:
                flash("Conflit de réservation pour ce créneau", "danger")
                return redirect(url_for('locations_terrains'))

        db.session.commit()
        flash("Réservation mise à jour avec succès", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la mise à jour : {str(e)}", "danger")

    return redirect(url_for('locations_terrains'))


@app.route('/supprimer_location/<int:id>', methods=['POST'])
def supprimer_location(id):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    location = LocationTerrain.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    flash("Réservation supprimée avec succès", "success")
    return redirect(url_for('locations_terrains'))

# Routes pour la gestion des groupes (à ajouter dans app.py)

@app.route('/ajouter_groupe', methods=['POST'])
def ajouter_groupe():
    # --- Vérification d'accès ---
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        return jsonify({"error": "Accès non autorisé"}), 403

    current_season_code = session.get('saison_code')
    if not current_season_code:
        return jsonify({"error": "Aucune saison active"}), 400

    data = request.get_json()
    group_name = data.get('groupName')
    entraineur_id = data.get('entraineurId')
    prep_physique_id = data.get('prepPhysiqueId')
    cotisation = data.get('cotisation')

    # --- Validation des champs obligatoires ---
    if not group_name or not entraineur_id:
        return jsonify({"error": "Nom et entraîneur requis"}), 400

    # --- Vérifier l'existence du groupe dans la saison courante ---
    existing_group = Groupe.query.filter_by(nom_groupe=group_name, saison_code=current_season_code).first()
    if existing_group:
        return jsonify({"error": f"Groupe '{group_name}' existe déjà dans la saison {current_season_code}"}), 400

    try:
        # --- Récupérer l'entraîneur ---
        entraineur = Entraineur.query.get(entraineur_id)
        if not entraineur:
            return jsonify({"error": "Entraîneur introuvable"}), 404

        # --- Récupérer le préparateur physique ---
        prep_physique_nom = None
        if prep_physique_id:
            prep_physique = Entraineur.query.get(prep_physique_id)
            if prep_physique and prep_physique.type_abonnement == "prep_physique":
                prep_physique_nom = f"{prep_physique.nom} {prep_physique.prenom}"

        # --- Création du nouveau groupe ---
        nouveau_groupe = Groupe(
            nom_groupe=group_name,
            entraineur_nom=f"{entraineur.nom} {entraineur.prenom}",
            type_abonnement=entraineur.type_abonnement,
            categorie=group_name.split('-')[0],
            preparateur_physique=prep_physique_nom,
            saison_code=current_season_code,           # 🆕 Saison actuelle
            date_creation=datetime.utcnow()             # 🆕 Date automatique
        )

        db.session.add(nouveau_groupe)
        db.session.flush()  # Permet de récupérer l'ID avant le commit

        # --- Création de la cotisation liée (si fournie) ---
        if cotisation:
            nouvelle_cotisation = Cotisation(
                nom_cotisation=group_name,
                montant_cotisation=float(cotisation)
            )
            db.session.add(nouvelle_cotisation)

        db.session.commit()
        return jsonify({
            "message": f"Groupe '{group_name}' ajouté avec succès pour la saison {current_season_code}",
            "groupe_id": nouveau_groupe.id_groupe
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de la création du groupe : {str(e)}"}), 500

# Route avec le bon nom pour correspondre au JS
@app.route('/api/get_groupe_details/<int:groupe_id>', methods=['GET'])
def get_groupe_details(groupe_id):
    """Récupérer les détails d'un groupe pour l'édition"""
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        return jsonify({"success": False, "error": "Accès non autorisé"}), 403
    
    try:
        groupe = Groupe.query.get_or_404(groupe_id)
        
        # Récupérer la cotisation associée
        cotisation = Cotisation.query.filter_by(nom_cotisation=groupe.nom_groupe).first()
        
        # Récupérer les adhérents du groupe
        current_season_code = session.get('saison_code')
        adherents = Adherent.query.filter_by(
            groupe=groupe.nom_groupe,
            code_saison=current_season_code,
            status='Actif'
        ).all()
        
        # Récupérer l'ID de l'entraîneur
        entraineur = Entraineur.query.filter(
            db.func.concat(Entraineur.nom, ' ', Entraineur.prenom) == groupe.entraineur_nom
        ).first()
        
        # Récupérer l'ID du préparateur physique
        prep_physique_id = None
        if groupe.preparateur_physique:
            prep_physique = Entraineur.query.filter(
                db.func.concat(Entraineur.nom, ' ', Entraineur.prenom) == groupe.preparateur_physique
            ).first()
            if prep_physique:
                prep_physique_id = prep_physique.id_entraineur
        
        return jsonify({
            "success": True,
            "groupe": {
                "id_groupe": groupe.id_groupe,
                "nom_groupe": groupe.nom_groupe,
                "entraineur_id": entraineur.id_entraineur if entraineur else None,
                "entraineur_nom": groupe.entraineur_nom,
                "prep_physique_id": prep_physique_id,
                "prep_physique_nom": groupe.preparateur_physique
            },
            "cotisation": float(cotisation.montant_cotisation) if cotisation else None,
            "adherents": [{
                "matricule": a.matricule,
                "nom": a.nom,
                "prenom": a.prenom
            } for a in adherents]
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/update_groupe/<int:groupe_id>', methods=['POST'])
def update_groupe(groupe_id):
    """Mettre à jour un groupe"""
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        return jsonify({"success": False, "error": "Accès non autorisé"}), 403
    
    try:
        data = request.get_json()
        groupe = Groupe.query.get_or_404(groupe_id)
        
        # Mettre à jour l'entraîneur
        if data.get('entraineur_id'):
            entraineur = Entraineur.query.get(data['entraineur_id'])
            if entraineur:
                ancien_entraineur = groupe.entraineur_nom
                nouveau_nom = f"{entraineur.nom} {entraineur.prenom}"
                
                # Mettre à jour le groupe
                groupe.entraineur_nom = nouveau_nom
                
                # Mettre à jour tous les adhérents du groupe
                current_season_code = session.get('saison_code')
                adherents = Adherent.query.filter_by(
                    groupe=groupe.nom_groupe,
                    entraineur=ancien_entraineur,
                    code_saison=current_season_code
                ).all()
                
                for adherent in adherents:
                    adherent.entraineur = nouveau_nom
        
        # Mettre à jour le préparateur physique
        if 'prep_physique_id' in data:
            if data['prep_physique_id']:
                prep = Entraineur.query.get(data['prep_physique_id'])
                if prep:
                    groupe.preparateur_physique = f"{prep.nom} {prep.prenom}"
            else:
                groupe.preparateur_physique = None
        
        # Mettre à jour la cotisation
        if 'cotisation' in data:
            cotisation = Cotisation.query.filter_by(nom_cotisation=groupe.nom_groupe).first()
            
            if data['cotisation']:
                nouveau_montant = float(data['cotisation'])
                
                if cotisation:
                    # Mettre à jour
                    ancienne_cotisation = cotisation.montant_cotisation
                    cotisation.montant_cotisation = nouveau_montant
                    
                    # Mettre à jour tous les adhérents qui ont l'ancienne cotisation
                    current_season_code = session.get('saison_code')
                    adherents = Adherent.query.filter_by(
                        groupe=groupe.nom_groupe,
                        cotisation=ancienne_cotisation,
                        code_saison=current_season_code
                    ).all()
                    
                    for adherent in adherents:
                        adherent.cotisation = nouveau_montant
                else:
                    # Créer
                    nouvelle_cotisation = Cotisation(
                        nom_cotisation=groupe.nom_groupe,
                        montant_cotisation=nouveau_montant
                    )
                    db.session.add(nouvelle_cotisation)
                    
                    # Appliquer aux adhérents du groupe qui n'ont pas de cotisation
                    current_season_code = session.get('saison_code')
                    adherents = Adherent.query.filter_by(
                        groupe=groupe.nom_groupe,
                        code_saison=current_season_code
                    ).filter(
                        or_(Adherent.cotisation == None, Adherent.cotisation == 0)
                    ).all()
                    
                    for adherent in adherents:
                        adherent.cotisation = nouveau_montant
            else:
                # Supprimer la cotisation si mise à 0 ou vide
                if cotisation:
                    db.session.delete(cotisation)
        
        db.session.commit()
        return jsonify({"success": True, "message": "Groupe mis à jour avec succès"}), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/retirer_adherent_groupe/<int:groupe_id>', methods=['POST'])
def retirer_adherent_groupe(groupe_id):
    """Retirer un adhérent d'un groupe et réinitialiser ses champs"""
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        return jsonify({"error": "Accès non autorisé"}), 403
    
    try:
        current_season_code = session.get('saison_code')
        if not current_season_code:
            return jsonify({"error": "Aucune saison sélectionnée"}), 400
        
        data = request.get_json()
        matricule = data.get('matricule')
        
        if not matricule:
            return jsonify({"error": "Matricule non fourni"}), 400
        
        groupe = Groupe.query.get_or_404(groupe_id)
        
        # Trouver l'adhérent
        adherent = Adherent.query.filter_by(
            matricule=matricule,
            groupe=groupe.nom_groupe,
            code_saison=current_season_code
        ).first()
        
        if not adherent:
            return jsonify({"error": "Adhérent non trouvé dans ce groupe"}), 404
        
        # Réinitialiser tous les champs liés au groupe
        adherent.groupe = None
        adherent.entraineur = None
        adherent.cotisation = None
        adherent.remise = None
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Adhérent retiré et champs réinitialisés avec succès"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
@app.route('/directeur_technique', methods=['GET', 'POST'])
@season_required
def directeur_technique():
    # Vérification des droits d'accès
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    current_season_code = session.get('saison_code')
    if not current_season_code:
        flash("Veuillez sélectionner une saison.", "warning")
        return redirect(url_for('login'))

    # Contexts saisonniers
    seance_season = SeasonContext(Seance)
    adherent_season = SeasonContext(Adherent)

    # Création des créneaux de 30 minutes
    creneaux = [
        {'start': time(hour, minute), 'end': time(hour if minute == 0 else hour + 1, 30 if minute == 0 else 0)}
        for hour in range(8, 21)
        for minute in [0, 30]
    ]

    # --- GESTION DES ACTIONS POST ---
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'changer_entraineur':
            groupe_id = request.form.get('groupe_id')
            nouvel_entraineur_id = request.form.get('entraineur_id')
            groupe = Groupe.query.get(groupe_id)
            ancien_entraineur = groupe.entraineur_nom
            nouveau_entraineur = Entraineur.query.get(nouvel_entraineur_id)

            seance_season.filter_query(
                Seance.query.filter_by(entraineur=ancien_entraineur)
            ).update({'entraineur': f"{nouveau_entraineur.nom} {nouveau_entraineur.prenom}"})

            groupe.entraineur_nom = f"{nouveau_entraineur.nom} {nouveau_entraineur.prenom}"
            db.session.commit()
            flash("Entraîneur modifié avec succès", "success")

        elif action == 'changer_prep_physique':
            groupe_id = request.form.get('groupe_id')
            nouveau_prep_id = request.form.get('prep_physique_id')
            groupe = Groupe.query.get(groupe_id)

            if nouveau_prep_id:
                nouveau_prep = Entraineur.query.get(nouveau_prep_id)
                groupe.preparateur_physique = (
                    f"{nouveau_prep.nom} {nouveau_prep.prenom}"
                    if nouveau_prep and nouveau_prep.type_abonnement == "prep_physique"
                    else None
                )
            else:
                groupe.preparateur_physique = None

            db.session.commit()
            flash("Préparateur physique modifié avec succès", "success")

        elif action == 'supprimer_seance':
            seance_id = request.form.get('seance_id')
            seance = Seance.query.get(seance_id)
            if seance:
                db.session.delete(seance)
                db.session.commit()
                flash("Séance supprimée", "success")

    # --- LOGIQUE D'AFFICHAGE DES DONNÉES ---
    week_offset = request.args.get('week_offset', 0, type=int)
    day_offset = max(0, min(6, request.args.get('day_offset', 0, type=int)))

    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    current_day = start_of_week + timedelta(days=day_offset)

    # Récupération des groupes de la saison
    groupes = Groupe.query.all()

    entraineurs = Entraineur.query.filter_by(status='Actif').all()
    prep_physiques = Entraineur.query.filter_by(type_abonnement="prep_physique", status='Actif').all()

    seances_week = seance_season.filter_query(
        Seance.query.filter(
            Seance.date >= start_of_week.date(),
            Seance.date <= (start_of_week + timedelta(days=6)).date()
        )
    ).all()

    seances_day = seance_season.filter_query(
        Seance.query.filter(Seance.date == current_day.date())
    ).all()

    # Comptage des séances par groupe
    seances_par_groupe = {}
    for seance in seances_week:
        seances_par_groupe[seance.groupe] = seances_par_groupe.get(seance.groupe, 0) + 1

    # Liste des adhérents actifs de la saison
    all_adherents = adherent_season.filter_query(
        Adherent.query.filter_by(status='Actif')
    ).all()

    adherents_list = [
        {'matricule': a.matricule, 'nom': a.nom, 'prenom': a.prenom}
        for a in all_adherents
    ]

    # ← NOUVEAU : Récupérer les adhérents NON affectés à un groupe
    adherents_non_affectes = Adherent.query.filter(
        Adherent.code_saison == current_season_code,
        Adherent.status == 'Actif',
        or_(
            Adherent.groupe.is_(None),
            Adherent.groupe == '',
            Adherent.groupe == 'None'
        )
    ).order_by(Adherent.nom, Adherent.prenom).all()

    # Transformer en liste de dictionnaires
    adherents_non_affectes_list = [{
        'matricule': a.matricule,
        'nom': a.nom,
        'prenom': a.prenom,
        'type_abonnement': a.type_abonnement or 'N/D',
        'date_naissance': a.date_naissance.strftime('%d/%m/%Y') if a.date_naissance else 'N/D',
        'date_inscription': a.date_inscription.strftime('%d/%m/%Y') if a.date_inscription else 'N/D'
    } for a in adherents_non_affectes]

    # Rendu de la page
    return render_template(
        'gestion_groupes.html',
        current_day=current_day,
        week_offset=week_offset,
        day_offset=day_offset,
        groupes=groupes,
        entraineurs=entraineurs,
        prep_physiques=prep_physiques,
        seances=seances_day,
        seances_week=seances_week,
        creneaux=creneaux,
        terrains=range(1, 10),
        seances_par_groupe=seances_par_groupe,
        all_adherents=adherents_list,
        adherents_json=json.dumps(adherents_list),
        adherents_non_affectes=adherents_non_affectes_list,  # ← NOUVEAU
        saison_code=current_season_code,
        saison_type=session.get('saison_type'),
        saison_year=session.get('saison')
    )

@app.route('/planning_prep_physique', methods=['GET', 'POST'])
@season_required
def planning_prep_physique():
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    current_season_code = session.get('saison_code')
    if not current_season_code:
        flash("Veuillez sélectionner une saison.", "warning")
        return redirect(url_for('login'))

    season = SeasonContext(Seance)

    # Créneaux de 30 minutes
    creneaux = []
    for hour in range(8, 22):
        for minute in [0, 30]:
            start_time = time(hour, minute)
            end_hour = hour if minute == 0 else hour + 1
            end_minute = 30 if minute == 0 else 0
            end_time = time(end_hour, end_minute)
            creneaux.append({'start': start_time, 'end': end_time})

    week_offset = request.args.get('week_offset', 0, type=int)
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    days_of_week = [start_of_week + timedelta(days=i) for i in range(7)]

    seances_week = season.filter_query(
        Seance.query.filter(
            Seance.type_seance == 'prep_physique',
            Seance.date >= start_of_week.date(),
            Seance.date <= (start_of_week + timedelta(days=6)).date()
        )
    ).all()

    seances_dict = {
        day.date(): {c['start']: [] for c in creneaux}
        for day in days_of_week
    }

    for s in seances_week:
        if s.date in seances_dict and s.heure_debut in seances_dict[s.date]:
            seances_dict[s.date][s.heure_debut].append(s)

    return render_template(
        'planning_prep_physique.html',
        days_of_week=days_of_week,
        creneaux=creneaux,
        seances_dict=seances_dict,
        week_offset=week_offset,
        saison_code=current_season_code,
        saison_type=session.get('saison_type'),
        saison_year=session.get('saison')
    )


@app.route('/planning', methods=['GET', 'POST'])
@season_required
def planning():
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    current_season_code = session.get('saison_code')
    if not current_season_code:
        flash("Veuillez sélectionner une saison.", "warning")
        return redirect(url_for('login'))

    seance_season = SeasonContext(Seance)
    adherent_season = SeasonContext(Adherent)

    creneaux = []
    start_hour = 8  # 8h
    end_hour = 22   # 22h
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:
            start_time = time(hour, minute)
            end_time = time(hour, minute + 30) if minute == 0 else time(hour + 1, 0)
            if end_time <= time(end_hour, 0):
                creneaux.append({'start': start_time, 'end': end_time})

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'changer_entraineur':
            groupe_id = request.form.get('groupe_id')
            nouvel_entraineur_id = request.form.get('entraineur_id')
            groupe = Groupe.query.get(groupe_id)
            ancien_entraineur = groupe.entraineur_nom
            nouveau_entraineur = Entraineur.query.get(nouvel_entraineur_id)
            
            seance_season.filter_query(
                Seance.query.filter_by(entraineur=ancien_entraineur)
            ).update({'entraineur': nouveau_entraineur.nom + ' ' + nouveau_entraineur.prenom})
            
            groupe.entraineur_nom = nouveau_entraineur.nom + ' ' + nouveau_entraineur.prenom
            db.session.commit()
            flash("Entraîneur modifié avec succès", "success")

        elif action == 'supprimer_seance':
            seance_id = request.form.get('seance_id')
            seance = Seance.query.get(seance_id)
            if seance:
                db.session.delete(seance)
                db.session.commit()
                flash("Séance supprimée", "success")
    
    week_offset = request.args.get('week_offset', 0, type=int)
    day_offset = request.args.get('day_offset', 0, type=int)
    
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    day_offset = max(0, min(6, day_offset))
    current_day = start_of_week + timedelta(days=day_offset)

    groupes = Groupe.query.all()
    entraineurs = Entraineur.query.filter_by(status='Actif').all()
    
      # Séances pour la semaine - FILTRAGE DIRECT par code_saison
    seances_week = Seance.query.filter(
        Seance.date >= start_of_week.date(),
        Seance.date <= (start_of_week + timedelta(days=6)).date(),
        Seance.code_saison == current_season_code
    ).all()
    
    seances_day = Seance.query.filter(
        Seance.date == current_day.date(),
        Seance.code_saison == current_season_code
    ).order_by(Seance.heure_debut).all()  # Tri par heure de début


    seances_par_groupe = {}
    for seance in seances_week:
        if seance.groupe not in seances_par_groupe:
            seances_par_groupe[seance.groupe] = 0
        seances_par_groupe[seance.groupe] += 1

    all_adherents = adherent_season.filter_query(
        Adherent.query.filter_by(status='Actif')
    ).all()
    
    adherents_list = [{
        'matricule': a.matricule,
        'nom': a.nom,
        'prenom': a.prenom
    } for a in all_adherents]

    return render_template(
        'planning.html',
        current_day=current_day,
        week_offset=week_offset,
        day_offset=day_offset,
        groupes=groupes,
        entraineurs=entraineurs,
        seances=seances_day,  # Inclut maintenant les durées
        seances_week=seances_week,
        creneaux=creneaux,
        terrains=range(1, 10),
        all_adherents=adherents_list,
        adherents_json=json.dumps(adherents_list),
        saison_code=current_season_code,
        saison_type=session.get('saison_type'),
        saison_year=session.get('saison')
    )


@app.route('/ajouter_seance', methods=['POST'])
def ajouter_seance():
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        return jsonify({"error": "Accès non autorisé"}), 403
    
    data = request.get_json()
    groupe = Groupe.query.get(data['groupe_id'])
    if not groupe:
        return jsonify({"error": "Groupe introuvable"}), 404

    try:
        # Récupération du code saison courant
        current_season_code = session.get('saison_code')
        if not current_season_code:
            return jsonify({"error": "Aucune saison sélectionnée"}), 400

        # Récupération de la date
        date_str = data['date']
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()

        # Heures début et fin
        heure_debut = datetime.strptime(data['heure_debut'], '%H:%M').time()
        heure_fin = datetime.strptime(data['heure_fin'], '%H:%M').time()
        
        # Vérifier que l'heure de fin est après l'heure de début
        if heure_fin <= heure_debut:
            return jsonify({"error": "L'heure de fin doit être après l'heure de début"}), 400

        # Calculer la durée en minutes
        debut_dt = datetime.combine(date_obj, heure_debut)
        fin_dt = datetime.combine(date_obj, heure_fin)
        duree_minutes = int((fin_dt - debut_dt).total_seconds() / 60)

        # Type de séance
        type_seance = data.get('type_seance', 'entrainement')

        # Option répétition
        repeat_weekly = data.get('repeat_weekly', False)

        # Définir la période saison
        saison_debut = date(date_obj.year, 10, 1)
        saison_fin = date(date_obj.year + 1, 8, 31)

        # Vérifier si la séance doit être répétée
        dates_a_inserer = [date_obj]
        if repeat_weekly:
            current_date = date_obj + timedelta(weeks=1)
            while current_date <= saison_fin:
                dates_a_inserer.append(current_date)
                current_date += timedelta(weeks=1)

        # Boucle d'insertion avec vérification des conflits
        for d in dates_a_inserer:
            conflits = Seance.query.filter(
                Seance.date == d,
                Seance.terrain == data['terrain'],
                Seance.heure_debut < heure_fin,
                Seance.heure_fin > heure_debut,
                Seance.code_saison == current_season_code  # Filtrer par saison
            ).first()

            if conflits:
                return jsonify({"error": f"Conflit détecté pour la date {d}"}), 400
            
            nouvelle_seance = Seance(
                date=d,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                duree=duree_minutes,
                groupe=groupe.nom_groupe,
                entraineur=groupe.entraineur_nom,
                type_seance=type_seance,
                terrain=data['terrain'],
                code_saison=current_season_code  # Ajout du code saison
            )
            db.session.add(nouvelle_seance)

        db.session.commit()
        return jsonify({"message": f"{len(dates_a_inserer)} séance(s) ajoutée(s) avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de l'ajout de la séance: {str(e)}"}), 500


@app.route('/get_session_data/<int:session_id>')
def get_session_data(session_id):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        return jsonify({"error": "Accès non autorisé"}), 403
    
    seance = Seance.query.get_or_404(session_id)
    
    # Trouver l'ID de l'entraîneur par son nom
    entraineur = Entraineur.query.filter(
        db.func.concat(Entraineur.nom, ' ', Entraineur.prenom) == seance.entraineur
    ).first()
    
    return jsonify({
        'seance_id': seance.seance_id,
        'date': seance.date.isoformat(),
        'heure_debut': seance.heure_debut.strftime('%H:%M'),
        'heure_fin': seance.heure_fin.strftime('%H:%M'),
        'terrain': seance.terrain,
        'entraineur_id': entraineur.id_entraineur if entraineur else None,
        'type_seance': seance.type_seance,
        'duree': seance.duree
    })


@app.route('/edit_session', methods=['POST'])
def edit_session():
    data = request.get_json()
    seance_id = data['session_id']
    date_str = data['date']
    new_heure_debut = data['heure_debut']
    new_heure_fin = data.get('heure_fin')  # Nouvelle heure de fin
    new_terrain = data['terrain']
    entraineur_id = data['entraineur']

    try:
        new_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        try:
            new_date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            return jsonify({"error": "Format de date invalide"}), 400

    entraineur = Entraineur.query.filter_by(id_entraineur=entraineur_id).first()
    if not entraineur:
        return jsonify({"error": "Entraîneur introuvable"}), 404
    new_entraineur = f"{entraineur.nom} {entraineur.prenom}"

    session = Seance.query.get(seance_id)
    if not session:
        return jsonify({"error": "Séance non trouvée"}), 404

    try:
        new_heure_debut_obj = datetime.strptime(new_heure_debut, '%H:%M').time()
        
        if new_heure_fin:
            new_heure_fin_obj = datetime.strptime(new_heure_fin, '%H:%M').time()
        else:
            # Si pas d'heure de fin fournie, calculer selon le type
            if session.type_seance == "prep_physique":
                new_heure_fin_obj = (datetime.combine(new_date_obj, new_heure_debut_obj) + timedelta(minutes=60)).time()
            else:
                new_heure_fin_obj = (datetime.combine(new_date_obj, new_heure_debut_obj) + timedelta(minutes=90)).time()

        # Vérifier que fin > début
        if datetime.combine(new_date_obj, new_heure_fin_obj) <= datetime.combine(new_date_obj, new_heure_debut_obj):
            return jsonify({"error": "L'heure de fin doit être après l'heure de début"}), 400

        # Vérification des conflits
        terrain_conflit = Seance.query.filter(
            Seance.seance_id != seance_id,
            Seance.terrain == new_terrain,
            Seance.date == new_date_obj,
            Seance.heure_debut < new_heure_fin_obj,
            Seance.heure_fin > new_heure_debut_obj
        ).first()

        if terrain_conflit:
            return jsonify({"error": "Conflit de planning sur ce terrain"}), 400

        entraineur_conflit = Seance.query.filter(
            Seance.seance_id != seance_id,
            Seance.entraineur == new_entraineur,
            Seance.date == new_date_obj,
            Seance.heure_debut < new_heure_fin_obj,
            Seance.heure_fin > new_heure_debut_obj
        ).first()

        if entraineur_conflit:
            return jsonify({"error": "L'entraîneur est occupé à ce créneau"}), 400

        # Mise à jour
        session.date = new_date_obj
        session.heure_debut = new_heure_debut_obj
        session.heure_fin = new_heure_fin_obj
        session.terrain = new_terrain
        session.entraineur = new_entraineur
        db.session.commit()

        return jsonify({"message": "Séance modifiée avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@app.route('/api/search_adherent/<string:matricule>', methods=['GET'])
def api_search_adherent(matricule):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    adherents = Adherent.query.filter(Adherent.matricule.like(f"%{matricule}%")).all()
    adherents_list = [
        {"matricule": adherent.matricule, "nom": adherent.nom, "prenom": adherent.prenom}
        for adherent in adherents
    ]
    return jsonify({"adherents": adherents_list}), 200

@app.route('/changer_mot_de_passe', methods=['POST'])
def changer_mot_de_passe():
    # Vérifier si l'utilisateur est connecté (présence du 'username' dans la session)
    username = session.get('username')
    if not username:
        return jsonify({"error": "Vous devez être connecté pour changer votre mot de passe."}), 401

    data = request.get_json()
    nouveau_mot_de_passe = data.get('nouveau_mot_de_passe')
    confirmation_mot_de_passe = data.get('confirmation_mot_de_passe')
   

    # Vérification des champs
    if not nouveau_mot_de_passe or not confirmation_mot_de_passe:
        return jsonify({"error": "Veuillez remplir tous les champs."}), 400

    if nouveau_mot_de_passe != confirmation_mot_de_passe:
        return jsonify({"error": "Les mots de passe ne correspondent pas."}), 400

    # Rechercher l'utilisateur par username
    user = User.query.filter_by(utilisateur=username).first()

    if not user:
        return jsonify({"error": "Utilisateur introuvable."}), 404

    # Hachage du nouveau mot de passe
    hashed_password = hashlib.sha256(nouveau_mot_de_passe.encode()).hexdigest()

    # Mettre à jour le mot de passe de l'utilisateur
    user.password = hashed_password

    # Sauvegarder les modifications dans la base de données
    db.session.commit()

    return jsonify({"message": "Mot de passe mis à jour avec succès."}), 200





from flask import make_response
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
import pandas as pd
from io import BytesIO

@app.route('/export-schedule')
def export_schedule():
    # Récupération des paramètres
    week_offset = request.args.get('week_offset', 0, type=int)
    day_offset = request.args.get('day_offset', 0, type=int)
    export_type = request.args.get('export_type', 'pdf')
    scope = request.args.get('scope', 'day')

    # Calcul des dates
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    current_day = start_of_week + timedelta(days=day_offset)

    # Récupération des données
    if scope == 'day':
        seances = Seance.query.filter(Seance.date == current_day.date()).all()
        days = [current_day]
    else:
        days = [start_of_week + timedelta(days=i) for i in range(7)]
        seances = Seance.query.filter(
            Seance.date >= start_of_week.date(),
            Seance.date <= (start_of_week + timedelta(days=6)).date()
        ).all()

    # Création des créneaux horaires
    # Création des créneaux horaires
    creneaux = [
        {'start': time(8, 0), 'end': time(9, 30)},
        {'start': time(9, 30), 'end': time(11, 0)},
        {'start': time(11, 0), 'end': time(12, 30)},
        {'start': time(12, 30), 'end': time(14, 0)},
        {'start': time(14, 0), 'end': time(15, 30)},
        {'start': time(15, 30), 'end': time(17, 0)},
        {'start': time(17, 0), 'end': time(18, 30)},
        {'start': time(18, 30), 'end': time(20, 0)}
    ]

    # Génération du fichier
    if export_type == 'excel':
        return generate_excel(seances, days, creneaux, scope)
    else:
        return generate_pdf(seances, days, creneaux, scope)
import locale

def generate_excel(seances, days, creneaux, scope):
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'french')
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book

    # Styles personnalisés
    header_format = workbook.add_format({
        'bold': True, 
        'bg_color': '#D3D3D3',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    time_header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'border': 1,
        'align': 'center'
    })

    cell_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top',
        'border': 1
    })

    for day in days:
        # Création des données structurées
        data = []
        
        # Ligne 1 : Date fusionnée
        data.append([f"{day.strftime('%A %d/%m/%Y')}"] + [''] * (len(creneaux)))
        
        # Ligne 2 : En-têtes des créneaux
        data.append(['Terrain'] + [f"{c['start'].strftime('%H:%M')}-{c['end'].strftime('%H:%M')}" for c in creneaux])
        
        # Lignes suivantes : Données des terrains
        for terrain in range(1, 8):
            row = [f'Terrain {terrain}']
            for creneau in creneaux:
                sessions = [
                    f"{s.groupe}\r\n{s.entraineur}" 
                    for s in seances 
                    if s.date == day.date() 
                    and s.terrain == terrain 
                    and s.heure_debut.strftime('%H:%M') == creneau['start'].strftime('%H:%M')
                ]
                row.append('\n'.join(sessions))
            data.append(row)
        
        # Création du DataFrame
        df = pd.DataFrame(data[2:], columns=data[1])
        
        # Écriture dans Excel
        df.to_excel(writer, sheet_name=day.strftime('%A'), index=False, startrow=2, header=False)
        
        # Accès à la feuille
        worksheet = writer.sheets[day.strftime('%A')]
        
        # Fusionner la cellule de date
        worksheet.merge_range(0, 0, 0, len(creneaux), data[0][0], header_format)
        
        # Écrire les en-têtes de créneaux
        for col_num, value in enumerate(data[1]):
            worksheet.write(1, col_num, value, time_header_format)
        
        # Formatage des dimensions
        worksheet.set_column(0, len(creneaux), 25)  # 150px = ~25 unités Excel
        for row_num in range(2, len(data)+2):
            worksheet.set_row(row_num, 50, cell_format)  # Hauteur de ligne 50px
        

    writer.close()
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                    download_name=f'emploi_du_temps_{scope}.xlsx')

def generate_pdf(seances, days, creneaux, scope):
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, PageBreak
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    import locale

    # Configuration locale française
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'french')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []

    # Style du tableau
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D3D3D3')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ])

    for day in days:
        # Titre de la journée
        title = day.strftime('%A %d/%m/%Y').capitalize()
        elements.append(Table([[title]], 
            style=[
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 14),
                ('BOTTOMPADDING', (0,0), (-1,-1), 15),
            ]))
        
        # En-têtes des créneaux
        headers = ['Terrain'] + [f"{c['start'].strftime('%H:%M')}\n-\n{c['end'].strftime('%H:%M')}" for c in creneaux]
        data = [headers]

        # Données des terrains
        for terrain in range(1, 8):
            row = [f'Terrain {terrain}']
            for creneau in creneaux:
                sessions = [
                    f"{s.groupe}\n({s.entraineur})" 
                    for s in seances 
                    if s.date == day.date() 
                    and s.terrain == terrain 
                    and s.heure_debut.strftime('%H:%M') == creneau['start'].strftime('%H:%M')
                ]
                row.append('\n\n'.join(sessions))
            data.append(row)

        # Création du tableau
        table = Table(data, repeatRows=1)
        table.setStyle(style)
        
        # Dimensions des colonnes
        col_widths = [3*cm] + [3.5*cm]*len(creneaux)  # 3cm pour les terrains, 3.5cm pour les créneaux
        table._argW = col_widths
        
        elements.append(table)
        elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, 
                   mimetype='application/pdf',
                   download_name=f'emploi_du_temps_{scope}.pdf',
                   as_attachment=True)
                   
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        utilisateur = request.form.get('utilisateur')
        password = request.form.get('password')
        saison_code = request.form.get('saison')  # This will be like 'S2025' or 'E2025'
        
        user = User.query.filter_by(utilisateur=utilisateur).first()
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user and user.password == hashed_password:
            # Store user info in session
            session['user_id'] = user.id
            session['username'] = user.utilisateur
            session['role'] = user.role
            
            # Store both the full season code and extract the year
            session['saison_code'] = saison_code  # Store full code (e.g., 'S2025')
            session['saison'] = int(saison_code[1:])  # Store year as integer (e.g., 2025)
            session['saison_type'] = saison_code[0]   # Store type ('S' or 'E')
            print(f"Session variables set: {session}")  # Add this debug line
            # Get season codes
            season_codes = get_season_codes(int(saison_code[1:]))
            session['saison_normale'] = season_codes['normal']
            session['saison_ete'] = season_codes['summer']
            
            flash("Connexion réussie.", "success")
            
            if user.role == 'admin':
                return redirect(url_for('admin'))
            elif user.role == 'directeur_technique':
                return redirect(url_for('directeur_technique'))
            elif user.role == 'entraineur':
                return redirect(url_for('entraineur'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")

    # Calculate default season code
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    
    # If we're in October or later, use next year
    default_year = current_year + 1 if current_month >= 10 else current_year
    # If we're in July-September, use E, otherwise S
    default_type = 'E' if 7 <= current_month <= 9 else 'S'
    default_season = f"{default_type}{default_year}"
    
    return render_template('signin.html', 
                         default_season=default_season,
                         current_year=current_year)

@app.route('/ajouter_utilisateur', methods=['GET', 'POST'])
def ajouter_utilisateur():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        utilisateur = request.form.get('utilisateur')
        password = request.form.get('password')
        role = request.form.get('role')

        if not all([utilisateur, password, role]):
            flash("Tous les champs sont obligatoires.", "danger")
            return redirect(url_for('ajouter_utilisateur'))

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            new_utuiisateur = User(utilisateur=utilisateur, password=hashed_password, role=role)
            db.session.add(new_utuiisateur)
            db.session.commit()
            flash("Utilisateur ajouté avec succès.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout de l'utilisateur : {str(e)}", "danger")
        return redirect(url_for('admin'))

    return render_template('ajouter_utilisateur.html')


@app.route('/gerer_utilisateur', methods=['GET', 'POST'])
def gerer_utilisateur():
    utilisateurs=User.query.all()
    return render_template('gerer_utilisateur.html',utilisateurs=utilisateurs)

@app.route('/modifier_utilisateur/<int:id>', methods=['GET', 'POST'])
def modifier_utilisateur(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    # Récupérer l'utilisateur par son ID, sinon retourner une erreur 404 si non trouvé
    utilisateur = User.query.get_or_404(id)
    
    if request.method == 'POST':
        utilisateur.utilisateur = request.form['utilisateur']
        new_password = request.form['password']
        
        # Vérifier si le mot de passe a été modifié
        if new_password != '':  # Placeholder value
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            utilisateur.password = hashed_password
        
        utilisateur.role = request.form['role']
        
        db.session.commit()
        return redirect(url_for('gerer_utilisateur'))
    
    return render_template('modifier_utilisateur.html', utilisateur=utilisateur)

@app.route('/supprimer_utilisateur/<int:id>', methods=['GET', 'POST'])
def supprimer_utilisateur(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    # Récupérer l'adhérent par son ID
    utilisateur = User.query.get_or_404(id)

    # Supprimer l'adhérent de la base de données
    db.session.delete(utilisateur)
    db.session.commit()

    # Rediriger vers la page d'accueil ou la liste des adhérents
    return redirect(url_for('gerer_utilisateur'))




from datetime import datetime

def generer_code_saison():
    """
    Génère le code saison basé sur la date actuelle
    Saison (S): octobre à juin (année suivante)
    École d'été (E): juin à août (même année)
    """
    aujourd_hui = datetime.now()
    mois = aujourd_hui.month
    annee = aujourd_hui.year
    
    if mois >= 10:  # Octobre à décembre - début de saison
        return f"S{annee + 1}"
    elif mois >= 6 and mois <= 8:  # Juin à août - école d'été
        return f"E{annee}"
    else:  # Janvier à mai - fin de saison
        return f"S{annee}"

def get_next_matricule(code_saison):
    """
    Génère le prochain matricule disponible pour une saison donnée.
    Réutilise les matricules des adhérents supprimés.
    """
    # Récupérer tous les matricules utilisés pour cette saison
    matricules_utilises = db.session.query(Adherent.matricule).filter(
        Adherent.code_saison == code_saison
    ).order_by(Adherent.matricule).all()
    
    matricules_utilises = [m[0] for m in matricules_utilises]
    
    # Si aucun matricule, commencer à 1
    if not matricules_utilises:
        return 1
    
    # Chercher le premier trou dans la séquence
    for i in range(1, max(matricules_utilises) + 2):
        if i not in matricules_utilises:
            return i
    
    # Si aucun trou, retourner le max + 1
    return max(matricules_utilises) + 1

@app.route('/ajouter_adherent', methods=['POST', 'GET'])
def ajouter_adherent():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    code_saison_defaut = session.get('saison_code')
    
    if request.method == 'POST':
        # Récupérer nom et prénom
        nom = request.form['Nom'].strip()
        prenom = request.form['Prénom'].strip()
        code_saison = request.form.get('code_saison', code_saison_defaut)
        
        # CONTRÔLE BACKEND : Vérifier les doublons (nom + prénom + saison)
        adherent_existant = Adherent.query.filter(
            func.lower(Adherent.nom) == nom.lower(),
            func.lower(Adherent.prenom) == prenom.lower(),
            Adherent.code_saison == code_saison
        ).first()
        
        if adherent_existant:
            flash(
                f"Un adhérent nommé {nom} {prenom} existe déjà pour la saison {code_saison} "
                f"(Matricule: {adherent_existant.matricule}). Impossible d'ajouter un doublon.",
                'danger'
            )
            return redirect(url_for('ajouter_adherent'))
        
        # Calculer le prochain matricule disponible pour cette saison
        matricule = get_next_matricule(code_saison)
        
        # Créer le nouvel adhérent
        nouveau_adherent = Adherent(
            nom=nom,
            prenom=prenom,
            date_naissance=request.form['date_naissance'],
            date_inscription=request.form['date_inscription'],
            sexe=request.form['sexe'],
            tel1=request.form['tel1'],
            tel2=request.form.get('tel2'),
            type_abonnement=request.form['type_abonnement'],
            categorie=request.form['type_abonnement'],
            matricule=matricule,
            email=request.form.get('email'),
            code_saison=code_saison,
            paye='N',
            status='Actif',
            groupe=None,
            entraineur=None,
            cotisation=None,
            remise=None
        )

        try:
            db.session.add(nouveau_adherent)
            db.session.commit()
            flash(
                f'Adhérent {nouveau_adherent.nom} {nouveau_adherent.prenom} ajouté avec succès '
                f'(Matricule: {matricule}, Saison: {code_saison})', 
                'success'
            )
            return redirect(url_for('gerer_adherent'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur : {str(e)}", 'danger')
    
    # Récupérer les adhérents existants de la saison pour le contrôle frontend
    adherents_existants = Adherent.query.filter_by(
        code_saison=code_saison_defaut
    ).with_entities(
        Adherent.nom, 
        Adherent.prenom, 
        Adherent.matricule,
        Adherent.status,
        Adherent.date_inscription
    ).all()
    
    # Transformer en liste de dictionnaires pour JSON
    adherents_list = [{
        'nom': a.nom.lower(),
        'prenom': a.prenom.lower(),
        'matricule': a.matricule,
        'status': a.status,
        'date_inscription': a.date_inscription.strftime('%d/%m/%Y')
    } for a in adherents_existants]

    return render_template('ajouter_adherent.html', 
                         code_saison_defaut=code_saison_defaut,
                         adherents_existants=adherents_list)



@app.route('/gerer_adherent')
@season_required
def gerer_adherent():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    # Get current season code from session
    current_season_code = session.get('saison_code')  # Ex: 'S2025' ou 'E2025'
    if not current_season_code:
        flash("Veuillez sélectionner une saison.", "warning")
        return redirect(url_for('login'))
    
    # Filter adherents by exact season code
    adherents = Adherent.query.filter(
        Adherent.code_saison == current_season_code,
        Adherent.status == 'Actif'  # Optionnel: filtrer aussi par statut
    ).order_by(Adherent.nom).all()
    
    return render_template('gerer_adherent.html',
                         adherents=adherents,
                         saison_code=current_season_code,
                         saison_type=session.get('saison_type'),
                         saison_year=session.get('saison'))

@app.route('/modifier_adherent/<int:id>', methods=['GET', 'POST'])
def modifier_adherent(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    # Récupérer le code_saison de la session
    saison_code = session.get('saison_code')
    
    if not saison_code:
        flash("Aucune saison active. Veuillez vous reconnecter.", "danger")
        return redirect(url_for('login'))
    
    # Récupérer l'adhérent par son ID, sinon retourner une erreur 404 si non trouvé
    adherent = Adherent.query.get_or_404(id)
    
    # Filtrer les groupes par code_saison
    groupes = Groupe.query.filter_by(saison_code=saison_code).all()
    nom_groupes = [groupe.nom_groupe for groupe in groupes]
    
    if request.method == 'POST':
        adherent.nom = request.form['nom']
        adherent.prenom = request.form['prenom']
        adherent.date_naissance = request.form['date_naissance']
        adherent.sexe = request.form['sexe']
        adherent.tel1 = request.form['tel1']
        adherent.tel2 = request.form['tel2']
        adherent.type_abonnement = request.form['type_abonnement']
        adherent.ancien_abonnee = request.form['ancien_abonnee']
        adherent.groupe = request.form['groupe']
        adherent.entraineur = request.form['entraineur']
        adherent.email = request.form['email']
        adherent.status = request.form['status']
        
        db.session.commit()
        flash("Adhérent modifié avec succès.", "success")
        return redirect(url_for('gerer_adherent'))
    
    # Filtrer les entraîneurs par code_saison
    entraineurs = Entraineur.query.filter_by(code_saison=saison_code).all()
    
    return render_template('modifier_adherent.html',
                          adherent=adherent,
                          entraineurs=entraineurs,
                          nom_groupes=nom_groupes)

@app.route('/supprimer_adherent/<int:id>', methods=['GET', 'POST'])
def supprimer_adherent(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    # Récupérer l'adhérent par son ID
    adherent = Adherent.query.get_or_404(id)

    # Supprimer l'adhérent de la base de données
    db.session.delete(adherent)
    db.session.commit()

    # Rediriger vers la page d'accueil ou la liste des adhérents
    return redirect(url_for('gerer_adherent'))

@app.route('/ajouter_entraineur', methods=['POST', 'GET'])
def ajouter_entraineur():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Récupérer le code saison
            saison_type = request.form.get('saison_type')
            annee_saison = request.form.get('annee_saison')
            code_saison = f"{saison_type}{annee_saison}"
            
            # Récupérer le rôle et la catégorie
            role_technique = request.form.get('role_technique')
            type_abonnement = request.form.get('type_abonnement') if role_technique == 'Entraineur' else None
            
            # Création d'un nouvel entraîneur
            nouveau_entraineur = Entraineur(
                nom=request.form['nom'],
                prenom=request.form['prenom'],
                sexe=request.form['sexe'],
                role_technique=role_technique,  # ← AJOUTER
                type_abonnement=type_abonnement,  # ← Catégorie (peut être None)
                tel=request.form.get('tel'),
                addresse=request.form.get('addresse'),
                compte_bancaire=request.form.get('compte_bancaire'),
                status='Actif',
                code_saison=code_saison
            )

            # Créer l'utilisateur
            password = 'entraineur'
            user_nom = nouveau_entraineur.nom.replace(" ", "").lower()
            user_prenom = nouveau_entraineur.prenom.replace(" ", "").lower()
            user = f"{user_nom}.{user_prenom}"
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            new_utilisateur = User(utilisateur=user, password=hashed_password, role='entraineur')

            db.session.add(new_utilisateur)
            db.session.add(nouveau_entraineur)
            db.session.commit()

            flash("Entraîneur ajouté avec succès.", "success")
            return redirect(url_for('admin'))

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout : {str(e)}", 'danger')

    current_season_code = session.get('saison_code', 'S2025')
    current_season_type = session.get('saison_type', 'S')
    current_season_year = session.get('saison', 2025)
    
    return render_template('ajouter_entraineur.html',
                         current_season_code=current_season_code,
                         current_season_type=current_season_type,
                         current_season_year=current_season_year)

@app.route('/modifier_entraineur/<int:id>', methods=['GET', 'POST'])
def modifier_entraineur(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    entraineur = Entraineur.query.get_or_404(id)
    
    if request.method == 'POST':
        entraineur.nom = request.form['nom']
        entraineur.prenom = request.form['prenom']
        entraineur.sexe = request.form['sexe']
        entraineur.addresse = request.form.get('adresse', '')  # ⚠️ addresse dans le modèle
        entraineur.tel = request.form.get('telephone', '')  # ⚠️ tel dans le modèle
        entraineur.compte_bancaire = request.form.get('compte_bancaire', '')
        
        # Rôle technique
        entraineur.role_technique = request.form['role_technique']
        
        # Si le rôle est "Entraineur", on garde la catégorie, sinon on la met à None
        if request.form['role_technique'] == 'Entraineur':
            entraineur.type_abonnement = request.form.get('type_abonnement')
        else:
            entraineur.type_abonnement = None
        
        # Status
        entraineur.status = request.form['status']
        
        # Mettre à jour le code saison
        saison_type = request.form.get('saison_type')
        annee_saison = request.form.get('annee_saison')
        if saison_type and annee_saison:
            entraineur.code_saison = f"{saison_type}{annee_saison}"
        
        try:
            db.session.commit()
            flash("Les informations de l'entraîneur ont été mises à jour avec succès.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la mise à jour : {str(e)}", "danger")
        
        return redirect(url_for('gerer_entraineur'))
    
    # Extraire type et année de la saison
    if entraineur.code_saison:
        saison_type = entraineur.code_saison[0]
        annee_saison = entraineur.code_saison[1:]
    else:
        saison_type = session.get('saison_type', 'S')
        annee_saison = session.get('saison', 2025)
    
    return render_template('modifier_entraineur.html',
                         entraineur=entraineur,
                         saison_type=saison_type,
                         annee_saison=annee_saison)


@app.route('/gerer_entraineur', methods=['POST', 'GET'])
@season_required
def gerer_entraineur():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    # Récupérer l'année de la saison
    current_season_year = session.get('saison')
    if not current_season_year:
        flash("Veuillez sélectionner une saison.", "warning")
        return redirect(url_for('login'))
    
    # Filtrer tous les entraîneurs dont le code_saison contient l'année
    # Ex: Si année = 2025, on récupère S2025 ET E2025
    entraineurs = Entraineur.query.filter(
        Entraineur.code_saison.like(f"%{current_season_year}")
    ).all()
    
    return render_template('gerer_entraineur.html',
                         entraineurs=entraineurs,
                         saison_code=session.get('saison_code'),
                         saison_type=session.get('saison_type'),
                         saison_year=current_season_year)

@app.route('/supprimer_entraineur/<int:id>', methods=['POST', 'GET'])
def supprimer_entraineur(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    entraineur = Entraineur.query.get_or_404(id)
    nom_entraineur = entraineur.nom  # Sauvegarder le nom avant suppression
    
    try:
        # 1. Mettre à jour les adhérents qui ont cet entraîneur
        adherents_a_modifier = Adherent.query.filter(Adherent.entraineur == nom_entraineur).all()
        for adherent in adherents_a_modifier:
            adherent.entraineur = None  # ou "" selon votre préférence
        
        # 2. Mettre à jour les groupes qui ont cet entraîneur
        groupes_a_modifier = Groupe.query.filter(Groupe.entraineur_nom == nom_entraineur).all()
        for groupe in groupes_a_modifier:
            groupe.entraineur_nom = None
        
        # 3. Mettre à jour les séances qui ont cet entraîneur
        seances_a_modifier = Seance.query.filter(Seance.entraineur == nom_entraineur).all()
        for seance in seances_a_modifier:
            seance.entraineur = None
        
        # 4. Maintenant supprimer l'entraîneur
        db.session.delete(entraineur)
        
        # 5. Commit toutes les modifications
        db.session.commit()
        
        flash(f"L'entraîneur {nom_entraineur} a été supprimé avec succès. Les références dans les adhérents, groupes et séances ont été nettoyées.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la suppression : {str(e)}", "danger")
    
    return redirect(url_for('gerer_entraineur'))
    
@app.route('/discussions', methods=['GET', 'POST'])
def discussions():
    users = User.query.all()  # Récupère tous les utilisateurs
    users_list = [{'username': user.utilisateur} for user in users]

    if request.method == 'POST':
        destinataires = request.form.get('destinataires')  # Récupère la chaîne des destinataires
        objet = request.form['objet']
        corps = request.form['corps']
        expediteur = session['username']

        # Convertir la chaîne des destinataires en liste
        destinataires_list = destinataires.split(',')

        message = Message(expediteur=expediteur, destinataires=",".join(destinataires_list), objet=objet, corps=corps)
        db.session.add(message)
        db.session.commit()

        flash("Message envoyé avec succès!", "success")
        return redirect(url_for('discussions'))

    # Récupérer les messages envoyés et reçus
    messages_envoyes = Message.query.filter_by(expediteur=session['username']).all()
    messages_recus = Message.query.filter(Message.destinataires.like(f"%{session['username']}%")).all()

    # Préparer les données des messages
    messages_envoyes_data = [
        {
            'expediteur': msg.expediteur,
            'destinataires': msg.destinataires,
            'objet': msg.objet,
            'corps': msg.corps,
            'date': msg.date_envoi.strftime('%Y-%m-%d %H:%M')
        } for msg in messages_envoyes
    ]

    messages_recus_data = [
        {
            'expediteur': msg.expediteur,
            'destinataires': msg.destinataires,
            'objet': msg.objet,
            'corps': msg.corps,
            'date': msg.date_envoi.strftime('%Y-%m-%d %H:%M')
        } for msg in messages_recus
    ]

    return render_template('discussions.html', users=users_list, messages_envoyes=messages_envoyes_data, messages_recus=messages_recus_data)

@app.route('/message/<int:id>/marquer_lu', methods=['POST'])
def marquer_lu(id):
    message = Message.query.get(id)
    message.statut = 'lu'
    db.session.commit()
    return redirect(url_for('discussions'))

@app.route('/message/<int:id>/repondre', methods=['GET', 'POST'])
def repondre(id):
    if request.method == 'POST':
        corps = request.form['corps']
        message = Message.query.get(id)
        reponse = Message(expediteur=session['username'], destinataires=message.expediteur_id, objet=f"Re: {message.objet}", corps=corps)
        db.session.add(reponse)
        db.session.commit()
        flash("Réponse envoyée avec succès", "success")
        return redirect(url_for('discussions'))
    return render_template('repondre.html', message_id=id)





from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session


@app.route('/paiement', methods=['GET', 'POST'])
@season_required
def paiement():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    # Récupérer l'année de la saison depuis la session
    saison_year = session.get('saison')  # Ex: 2025
    if not saison_year:
        flash("Veuillez sélectionner une saison.", "warning")
        return redirect(url_for('login'))
    
    # Récupérer le type depuis l'URL (annuel ou ete)
    type_param = request.args.get('type', 'annuel')  # Par défaut: annuel
    
    # Déterminer le code saison selon le type
    if type_param == 'ete':
        code_saison = f"E{saison_year}"  # Ex: E2025
        saison_type = 'ete'
    else:
        code_saison = f"S{saison_year}"  # Ex: S2025
        saison_type = 'annuel'
    
    # Récupérer TOUS les adhérents de la saison pour l'autocomplete
    adherents_search_data = Adherent.query.filter_by(
        code_saison=code_saison,
        status='Actif'
    ).with_entities(
        Adherent.matricule,
        Adherent.nom,
        Adherent.prenom
    ).all()
    
    # Convertir en liste de dictionnaires pour le JS
    adherents_list = [
        {
            'matricule': adh.matricule,
            'nom': adh.nom,
            'prenom': adh.prenom,
        }
        for adh in adherents_search_data
    ]
    
    
    adherent = None
    paiements = []
    cotisations = []
    numero_carnet = 1
    numero_bon = 1
    cotisation = 0
    remise = 0
    montant_net = 0
    remise_montant = 0
    total_montant_paye = 0

    if request.method == 'POST':
        matricule = request.form.get('matricule', '').strip()
        
        if not matricule:
            flash("Veuillez saisir un matricule.", "warning")
            return render_template('paiement.html',
                                 adherent=None,
                                 paiements=[],
                                 cotisations=[],
                                 saison_type=saison_type,
                                 code_saison=code_saison,
                                 saison_year=saison_year,
                                 adherents_list=adherents_list)
        
        # Rechercher l'adhérent avec le code saison correspondant
        adherent = Adherent.query.filter_by(
            matricule=matricule,
            code_saison=code_saison,
            status='Actif'
        ).first()

        if not adherent:
            flash(f"Aucun adhérent trouvé avec le matricule {matricule} pour la saison {code_saison}.", "danger")
            return render_template('paiement.html',
                                 adherent=None,
                                 paiements=[],
                                 cotisations=[],
                                 saison_type=saison_type,
                                 code_saison=code_saison,
                                 saison_year=saison_year,
                                 adherents_list=adherents_list)

        # Récupérer les paiements existants pour cet adhérent dans la saison actuelle
        paiements = Paiement.query.filter_by(
            matricule_adherent=str(matricule),
            code_saison=code_saison
        ).order_by(Paiement.date_paiement.asc()).all()

        # Traitement du paiement si montant_paye est fourni
        if request.form.get('montant_paye'):
            try:
                montant_paye = float(request.form.get('montant_paye', 0))
                type_reglement = request.form.get('type_reglement')
                numero_cheque = request.form.get('numero_cheque')
                banque = request.form.get('banque')
                
                # Premier paiement : définir la cotisation et la remise
                if not adherent.cotisation:
                    cotisation_select = request.form.get('cotisation_select')
                    if cotisation_select:
                        cot = Cotisation.query.get(cotisation_select)
                        if cot:
                            adherent.cotisation = cot.montant_cotisation
                    
                    remise_input = request.form.get('remise_input', 0)
                    adherent.remise = float(remise_input) if remise_input else 0
                    
                    db.session.commit()
                
                # Calculer le montant restant
                cotisation = float(adherent.cotisation or 0)
                remise_pourcentage = float(adherent.remise or 0)
                remise_montant = (cotisation * remise_pourcentage) / 100
                montant_net = cotisation - remise_montant
                
                total_deja_paye = sum(float(p.montant_paye or 0) for p in paiements)
                montant_reste = max(0, montant_net - total_deja_paye - montant_paye)
                
                # Calculer le numéro de bon
                dernier_paiement = Paiement.query.order_by(Paiement.id_paiement.desc()).first()
                numero_carnet = dernier_paiement.numero_carnet if dernier_paiement else 1
                numero_bon = (dernier_paiement.numero_bon + 1) if dernier_paiement else 1
                
                if numero_bon > 50:
                    numero_carnet += 1
                    numero_bon = 1
                
                # Créer le nouveau paiement
                nouveau_paiement = Paiement(
                    matricule_adherent=str(matricule),
                    montant=montant_net,
                    montant_paye=montant_paye,
                    montant_reste=montant_reste,
                    type_reglement=type_reglement,
                    numero_cheque=numero_cheque,
                    banque=banque,
                    cotisation=cotisation,
                    remise=remise_pourcentage,
                    numero_bon=numero_bon,
                    numero_carnet=numero_carnet,
                    code_saison=code_saison
                )
                
                db.session.add(nouveau_paiement)
                
                # Mettre à jour le statut de paiement de l'adhérent
                if montant_reste <= 0:
                    adherent.paye = 'O'
                else:
                    adherent.paye = 'N'
                
                db.session.commit()
                
                flash("Paiement enregistré avec succès.", "success")
                return redirect(url_for('paiement', type=type_param))
                
            except ValueError as e:
                flash(f"Montant invalide: {str(e)}", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Erreur lors de l'enregistrement: {str(e)}", "danger")
        
        # Calculer les informations financières
        if adherent.cotisation:
            cotisation = float(adherent.cotisation)
            remise = float(adherent.remise or 0)
            remise_montant = (cotisation * remise) / 100
            montant_net = cotisation - remise_montant
            total_montant_paye = sum(float(p.montant_paye or 0) for p in paiements)
        
        # Récupérer les cotisations disponibles pour le premier paiement
        cotisations = Cotisation.query.all()
        
        # Calculer le prochain numéro de bon
        dernier_paiement = Paiement.query.order_by(Paiement.id_paiement.desc()).first()
        numero_carnet = dernier_paiement.numero_carnet if dernier_paiement else 1
        numero_bon = (dernier_paiement.numero_bon + 1) if dernier_paiement else 1
        
        if numero_bon > 50:
            numero_carnet += 1
            numero_bon = 1
    print("=== DEBUG AUTCOMPLETE ===")
    print(f"Type de adherents_list: {type(adherents_list)}")
    print(f"Nombre d'éléments: {len(adherents_list)}")
    for i, adh in enumerate(adherents_list[:5]):
        print(f"  {i+1}. {adh}")
    return render_template('paiement.html',
                         adherent=adherent,
                         paiements=paiements,
                         cotisations=cotisations,
                         cotisation=cotisation,
                         remise=remise,
                         remise_montant=remise_montant,
                         montant_net=montant_net,
                         total_montant_paye=total_montant_paye,
                         numero_carnet=numero_carnet,
                         numero_bon=numero_bon,
                         saison_type=saison_type,
                         code_saison=code_saison,
                         saison_year=saison_year,
                         adherents_list=adherents_list,
                         reste_a_payer=max(0, montant_net - total_montant_paye))

@app.route('/cotisations', methods=['GET', 'POST'])
def gestion_cotisations():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    groupes = Groupe.query.all()
    nom_groupes = [groupe.nom_groupe for groupe in groupes]
    cotisations = Cotisation.query.all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'ajouter':
            nom = request.form.get('nom')
            montant = request.form.get('montant')
            if not nom or not montant:
                flash("Tous les champs sont obligatoires", "danger")
                return redirect(url_for('gestion_cotisations'))
                
            nouvelle_cotisation = Cotisation(
                nom_cotisation=nom,
                montant_cotisation=float(montant)
            )
            db.session.add(nouvelle_cotisation)
            flash("Cotisation ajoutée avec succès", "success")

        elif action == 'modifier':
            id_cotisation = request.form.get('id')
            cotisation = Cotisation.query.get(id_cotisation)
            if cotisation:
                cotisation.nom_cotisation = request.form.get('nom')
                cotisation.montant_cotisation = float(request.form.get('montant'))
                flash("Cotisation modifiée avec succès", "success")

        elif action == 'supprimer':
            id_cotisation = request.form.get('id')
            cotisation = Cotisation.query.get(id_cotisation)
            if cotisation:
                db.session.delete(cotisation)
                flash("Cotisation supprimée avec succès", "success")

        db.session.commit()
        return redirect(url_for('gestion_cotisations'))

    return render_template('gestion_cotisations.html', cotisations=cotisations,nom_groupes=nom_groupes)


@app.route('/rechercher_adherent', methods=['POST'])
def rechercher_adherent():
    matricule = request.form.get('matricule')
    adherent = Adherent.query.filter_by(matricule=matricule).first()
    if adherent:
        return jsonify({
            'nom': adherent.nom,
            'prenom': adherent.prenom,
            'type_abonnement': adherent.type_abonnement,
            'date_inscription': adherent.date_inscription.strftime('%d/%m/%Y'),
            'cotisation': adherent.cotisation,
            'remise': adherent.remise
        })
    else:
        return jsonify({'error': 'Adhérent non trouvé'}), 404

@app.route('/gerer_abonnement')
def gerer_abonnement():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    return "Gerer Les Abonnements"

@app.route('/Locations')
def locations():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    return "Locations"

@app.route('/Equipement')
def equipement():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    return "Equipement"

@app.route('/logout')
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "success")
    return redirect(url_for('login'))


@app.route('/stats/payment-types')
def payment_types_stats():
    data = db.session.query(
        Paiement.type_reglement,
        func.sum(Paiement.montant_paye)
    ).group_by(Paiement.type_reglement).all()
    
    labels = [result[0] or 'Non spécifié' for result in data]
    values = [float(result[1]) for result in data]
    
    return jsonify({
        'labels': labels,
        'values': values
    })

@app.route('/stats/saisons')
def saison_stats():
    data = db.session.query(
        Paiement.code_saison,
        func.sum(Paiement.montant_paye)
    ).group_by(Paiement.code_saison).order_by(Paiement.code_saison).all()
    
    total = sum(float(result[1]) for result in data)
    average = total / len(data) if data else 0
    
    return jsonify({
        'labels': [result[0] for result in data],
        'values': [float(result[1]) for result in data],
        'average': average
    })

@app.route('/stats/payment-status')
def payment_status():
    total_paid = db.session.query(func.sum(Paiement.montant_paye)).scalar() or 0
    # Total restant : récupérer le montant_reste du paiement le plus récent pour chaque adhérent
    subquery = db.session.query(
        Paiement.matricule_adherent,
        func.max(Paiement.id_paiement).label("last_payment_id")
    ).group_by(Paiement.matricule_adherent).subquery()

    total_remaining = db.session.query(
        func.sum(Paiement.montant_reste)
    ).join(subquery, Paiement.id_paiement == subquery.c.last_payment_id).scalar() or 0
    total = total_paid + total_remaining
    
    return jsonify({
        'totalPaid': float(total_paid),
        'totalRemaining': float(total_remaining),
        'paidPercentage': total_paid / total if total else 0
    })

@app.route('/stats/monthly-trend/<int:year>')
def monthly_trend(year):
    data = db.session.query(
        func.extract('month', Paiement.date_paiement),
        func.sum(Paiement.montant_paye)
    ).filter(
        func.extract('year', Paiement.date_paiement) == year
    ).group_by(
        func.extract('month', Paiement.date_paiement)
    ).order_by(
        func.extract('month', Paiement.date_paiement)
    ).all()
    
    months = [int(result[0]) for result in data]
    amounts = [float(result[1]) for result in data]
    
    return jsonify({
        'months': months,
        'amounts': amounts
    })




@app.route('/statistiques')
def statistiques():
    # Calculate paiements by type
    paiements = db.session.query(
        Paiement.type_reglement,
        func.sum(Paiement.montant_paye).label('montant_total')
    ).group_by(Paiement.type_reglement).all()

    types_paiement = [result.type_reglement or 'Non spécifié' for result in paiements]
    montants_paiement = [float(result.montant_total) for result in paiements]

    # Calculate monthly collectes
    collectes = db.session.query(
        func.DATE_FORMAT(Paiement.date_paiement, '%m/%Y').label('date_format'),
        func.sum(Paiement.montant_paye).label('montant_total')
    ).group_by(
        func.DATE_FORMAT(Paiement.date_paiement, '%m/%Y')
    ).order_by(
        func.min(Paiement.date_paiement)
    ).all()

    mois = [result.date_format for result in collectes]
    montants_mois = [float(result.montant_total) for result in collectes]
    return render_template(
        'statistiques.html',
        types_paiement=types_paiement,
        montants_paiement=montants_paiement,
        mois=mois,
        montants_mois=montants_mois
    )


@app.route('/get_bank_percentages', methods=['POST'])
def get_bank_percentages():
    selected_type = request.json.get('type_reglement', 'Non spécifié')
    
    # Gestion correcte des valeurs NULL
    filter_condition = (
        Paiement.type_reglement.is_(None) 
        if selected_type == 'Non spécifié' 
        else Paiement.type_reglement == selected_type
    )

    total = db.session.query(
        func.coalesce(func.sum(Paiement.montant_paye), 0)
    ).filter(filter_condition).scalar()

    bank_data = db.session.query(
        Paiement.banque,
        func.coalesce(func.sum(Paiement.montant_paye), 0).label('montant_total')
    ).filter(filter_condition).group_by(Paiement.banque).all()

    result = []
    for bank in bank_data:
        percentage = (bank.montant_total / total) * 100 if total != 0 else 0
        result.append({
            'banque': bank.banque or 'Non spécifié',
            'montant_total': float(bank.montant_total),
            'percentage': round(percentage, 2)
        })

    return jsonify(result)


@app.route('/stats/top-adherents')
def top_adherents():
    data = db.session.query(
        Paiement.matricule_adherent,
        func.sum(Paiement.montant_paye)
    ).group_by(Paiement.matricule_adherent).order_by(func.sum(Paiement.montant_paye).desc()).limit(10).all()
    
    labels = [result[0] for result in data]
    values = [float(result[1]) for result in data]

    return jsonify({
        'labels': labels,
        'values': values,
        'colors': ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f', '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ac']
    })



class User(db.Model):
    __tablename__ = 'utilisateurs'  # Remplacez 'users' par le nom réel de votre table
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    utilisateur = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<User {self.utilisateur}>"

class Adherent(db.Model):
    __tablename__ = 'adherent'
    
    adherent_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    date_inscription = db.Column(db.Date, nullable=False)
    sexe = db.Column(db.String(1), nullable=False)
    tel1 = db.Column(db.String(15), nullable=True)
    tel2 = db.Column(db.String(15), nullable=True)
    type_abonnement = db.Column(db.String(50), nullable=True)
    categorie = db.Column(db.String(50), nullable=True)
    matricule = db.Column(db.Integer, unique=True, nullable=False)
    groupe = db.Column(db.String(100), nullable=True)
    entraineur = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    paye = db.Column(db.Enum('O', 'N'), nullable=False)
    status = db.Column(db.Enum('Actif', 'Non-Actif'), nullable=False)
    code_saison = db.Column(db.String(10), nullable=True)
    cotisation = db.Column(db.Float, nullable=True)  # Nouveau champ
    remise = db.Column(db.Float, nullable=True)      # Nouveau champ

    def __repr__(self):
        return f'<Adherent {self.nom} {self.prenom}>'

    def to_dict(self):
        return {
            "adherent_id": self.adherent_id,
            "nom": self.nom,
            "prenom": self.prenom,
            "date_naissance": self.date_naissance.isoformat(),
            "date_inscription": self.date_inscription.isoformat(),
            "sexe": self.sexe,
            "tel1": self.tel1,
            "tel2": self.tel2,
            "type_abonnement": self.type_abonnement,
            "categorie": self.categorie,
            "matricule": self.matricule,
            "groupe": self.groupe,
            "entraineur": self.entraineur,
            "email": self.email,
            "paye": self.paye,
            "status": self.status,
            "code_saison": self.code_saison,
            "cotisation": self.cotisation,
            "remise": self.remise
        }

class Entraineur(db.Model):
    __tablename__ = 'entraineur'
    
    id_entraineur = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    sexe = db.Column(db.Enum('M', 'F'), nullable=False)
    role_technique = db.Column(db.String(50), nullable=True)
    type_abonnement = db.Column(db.String(50), nullable=True, default=None)
    tel = db.Column(db.String(100), nullable=True)
    addresse = db.Column(db.String(100), nullable=True)
    compte_bancaire = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Enum('Actif', 'Non-Actif'), nullable=False)
    code_saison = db.Column(db.String(10), nullable=True)
    def __repr__(self):
        return f'<Entraineur {self.nom} {self.prenom}>'



class Groupe(db.Model):
    __tablename__ = 'groupe'
    
    id_groupe = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_groupe = db.Column(db.String(100), nullable=False)
    entraineur_nom = db.Column(db.String(50), nullable=False)
    type_abonnement = db.Column(db.String(50), nullable=False)
    categorie = db.Column(db.String(50), nullable=False)
    preparateur_physique = db.Column(db.String(100), nullable=True)  # Nouvelle colonne
    saison_code = db.Column(db.String(10), nullable=False)  # ex: 'S2025'
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Groupe {self.nom_groupe} géré par {self.entraineur_nom}>'

class Seance(db.Model):
    __tablename__ = 'seances'
    seance_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    groupe = db.Column(db.String(100), nullable=False)
    entraineur = db.Column(db.String(100), nullable=False)
    terrain = db.Column(db.Integer, nullable=True)
    adherents_matricules = db.Column(db.Text, nullable=True)
    type_seance = db.Column(db.String(50), nullable=False, default="entrainement")
    duree = db.Column(db.Integer, nullable=True)  # Durée en minutes
    code_saison = db.Column(db.String(10), nullable=True)  # Ajout du champ manquant

    def __init__(self, date, heure_debut, groupe, entraineur, terrain, heure_fin=None, type_seance="entrainement", duree=None, code_saison=None):
        self.date = date
        self.heure_debut = heure_debut
        self.groupe = groupe
        self.entraineur = entraineur
        self.terrain = terrain
        self.type_seance = type_seance
        self.code_saison = code_saison  # Initialisation du code saison
        
        # Calcul automatique si heure_fin non fournie
        if heure_fin:
            self.heure_fin = heure_fin
            # Calculer la durée en minutes
            debut_dt = datetime.combine(date, heure_debut)
            fin_dt = datetime.combine(date, heure_fin)
            self.duree = int((fin_dt - debut_dt).total_seconds() / 60)
        else:
            # Durée par défaut selon le type
            default_duration = 90 if type_seance == "entrainement" else 60
            self.duree = duree or default_duration
            self.heure_fin = (datetime.combine(date, heure_debut) + 
                            timedelta(minutes=self.duree)).time()
    
class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id_reservation = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_entraineur = db.Column(db.String(100), nullable=False)
    prenom_entraineur = db.Column(db.String(100), nullable=False)
    date_reservation = db.Column(db.Date, nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    numero_terrain = db.Column(db.Integer, nullable=False)
    commentaire = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('en_attente', 'acceptée', 'refusée'), default='en_attente')
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)    

@app.route('/api/mes_reservations', methods=['GET'])
def get_mes_reservations():
    if 'user_id' not in session:
        return jsonify({"error": "Non autorisé"}), 403

    try:
        # Récupérer le nom et prénom de l'entraineur depuis le username
        username = session.get('username')
        nom, prenom = username.split('.')

        # Récupérer les réservations de l'entraineur
        reservations = Reservation.query.filter_by(
            nom_entraineur=nom,
            prenom_entraineur=prenom
        ).order_by(Reservation.date_reservation.desc()).all()

        # Convertir les réservations en format JSON
        reservations_list = []
        for res in reservations:
            reservations_list.append({
                'date': res.date_reservation.strftime('%d/%m/%Y'),
                'heure_debut': res.heure_debut.strftime('%H:%M'),
                'heure_fin': res.heure_fin.strftime('%H:%M'),
                'numero_terrain': res.numero_terrain,
                'status': res.status,
                'commentaire': res.commentaire
            })

        return jsonify({
            "success": True,
            "reservations": reservations_list
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/reserver_terrain', methods=['POST'])
def api_reserver_terrain():
    if 'user_id' not in session:
        return jsonify({"error": "Non autorisé"}), 403

    try:
        data = request.get_json()
        username = session.get('username')
        nom, prenom = username.split('.')  # Assurez-vous que cela correspond à votre format

        nouvelle_reservation = Reservation(
            nom_entraineur=nom,
            prenom_entraineur=prenom,
            date_reservation=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            heure_debut=datetime.strptime(data['heure_debut'], '%H:%M').time(),
            heure_fin=datetime.strptime(data['heure_fin'], '%H:%M').time(),
            numero_terrain=int(data['numero_terrain']),
            commentaire=data.get('commentaire', ''),
            status='en_attente'
        )
        
        db.session.add(nouvelle_reservation)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Réservation créée avec succès"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
@app.route('/api/all_reservations', methods=['GET'])
def get_all_reservations():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"error": "Non autorisé"}), 403

    try:
        reservations = Reservation.query.order_by(
            Reservation.date_creation.desc()
        ).all()

        reservations_list = []
        for res in reservations:
            reservations_list.append({
                'id': res.id_reservation,
                'entraineur': f"{res.nom_entraineur} {res.prenom_entraineur}",
                'date': res.date_reservation.strftime('%d/%m/%Y'),
                'heure_debut': res.heure_debut.strftime('%H:%M'),
                'heure_fin': res.heure_fin.strftime('%H:%M'),
                'numero_terrain': res.numero_terrain,
                'status': res.status,
                'commentaire': res.commentaire,
                'date_creation': res.date_creation.strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify({
            "success": True,
            "reservations": reservations_list
        })

    except Exception as e:
        import traceback
        return jsonify({"error": str(e)}), 400

@app.route('/api/update_reservation_status', methods=['POST'])
def update_reservation_status():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"error": "Non autorisé"}), 403

    try:
        data = request.get_json()
        reservation_id = data.get('reservation_id')
        new_status = data.get('status')

        if not reservation_id or not new_status:
            return jsonify({"error": "Paramètres manquants"}), 400

        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({"error": "Réservation non trouvée"}), 404

        reservation.status = new_status
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Statut mis à jour avec succès : {new_status}"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/reservations')
def reservations():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('login'))
    return render_template('reservations.html')



class LocationTerrain(db.Model):
    __tablename__ = 'locations_terrains'
    id_location = db.Column(db.Integer, primary_key=True)
    numero_terrain = db.Column(db.Integer, nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    date_location = db.Column(db.Date, nullable=False)
    locateur = db.Column(db.String(100), nullable=False)
    montant_location = db.Column(db.Float, nullable=False)


class Message(db.Model):
    __tablename__ = 'messages'
    
    # Définition des colonnes de la table
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Clé primaire auto-incrémentée
    expediteur = db.Column(db.String(255), nullable=False)  # Nom d'utilisateur de l'expéditeur
    destinataires = db.Column(db.String(255), nullable=False)  # Liste des destinataires sous forme de chaîne
    objet = db.Column(db.String(100), nullable=False)  # L'objet du message
    corps = db.Column(db.Text, nullable=False)  # Le contenu du message
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)  # Date d'envoi avec valeur par défaut
    statut = db.Column(db.String(50), default='non lu')  # Statut du message, valeur par défaut 'non lu'

    def __repr__(self):
        return f"<Message {self.objet}>"




class Paiement(db.Model):
    __tablename__ = 'paiements'

    id_paiement = db.Column(db.Integer, primary_key=True)
    matricule_adherent = db.Column(db.String(20), nullable=False)  # Pas de clé étrangère
    date_paiement = db.Column(
        db.DateTime,
        default=lambda: datetime.now(pytz.timezone('Europe/Paris')),  # Utilisez une fonction lambda pour évaluer dynamiquement la date et l'heure
        nullable=False
    )
    montant = db.Column(db.Float, nullable=False)  # Montant total à payer
    montant_paye = db.Column(db.Float, default=0, nullable=False)  # Montant payé dans cette tranche
    total_montant_paye = db.Column(db.Float, default=0, nullable=False)  # Montant payé dans cette tranche
    montant_reste = db.Column(db.Float, nullable=False)  # Montant restant après paiement
    type_reglement = db.Column(db.String(50), nullable=True)  # Espèce, chèque, virement
    numero_cheque = db.Column(db.String(50), nullable=True)  # Facultatif pour les chèques
    banque = db.Column(db.String(50), nullable=True)  # Facultatif pour les chèques
    cotisation = db.Column(db.Float, nullable=False)  # Cotisation totale
    remise = db.Column(db.Float, default=0, nullable=False)  # Remise appliquée (s'il y en a)
    numero_bon = db.Column(db.Integer, nullable=False)  # Numéro de bon
    numero_carnet = db.Column(db.Integer, nullable=False)  # Numéro de carnet
    code_saison = db.Column(db.String(50), nullable=False)  # code de la saison 
    def __repr__(self):
        return f"<Paiement {self.id_paiement} - Matricule: {self.matricule_adherent}>"


class Cotisation(db.Model):
    __tablename__ = 'cotisations'
    id_cotisation = db.Column(db.Integer, primary_key=True)
    nom_cotisation = db.Column(db.String(100), nullable=False, unique=True)
    montant_cotisation = db.Column(db.Float, nullable=False)

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

SAVE_DIR = "static/bons_paiements"  # Assurez-vous que ce dossier existe

import fitz  # PyMuPDF

def generer_bon_paiement(matricule_adherent, montant_paye, type_paiement, code_saison, id_bon, id_carnet):
    """
    Génère un bon de paiement en PDF et en PNG avec les informations de l'adhérent.
    """
    # Récupérer les infos de l'adhérent depuis la base de données
    adherent = Adherent.query.filter_by(matricule=matricule_adherent).first()
    if not adherent:
        return

    nom_complet = f"{adherent.prenom} {adherent.nom}"

    # Définition des chemins
    pdf_filename = os.path.join(SAVE_DIR, f"paiement_{id_bon}.pdf")
    png_filename = os.path.join(SAVE_DIR, f"paiement_{id_bon}.png")

    # Création du PDF
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    # En-tête
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "BON DE PAIEMENT")

    # Numéro du bon et date
    c.setFont("Helvetica", 12)
    c.drawString(400, height - 80, f"Bon n°: {id_bon}")
    c.drawString(400, height - 100, f"Date: {datetime.today().strftime('%d/%m/%Y')}")

    # Informations de l'adhérent
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 140, "Reçu de:")
    c.setFont("Helvetica", 12)
    c.drawString(150, height - 140, f"{nom_complet} (Matricule {matricule_adherent})")

    # Informations de paiement
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 170, "Montant payé:")
    c.setFont("Helvetica", 12)
    c.drawString(200, height - 170, f"{montant_paye:.2f} TND")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 200, "Méthode de paiement:")
    c.setFont("Helvetica", 12)
    c.drawString(250, height - 200, type_paiement)

    # Saison et Carnet
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 230, "Saison:")
    c.setFont("Helvetica", 12)
    c.drawString(150, height - 230, code_saison)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 260, "Carnet n°:")
    c.setFont("Helvetica", 12)
    c.drawString(150, height - 260, str(id_carnet))

    # Signature
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 320, "Reçu par:")
    c.line(150, height - 325, 300, height - 325)  # Ligne de signature

    # Finaliser et enregistrer le PDF
    c.save()

    try:
        # Convertir PDF en PNG avec PyMuPDF
        pdf_document = fitz.open(pdf_filename)
        page = pdf_document[0]
        pix = page.get_pixmap()
        pix.save(png_filename)
        pdf_document.close()
    except Exception as e:
        # En cas d'échec de la conversion PNG, on retourne quand même le PDF
        return pdf_filename, None

    return pdf_filename, png_filename

import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_abonnement(adherent):
    # Créer le dossier "bon_de_recette" s'il n'existe pas
    directory = 'abonnements'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Créer le nom du fichier PDF basé sur le matricule de l'adhérent
    pdf_filename = f"{directory}/{adherent.matricule}.pdf"

    # Créer le fichier PDF avec les informations du bon de recette
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    # Ajouter des informations au PDF
    c.drawString(100, 750, f"Bon de Recette - {adherent.matricule}")
    c.drawString(100, 730, f"Nom : {adherent.nom} {adherent.prenom}")
    c.drawString(100, 710, f"Type d'abonnement : {adherent.type_abonnement}")
    c.drawString(100, 630, f"Date d'échéance : {adherent.date_inscription}")

    # Sauvegarder le PDF
    c.save()

from sqlalchemy.sql import func

def get_totals_simple():
    # Obtenir le dernier paiement de chaque adhérent
    subquery = (
        db.session.query(
            Paiement.matricule_adherent,
            func.max(Paiement.date_paiement).label("latest_payment_date")
        )
        .group_by(Paiement.matricule_adherent)
        .subquery()
    )

    # Calculer les totaux à partir des derniers paiements
    results = (
        db.session.query(
            func.sum(Paiement.montant).label("total_montant"),
            func.sum(Paiement.montant_paye).label("total_montant_paye"),
            func.sum(Paiement.montant_reste).label("total_montant_reste"),
        )
        .join(subquery, (Paiement.matricule_adherent == subquery.c.matricule_adherent) &
                         (Paiement.date_paiement == subquery.c.latest_payment_date))
        .first()
    )

    



@app.route('/recherche-paiements')  
def recherche_paiements():
    return render_template('recherche_paiements.html')

@app.route('/api/search-paiements', methods=['POST'])
def search_paiements():
    matricule = request.json.get('matricule')
    
    if not matricule:
        return jsonify({'error': 'Matricule requis'}), 400
    
    paiements = Paiement.query.filter_by(matricule_adherent=matricule).all()
    
    # Grouper par numéro de bon
    bons = {}
    for p in paiements:
        if p.numero_bon not in bons:
            bons[p.numero_bon] = {
                'total_paye': 0,
                'date': p.date_paiement.strftime('%d/%m/%Y')
            }
        bons[p.numero_bon]['total_paye'] += p.montant_paye
    
    return jsonify({
        'matricule': matricule,
        'bons': bons
    })

@app.route('/api/delete-bon', methods=['DELETE'])
def delete_bon():
    numero_bon = request.json.get('numero_bon')
    if not numero_bon:
        return jsonify({'error': 'Numéro de bon requis'}), 400
    
    try:
        file_path = os.path.join(
             SAVE_DIR, 
            'bons_paiements', 
            f'paiement_'+'{numero_bon}.pdf'
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Fichier non trouvé'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/recherche-abonnements')
def recherche_abonnements():
    return render_template('recherche_abonnements.html')

@app.route('/api/search-abonnements', methods=['POST'])
def search_abonnements():
    matricule = request.json.get('matricule')
    
    if not matricule:
        return jsonify({'error': 'Matricule requis'}), 400
    
    adherents = Adherent.query.filter_by(matricule=matricule).all()
    
    if not adherents:
        return jsonify({'error': 'Aucun adhérent trouvé'}), 404
    
    # Convertir les résultats en JSON
    data = [{
        'id': a.adherent_id,
        'nom': a.nom,
        'prenom': a.prenom,
        'matricule': a.matricule
    } for a in adherents]
    
    return jsonify(data)





from datetime import datetime

class Tournois(db.Model):
    __tablename__ = 'tournois'
    
    id = db.Column(db.Integer, primary_key=True)
    nom_tournoi = db.Column(db.String(100), nullable=False)
    nombre_groupes = db.Column(db.Integer, nullable=False)
    joueurs_par_groupe = db.Column(db.Integer, nullable=False)
    qualifies_par_groupe = db.Column(db.Integer, nullable=False)
    dates_matches = db.Column(db.JSON, nullable=False)
    matches = db.Column(db.JSON, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin = db.Column(db.DateTime, nullable=False)
    matches = db.Column(db.JSON, nullable=False)
    statut = db.Column(db.String(20), default='en_attente')  # en_attente, en_cours, termine

    def update_match_score(self, phase, groupe, match_id, score1, score2):
        matches = self.matches
        if phase == 'groupes':
            if str(match_id) not in matches['phase_groupes'][groupe]['matches']:
                matches['phase_groupes'][groupe]['matches'][str(match_id)] = {
                    'joueur1': None,
                    'joueur2': None,
                    'score1': None,
                    'score2': None,
                    'joue': False
                }
            matches['phase_groupes'][groupe]['matches'][str(match_id)].update({
                'score1': score1,
                'score2': score2,
                'joue': True
            })
        else:
            # Mise à jour des scores pour les phases finales
            phase_matches = matches['phase_finale'][phase]
            for match in phase_matches:
                if match['id'] == match_id:
                    match.update({
                        'score1': score1,
                        'score2': score2,
                        'joue': True
                    })
                    break
        
        self.matches = matches
        db.session.commit()

    def __repr__(self):
        return f"<Tournois {self.nom_tournoi}>"


from datetime import datetime

@app.route('/creer-tournoi', methods=['POST'])
def creer_tournoi():
    data = request.get_json()
    
    try:
        # Validation des données
        if int(data['qualifies_par_groupe']) > int(data['joueurs_par_groupe']):
           
            return jsonify({'error': 'Le nombre de qualifiés ne peut pas dépasser le nombre de joueurs par groupe'}), 400
        
        nouveau_tournoi = Tournois(
            nom_tournoi=data['nom_tournoi'],
            nombre_groupes=int(data['nombre_groupes']),
            joueurs_par_groupe=int(data['joueurs_par_groupe']),
            qualifies_par_groupe=int(data['qualifies_par_groupe']),
            date_debut=datetime.fromisoformat(data['date_debut']),
            date_fin=datetime.fromisoformat(data['date_fin']),
            dates_matches=data['dates_matches'],
            matches=generer_structure_tournoi(
                int(data['nombre_groupes']),
                int(data['joueurs_par_groupe']),
                int(data['qualifies_par_groupe'])
            )
        )
        
        db.session.add(nouveau_tournoi)
        db.session.commit()
        return jsonify({'message': 'Tournoi créé avec succès', 'id': nouveau_tournoi.id}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tournois')
def get_tournois():
    tournois = Tournois.query.order_by(Tournois.date_debut.asc()).all()
    return jsonify([{
        'id': t.id,
        'nom': t.nom_tournoi,
        'groupes': t.nombre_groupes,
        'date_debut': t.date_debut.isoformat(),
        'date_fin': t.date_fin.isoformat()
    } for t in tournois])

@app.route('/api/tournois/<int:id>/matches')
def get_matches(id):
    tournoi = Tournois.query.get_or_404(id)
    return jsonify(tournoi.matches)

@app.route('/api/tournois/<int:id>', methods=['DELETE'])
def delete_tournoi(id):
    tournoi = Tournois.query.get_or_404(id)
    db.session.delete(tournoi)
    db.session.commit()
    return jsonify({'message': 'Tournoi supprimé'})

def generer_structure_tournoi(nb_groupes, joueurs_par_groupe, qualifies):
    structure = {
        'phase_groupes': {},
        'phase_finale': {
            'quart': [],
            'demi': [],
            'finale': None
        }
    }
    
    # Génération des groupes
    for i in range(nb_groupes):
        groupe = {
            'nom': f'Groupe {i+1}',
            'participants': [f'Joueur {j+1}' for j in range(joueurs_par_groupe)],
            'qualifies': [f'Joueur {q+1}' for q in range(qualifies)]
        }
        structure['phase_groupes'][f'groupe_{i+1}'] = groupe
    
    # Génération des matches de phase finale
    total_qualifies = nb_groupes * qualifies
    structure['phase_finale']['quart'] = [{
        'match': f'Quart {i+1}',
        'joueurs': []
    } for i in range(total_qualifies // 2)]
    
    return structure

@app.route('/api/tournois/<int:id>/update-match', methods=['POST'])
def update_match_score(id):
    data = request.get_json()
    tournoi = Tournois.query.get_or_404(id)
    
    try:
        tournoi.update_match_score(
            phase=data['phase'],
            groupe=data.get('groupe'),  # None pour les phases finales
            match_id=data['match_id'],
            score1=data['score1'],
            score2=data['score2']
        )
        return jsonify({'message': 'Score mis à jour avec succès'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/tournois/<int:id>/status', methods=['PUT'])
def update_tournament_status(id):
    tournoi = Tournois.query.get_or_404(id)
    data = request.get_json()
    
    if data['status'] in ['en_attente', 'en_cours', 'termine']:
        tournoi.statut = data['status']
        db.session.commit()
        return jsonify({'message': 'Statut mis à jour'})
    
    return jsonify({'error': 'Statut invalide'}), 400

@app.route('/tournois')  
def tournois():
    return render_template('tournois.html')
from flask import render_template, jsonify, request, flash, redirect, url_for
from datetime import datetime, timedelta, time

@app.route('/calendrier')
def calendrier():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder au calendrier.', 'danger')
        return redirect(url_for('login'))

    current_date = request.args.get('date')
    
    if current_date:
        current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
    else:
        current_date = datetime.now().date()

    # Créer les créneaux horaires de 6h à 22h
    heures = []
    current_time = time(6, 0)
    end_time = time(22, 0)
    
    while current_time <= end_time:
        heures.append(current_time)
        current_time = (datetime.combine(datetime.min, current_time) + 
                       timedelta(hours=1)).time()

    # Récupérer les séances
    seances = Seance.query.filter(
        Seance.date == current_date
    ).order_by(Seance.heure_debut).all()

    # Calculer la largeur des séances en fonction de leur durée
    seances_info = {}
    for seance in seances:
        debut = seance.heure_debut
        fin = (datetime.combine(current_date, debut) + timedelta(minutes=90)).time()
        
        # Calculer combien de colonnes la séance doit occuper
        colonnes = 1.5  # Pour 1h30
        
        seances_info[seance.seance_id] = {
            'seance': seance,
            'debut': debut,
            'fin': fin,
            'colonnes': colonnes
        }

    # Navigation des dates
    prev_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')

    return render_template('calendrier.html',
                         datetime=datetime,
                         timedelta=timedelta,
                         current_date=current_date,
                         prev_date=prev_date,
                         next_date=next_date,
                         heures=heures,
                         seances=seances,
                         seances_info=seances_info)

@app.route('/api/seance/<int:seance_id>')
def get_seance_details(seance_id):
    seance = Seance.query.get_or_404(seance_id)
    adherents = Adherent.query.filter_by(groupe=seance.groupe).all()
    
    return jsonify({
        'id': seance.seance_id,
        'groupe': seance.groupe,
        'entraineur': seance.entraineur,
        'terrain': seance.terrain,
        'heure_debut': seance.heure_debut.strftime('%H:%M'),
        'heure_fin': (datetime.combine(datetime.today(), seance.heure_debut) + 
                     timedelta(minutes=90)).time().strftime('%H:%M'),
        'nombre_adherents': len(adherents),
        'adherents': [{'nom': a.nom, 'prenom': a.prenom} for a in adherents]
    })


import os
from werkzeug.utils import secure_filename
# In your app configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autres-paiements')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper function to ensure folder exists
def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


class AutresPaiements(db.Model):
    __tablename__ = 'autres_paiements'
    id = db.Column(db.Integer, primary_key=True)
    nom_paiement = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    montant = db.Column(db.Float, nullable=False)
    type_reglement = db.Column(db.String(50), nullable=False)  # 'espèce', 'chèque', 'virement'
    banque = db.Column(db.String(255), nullable=True)          # seulement si chèque
    numero_bon = db.Column(db.Integer, nullable=False)
    numero_carnet = db.Column(db.Integer, nullable=False)
    code_saison = db.Column(db.String(10), nullable=False)     # ex: S2025 ou E2025
    date_paiement = db.Column(db.DateTime, default=datetime.now)

@app.route('/autres_paiements', methods=['GET', 'POST'])
def autres_paiements():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    current_year = datetime.now().year
    paiements = []
    numero_carnet = 1
    numero_bon = 1
    code_saison = f"S{current_year}"  # par défaut

    # Récupérer paiements existants pour affichage
    paiements = AutresPaiements.query.order_by(AutresPaiements.id.asc()).all()
    
    # Calcul du dernier carnet/bon
    dernier_paiement = AutresPaiements.query.order_by(AutresPaiements.id.desc()).first()
    if dernier_paiement:
        numero_carnet = dernier_paiement.numero_carnet
        numero_bon = dernier_paiement.numero_bon + 1
        if numero_bon > 50:
            numero_carnet += 1
            numero_bon = 1

    if request.method == 'POST':
        nom_paiement = request.form.get('nom_paiement')
        description = request.form.get('description')
        try:
            montant = float(request.form.get('montant', 0))
        except ValueError:
            montant = 0.0
        type_reglement = request.form.get('type_reglement')
        banque = request.form.get('banque') if type_reglement == 'chèque' else None

        saison_type = request.form.get('saison_type')
        annee_saison = int(request.form.get('annee_saison', current_year))
        code_saison = f"E{annee_saison}" if saison_type == 'ete' else f"S{annee_saison}"

        nouveau_paiement = AutresPaiements(
            nom_paiement=nom_paiement,
            description=description,
            montant=montant,
            type_reglement=type_reglement,
            banque=banque,
            numero_bon=numero_bon,
            numero_carnet=numero_carnet,
            code_saison=code_saison
        )
        db.session.add(nouveau_paiement)
        db.session.commit()

        flash("Paiement ajouté avec succès.", "success")
        return redirect(url_for('autres_paiements'))

    return render_template(
        'autres_paiements.html',
        paiements=paiements,
        numero_bon=numero_bon,
        numero_carnet=numero_carnet,
        code_saison=code_saison,
        current_year=current_year
    )


@app.route('/api/autres-paiements', methods=['GET'])
def get_autres_paiements():
    query = AutresPaiements.query

    category = request.args.get('category', 'all')
    if category != 'all':
        query = query.filter(AutresPaiements.category == category)
    
    date_filter = request.args.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(AutresPaiements.date == filter_date)
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

    transactions = query.order_by(AutresPaiements.date.desc()).all()
    return jsonify([transaction.to_dict() for transaction in transactions])

@app.route('/api/autres-paiements', methods=['POST'])
def add_autre_paiement():
    try:
        # Create data dictionary from form data
        data = {
            'amount': float(request.form['amount']),
            'category': request.form['category'],
            'date': request.form['date'],
            'description': request.form['description'],
            'company_name': request.form['company_name'],
            'bank_name': request.form['bank_name'],
            'rib': request.form.get('rib'),
            'location': request.form.get('location')
        }

        new_transaction = AutresPaiements.from_dict(data)
        db.session.add(new_transaction)
        db.session.flush()

        # Handle file uploads
        if 'documents' in request.files:
            files = request.files.getlist('documents')
            saved_files = []

            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], f'folder-{new_transaction.id}')
            ensure_folder_exists(folder_path)

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(folder_path, filename)
                    file.save(file_path)
                    saved_files.append(filename)

            new_transaction.documents = saved_files

        db.session.commit()
        return jsonify(new_transaction.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/autres-paiements/summary', methods=['GET'])
def get_summary():
    try:
        total_expenses = db.session.query(
            db.func.coalesce(db.func.sum(AutresPaiements.amount), 0.0)
        ).scalar()
        
        return jsonify({
            'expenses': float(total_expenses)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/autres-paiements/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        transaction = AutresPaiements.query.get_or_404(transaction_id)
        
        # Delete associated documents
        folder_path = os.path.join(UPLOAD_FOLDER, f'folder-{transaction_id}')
        if os.path.exists(folder_path):
            for filename in transaction.documents or []:
                file_path = os.path.join(folder_path, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            os.rmdir(folder_path)
        
        db.session.delete(transaction)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/autres-paiements/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    try:
        transaction = AutresPaiements.query.get_or_404(transaction_id)
        data = request.form.to_dict()
        files = request.files.getlist('documents')
        
        # Update basic fields
        transaction.amount = float(data['amount'])
        transaction.category = data['category']
        transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        transaction.description = data['description']
        transaction.company_name = data['company_name']
        transaction.bank_name = data['bank_name']
        transaction.rib = data.get('rib')
        transaction.location = data.get('location')
        
        # Handle new documents
        if files:
            folder_path = os.path.join(UPLOAD_FOLDER, f'folder-{transaction_id}')
            ensure_folder_exists(folder_path)
            
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(folder_path, filename)
                    file.save(file_path)
                    if transaction.documents is None:
                        transaction.documents = []
                    transaction.documents.append(filename)
        
        db.session.commit()
        return jsonify(transaction.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/autres-paiements/<int:transaction_id>/documents/<path:filename>')
def get_document(transaction_id, filename):
    try:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], f'folder-{transaction_id}')
        if not os.path.exists(folder_path):
            return jsonify({'error': 'Document folder not found'}), 404
            
        # Use safe_join to prevent directory traversal attacks
        from werkzeug.utils import safe_join
        safe_path = safe_join(folder_path, filename)
        
        if not os.path.exists(safe_path):
            return jsonify({'error': 'Document not found'}), 404
            
        return send_from_directory(folder_path, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': 'Error serving document'}), 500







from flask import Flask, jsonify, render_template, request
from sqlalchemy import or_
from datetime import datetime
import pytz


@app.route('/situation-adherent')
def show_situation_adherent():
    return render_template('situation-adherent.html')



@app.route('/ajouter_adherents_groupe/<int:groupe_id>', methods=['POST'])
def ajouter_adherents_groupe(groupe_id):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        return jsonify({"error": "Accès non autorisé"}), 403
    
    try:
        current_season_code = session.get('saison_code')
        if not current_season_code:
            return jsonify({"error": "Aucune saison sélectionnée"}), 400
        
        data = request.get_json()
        matricules = data.get('matricules', [])
        
        if not matricules:
            return jsonify({"error": "Aucun matricule fourni"}), 400
        
        groupe = Groupe.query.get_or_404(groupe_id)
        
        # Récupérer la cotisation associée au groupe
        cotisation_groupe = Cotisation.query.filter_by(
            nom_cotisation=groupe.nom_groupe
        ).first()
        
        added_count = 0
        
        for matricule in matricules:
            adherent = Adherent.query.filter_by(
                matricule=matricule,
                code_saison=current_season_code,
                status='Actif'
            ).first()
            
            if adherent:
                # Vérifier qu'il n'est pas déjà dans un autre groupe
                if adherent.groupe and adherent.groupe != groupe.nom_groupe:
                    print(f"Adhérent {matricule} déjà dans le groupe {adherent.groupe}")
                    continue
                
                # Affecter le groupe, l'entraîneur ET la cotisation
                adherent.groupe = groupe.nom_groupe
                adherent.entraineur = groupe.entraineur_nom
                
                # Définir la cotisation depuis le groupe
                if cotisation_groupe:
                    adherent.cotisation = cotisation_groupe.montant_cotisation
                    print(f"Cotisation {cotisation_groupe.montant_cotisation} affectée à {matricule}")
                else:
                    # Cotisation par défaut si pas trouvée
                    adherent.cotisation = 0
                    print(f"Aucune cotisation trouvée pour le groupe {groupe.nom_groupe}")
                
                # La remise sera définie lors du premier paiement
                if adherent.remise is None:
                    adherent.remise = 0
                
                added_count += 1
                print(f"Adhérent {matricule} ajouté au groupe {groupe.nom_groupe}")
            else:
                print(f"Adhérent {matricule} non trouvé pour la saison {current_season_code}")
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "added_count": added_count,
            "saison_code": current_season_code
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400


@app.route('/api/search-adherent')
def search_adherent():
    search_term = request.args.get('term', '')
    if not search_term:
        return jsonify([])
    
    # Récupérer le code saison de la session
    current_season_code = session.get('saison_code')
    if not current_season_code:
        return jsonify({'error': 'Aucune saison sélectionnée'}), 400
    
    print(f"Recherche adhérent: '{search_term}' pour la saison: {current_season_code}")
    
    # Rechercher avec filtre de saison
    adherents = Adherent.query.filter(
        and_(
            Adherent.code_saison == current_season_code,
            Adherent.status == 'Actif',
            or_(
                Adherent.matricule.cast(db.String).like(f'%{search_term}%'),
                Adherent.nom.ilike(f'%{search_term}%'),
                Adherent.prenom.ilike(f'%{search_term}%')
            )
        )
    ).order_by(Adherent.nom, Adherent.prenom).limit(10).all()
    
    print(f"Adhérents trouvés: {len(adherents)}")
    
    return jsonify([{
        'id': a.adherent_id,
        'matricule': a.matricule,
        'nom': a.nom,
        'prenom': a.prenom,
        'label': f"{a.matricule} - {a.nom} {a.prenom}",
        'code_saison': a.code_saison
    } for a in adherents])

@app.route('/api/situation-adherent/<int:matricule>')
@season_required
def get_situation_adherent(matricule):
    # Get current season information
    current_season_code = session.get('saison_code')
    if not current_season_code:
        return jsonify({'error': 'Aucune saison sélectionnée'}), 400

    # Create season contexts
    adherent_season = SeasonContext(Adherent)
    payment_season = SeasonContext(Paiement)
    presence_season = SeasonContext(Presence)
    
    # Get adherent with season filter
    adherent = adherent_season.filter_query(
        Adherent.query.filter_by(matricule=matricule)
    ).first_or_404()
    
    # Get payments for current season
    paiements = payment_season.filter_query(
        Paiement.query.filter_by(
            matricule_adherent=str(matricule),
            code_saison=current_season_code
        )
    ).order_by(Paiement.date_paiement).all()
    
    if paiements:
        dernier_paiement = paiements[-1]
        cotisation_brute = dernier_paiement.cotisation or 0
        remise_pourcentage = dernier_paiement.remise or 0
        code_saison = dernier_paiement.code_saison
    else:
        cotisation_brute = adherent.cotisation or 0
        remise_pourcentage = adherent.remise or 0
        code_saison = current_season_code

    # Calculate financials
    remise_montant = cotisation_brute * (remise_pourcentage / 100)
    cotisation_apres_remise = cotisation_brute - remise_montant
    total_paye = sum(float(p.montant_paye or 0) for p in paiements)
    reste_a_payer = round(max(0.0, cotisation_apres_remise - total_paye), 2)

    # Get presences for current season
    presences = presence_season.filter_query(
        Presence.query.filter(
            Presence.adherent_matricule == str(matricule)
        )
    ).all()
    nombre_presences = sum(1 for p in presences if p.est_present == 'O')

    # Get next session
    now = datetime.now(pytz.timezone('Europe/Paris'))
    prochaine_seance = presence_season.filter_query(
        Presence.query.filter(
            Presence.adherent_matricule == str(matricule),
            Presence.date_seance >= now.date()
        )
    ).order_by(Presence.date_seance, Presence.heure_debut).first()

    # Payment history for current season
    historique_paiements = [{
        'date': p.date_paiement.strftime('%d/%m/%Y') if p.date_paiement else 'N/D',
        'code_saison': p.code_saison,
        'numero_carnet': str(p.numero_carnet) if p.numero_carnet else '-',
        'numero_bon': str(p.numero_bon) if p.numero_bon else '-',
        'montant_paye': float(p.montant_paye or 0),
        'type_reglement': p.type_reglement if p.type_reglement and p.type_reglement != 'NULL' else 'Espèce',
        'numero_cheque': p.numero_cheque if p.numero_cheque and p.numero_cheque != 'NULL' else '-',
        'banque': p.banque if p.banque and p.banque != 'NULL' else '-'
    } for p in paiements]

    # Update adherent data
    adherent_data = adherent.to_dict()
    adherent_data.update({
        'cotisation': round(cotisation_apres_remise, 2),
        'remise': remise_pourcentage,
        'remise_montant': round(remise_montant, 2),
        'code_saison': code_saison,
        'date_inscription': adherent_data.get('date_inscription', 'N/D')
    })

    return jsonify({
        'adherent': adherent_data,
        'paiements': {
            'total_paye': round(total_paye, 2),
            'total_a_payer': round(cotisation_apres_remise, 2),
            'total_remise': remise_pourcentage,
            'remise_montant': round(remise_montant, 2),
            'reste_a_payer': reste_a_payer,
            'historique': historique_paiements
        },
        'presences': {
            'total': len(presences),
            'present': nombre_presences,
            'absent': len(presences) - nombre_presences
        },
        'prochaine_seance': {
            'date': prochaine_seance.date_seance.strftime('%d/%m/%Y') if prochaine_seance else None,
            'heure': prochaine_seance.heure_debut.strftime('%H:%M') if prochaine_seance else None,
            'groupe': prochaine_seance.groupe_nom if prochaine_seance else None
        } if prochaine_seance else None,
        'saison_code': current_season_code,
        'saison_type': session.get('saison_type'),
        'saison_year': session.get('saison')
    })


@app.route('/situation-paiement')
def show_situation_paiement():
    if 'user_id' not in session:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    return render_template('situation-paiement.html')

from flask import jsonify, render_template, request
from sqlalchemy import func, distinct, case
from datetime import datetime, timedelta
import pytz

@app.route('/api/situation-paiement/summary')
@season_required
def get_paiement_summary():
    try:
        # Get current season information
        current_season_code = session.get('saison_code')
        if not current_season_code:
            return jsonify({'error': 'Aucune saison sélectionnée'}), 400

        # Create season context
        payment_season = SeasonContext(Paiement)
        
        date_start = request.args.get('start_date', datetime.now().replace(day=1).strftime('%Y-%m-%d'))
        date_end = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        start_date = datetime.strptime(date_start, '%Y-%m-%d')
        end_date = datetime.strptime(date_end, '%Y-%m-%d')

        # Total payé with season filter
        total_paye = db.session.query(
            func.sum(Paiement.montant_paye).label('total_paye')
        ).filter(
            and_(
                Paiement.date_paiement.between(start_date, end_date + timedelta(days=1)),
                Paiement.code_saison == current_season_code
            )
        ).scalar() or 0

        # Last transaction subquery with season filter
        subquery = db.session.query(
            Paiement.matricule_adherent,
            func.max(Paiement.date_paiement).label('derniere_date')
        ).filter(
            and_(
                Paiement.date_paiement.between(start_date, end_date + timedelta(days=1)),
                Paiement.code_saison == current_season_code
            )
        ).group_by(Paiement.matricule_adherent).subquery()

        # Get latest transactions with remaining amounts
        dernieres_transactions = db.session.query(
            Paiement.matricule_adherent,
            (Paiement.montant - Paiement.montant_paye).label('reste_individuel')
        ).join(
            subquery, 
            and_(
                Paiement.matricule_adherent == subquery.c.matricule_adherent,
                Paiement.date_paiement == subquery.c.derniere_date,
                Paiement.code_saison == current_season_code
            )
        ).all()

        reste_a_payer_total = sum(float(t.reste_individuel or 0) for t in dernieres_transactions)

        # Total à payer with season filter
        total_a_payer = db.session.query(
            func.sum(Paiement.montant).label('total_a_payer')
        ).filter(
            and_(
                Paiement.date_paiement.between(start_date, end_date + timedelta(days=1)),
                Paiement.code_saison == current_season_code
            )
        ).scalar() or 0

        # First transactions subquery with season filter
        premieres_transactions = db.session.query(
            Paiement.matricule_adherent,
            func.min(Paiement.date_paiement).label('premiere_date')
        ).filter(
            and_(
                Paiement.date_paiement.between(start_date, end_date + timedelta(days=1)),
                Paiement.code_saison == current_season_code
            )
        ).group_by(Paiement.matricule_adherent).subquery()

        # Get remises data
        remises_data = db.session.query(
            Paiement.cotisation,
            Paiement.remise
        ).join(
            premieres_transactions,
            and_(
                Paiement.matricule_adherent == premieres_transactions.c.matricule_adherent,
                Paiement.date_paiement == premieres_transactions.c.premiere_date,
                Paiement.code_saison == current_season_code
            )
        ).all()

        total_remise = sum((float(r.cotisation or 0) * float(r.remise or 0) / 100.0) for r in remises_data)

        return jsonify({
            'summary': {
                'total_a_payer': float(total_a_payer),
                'total_paye': float(total_paye),
                'total_remise': float(total_remise),
                'reste_a_payer': float(reste_a_payer_total)
            },
            'saison_code': current_season_code,
            'saison_type': session.get('saison_type'),
            'saison_year': session.get('saison')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/situation-paiement/transactions')
@season_required
def get_paiement_transactions():
    try:
        # Get current season information
        current_season_code = session.get('saison_code')
        if not current_season_code:
            return jsonify({'error': 'Aucune saison sélectionnée'}), 400

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        date_start = request.args.get('start_date')
        date_end = request.args.get('end_date')
        search_term = request.args.get('search', '')

        # Base query with season filter
        query = db.session.query(Paiement, Adherent).join(
            Adherent, Paiement.matricule_adherent == Adherent.matricule
        ).filter(Paiement.code_saison == current_season_code)

        if date_start and date_end:
            start_date = datetime.strptime(date_start, '%Y-%m-%d')
            end_date = datetime.strptime(date_end, '%Y-%m-%d')
            query = query.filter(Paiement.date_paiement.between(start_date, end_date + timedelta(days=1)))

        if search_term:
            query = query.filter(
                or_(
                    Paiement.matricule_adherent.ilike(f'%{search_term}%'),
                    Paiement.type_reglement.ilike(f'%{search_term}%'),
                    Paiement.banque.ilike(f'%{search_term}%'),
                    Adherent.nom.ilike(f'%{search_term}%'),
                    Adherent.prenom.ilike(f'%{search_term}%')
                )
            )

        total_count = query.count()
        transactions = query.order_by(Paiement.date_paiement.desc())\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()

        results = []
        for paiement, adherent in transactions:
            # Get first payment of the season
            premier_paiement = db.session.query(Paiement).filter(
                and_(
                    Paiement.matricule_adherent == paiement.matricule_adherent,
                    Paiement.code_saison == current_season_code
                )
            ).order_by(Paiement.date_paiement.asc()).first()
            
            montant_remise = (float(premier_paiement.cotisation or 0) * float(premier_paiement.remise or 0) / 100.0) if premier_paiement else 0
            is_first_payment = (premier_paiement.id_paiement == paiement.id_paiement) if premier_paiement else False

            results.append({
                'id': paiement.id_paiement,
                'matricule': paiement.matricule_adherent,
                'nom': adherent.nom,
                'prenom': adherent.prenom,
                'date': paiement.date_paiement.strftime('%Y-%m-%d %H:%M:%S'),
                'montant': float(paiement.montant or 0),
                'montant_paye': float(paiement.montant_paye or 0),
                'montant_reste': float((paiement.montant or 0) - (paiement.montant_paye or 0)),
                'type_reglement': paiement.type_reglement,
                'numero_cheque': paiement.numero_cheque,
                'banque': paiement.banque,
                'remise': float(paiement.remise or 0),
                'montant_remise': float(montant_remise),
                'cotisation': float(paiement.cotisation or 0),
                'numero_bon': paiement.numero_bon,
                'numero_carnet': paiement.numero_carnet,
                'is_first_payment': is_first_payment,
                'code_saison': paiement.code_saison
            })

        return jsonify({
            'total': total_count,
            'pages': (total_count + per_page - 1) // per_page,
            'current_page': page,
            'transactions': results,
            'saison_code': current_season_code,
            'saison_type': session.get('saison_type'),
            'saison_year': session.get('saison')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
from sqlalchemy import text, literal

@app.route('/situation-terrains')
def show_situation_terrains():
    if 'user_id' not in session:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    return render_template('situation-terrains.html')



@app.route('/api/terrains/disponibilite')
@season_required
def check_terrain_availability():
    try:
        # Récupérer la saison active de la session
        year = session.get('saison')
        season_type = session.get('saison_type')
        print(f"Session - Year: {year}, Type: {season_type}")
        
        if not year:
            return jsonify({'error': 'Aucune saison sélectionnée'}), 400

        # Obtenir les dates de la saison active
        from filter_functions import get_active_season_dates
        season_dates = get_active_season_dates(year)
        
        if season_type == 'S':
            date_debut_saison = season_dates['normal']['start'].date()
            date_fin_saison = season_dates['normal']['end'].date()
        elif season_type == 'E':
            date_debut_saison = season_dates['summer']['start'].date()
            date_fin_saison = season_dates['summer']['end'].date()
        else:
            # Pour 'all', utiliser la plage complète
            date_debut_saison = season_dates['normal']['start'].date()
            date_fin_saison = season_dates['summer']['end'].date()

        date_str = request.args.get('date')
        heure_debut_str = request.args.get('heure_debut')
        heure_fin_str = request.args.get('heure_fin')

        if not date_str or not heure_debut_str:
            return jsonify({'error': 'Date et heure de début requises'}), 400

        date_check = datetime.strptime(date_str, '%Y-%m-%d').date()
        heure_debut = datetime.strptime(heure_debut_str, '%H:%M').time()
        heure_fin = datetime.strptime(heure_fin_str, '%H:%M').time() if heure_fin_str else None

        print(f"Recherche - Date: {date_check}, Heure début: {heure_debut}, Heure fin: {heure_fin}")
        print(f"Plage saison: {date_debut_saison} à {date_fin_saison}")

        # Vérifier si la date est dans la saison
        if date_check < date_debut_saison or date_check > date_fin_saison:
            return jsonify({'error': f'Date hors saison active ({date_debut_saison} à {date_fin_saison})'}), 400

        terrains_status = []
        for terrain_num in range(1, 10):
            # Check locations - filtrer par date uniquement (pas de code_saison)
            locations_query = LocationTerrain.query.filter(
                LocationTerrain.numero_terrain == terrain_num,
                LocationTerrain.date_location == date_check
            )
            locations = locations_query.all()
            print(f"Terrain {terrain_num} - Locations trouvées: {len(locations)}")

            location_conflict = False
            if heure_fin:
                location_conflict = any(
                    (loc.heure_debut <= heure_debut < loc.heure_fin) or
                    (loc.heure_debut < heure_fin <= loc.heure_fin) or
                    (heure_debut <= loc.heure_debut and heure_fin >= loc.heure_fin)
                    for loc in locations
                )
            else:
                location_conflict = any(
                    (loc.heure_debut <= heure_debut < loc.heure_fin)
                    for loc in locations
                )

            # Check sessions - filtrer par date uniquement (pas de code_saison)
            seances_query = Seance.query.filter(
                Seance.terrain == terrain_num,
                Seance.date == date_check
            )
            seances = seances_query.all()
            print(f"Terrain {terrain_num} - Séances trouvées: {len(seances)}")

            seance_conflict = False
            if heure_fin:
                seance_conflict = any(
                    (seance.heure_debut <= heure_debut < seance.heure_fin) or
                    (seance.heure_debut < heure_fin <= seance.heure_fin) or
                    (heure_debut <= seance.heure_debut and heure_fin >= seance.heure_fin)
                    for seance in seances
                )
            else:
                seance_conflict = any(
                    (seance.heure_debut <= heure_debut < seance.heure_fin)
                    for seance in seances
                )

            terrain_status = {
                'numero': terrain_num,
                'disponible': not (location_conflict or seance_conflict),
                'occupation': None
            }

            # Trouver le conflit spécifique
            if location_conflict:
                for loc in locations:
                    if (loc.heure_debut <= heure_debut < loc.heure_fin) or \
                       (heure_fin and (loc.heure_debut < heure_fin <= loc.heure_fin)) or \
                       (heure_fin and (heure_debut <= loc.heure_debut and heure_fin >= loc.heure_fin)):
                        terrain_status['occupation'] = {
                            'type': 'location',
                            'heure_debut': loc.heure_debut.strftime('%H:%M'),
                            'heure_fin': loc.heure_fin.strftime('%H:%M'),
                            'locateur': loc.locateur
                        }
                        break
            elif seance_conflict:
                for seance in seances:
                    if (seance.heure_debut <= heure_debut < seance.heure_fin) or \
                       (heure_fin and (seance.heure_debut < heure_fin <= seance.heure_fin)) or \
                       (heure_fin and (heure_debut <= seance.heure_debut and heure_fin >= seance.heure_fin)):
                        terrain_status['occupation'] = {
                            'type': 'seance',
                            'heure_debut': seance.heure_debut.strftime('%H:%M'),
                            'heure_fin': seance.heure_fin.strftime('%H:%M'),
                            'groupe': seance.groupe,
                            'entraineur': seance.entraineur
                        }
                        break

            terrains_status.append(terrain_status)

        print(f"Résultats: {terrains_status}")
        return jsonify({
            'terrains': terrains_status,
            'saison_code': f"{season_type}{year}",
            'saison_type': season_type,
            'saison_year': year
        })
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/terrains/stats')
@season_required
def get_terrain_stats():
    try:
        # Récupérer la saison active de la session
        year = session.get('saison')
        season_type = session.get('saison_type')
        
        if not year:
            return jsonify({'error': 'Aucune saison sélectionnée'}), 400

        # Obtenir les dates de la saison active
        from filter_functions import get_active_season_dates
        season_dates = get_active_season_dates(year)
        
        if season_type == 'S':
            date_debut_saison = season_dates['normal']['start'].date()
            date_fin_saison = season_dates['normal']['end'].date()
        elif season_type == 'E':
            date_debut_saison = season_dates['summer']['start'].date()
            date_fin_saison = season_dates['summer']['end'].date()
        else:
            date_debut_saison = season_dates['normal']['start'].date()
            date_fin_saison = season_dates['summer']['end'].date()

        date_start = request.args.get('start_date')
        date_end = request.args.get('end_date')

        # Si pas de dates fournies, utiliser toute la saison
        if not date_start:
            date_start = date_debut_saison.strftime('%Y-%m-%d')
        if not date_end:
            date_end = date_fin_saison.strftime('%Y-%m-%d')

        start_date_obj = datetime.strptime(date_start, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(date_end, '%Y-%m-%d').date()

        # Vérifier que la plage demandée est dans la saison
        if start_date_obj < date_debut_saison or end_date_obj > date_fin_saison:
            return jsonify({'error': f'Plage de dates hors saison active ({date_debut_saison} à {date_fin_saison})'}), 400

        # Location stats - filtrer par plage de dates
        locations_stats = db.session.query(
            LocationTerrain.numero_terrain,
            func.count(LocationTerrain.id_location).label('total_locations'),
            func.sum(LocationTerrain.montant_location).label('total_montant')
        ).filter(
            LocationTerrain.date_location.between(start_date_obj, end_date_obj)
        ).group_by(LocationTerrain.numero_terrain).all()

        # Session stats - filtrer par plage de dates
        seances_stats = db.session.query(
            Seance.terrain,
            func.count(Seance.seance_id).label('total_seances')
        ).filter(
            Seance.date.between(start_date_obj, end_date_obj)
        ).group_by(Seance.terrain).all()

        statistics = {
            terrain_num: {
                'locations': 0,
                'montant_total': 0,
                'seances': 0
            } for terrain_num in range(1, 10)
        }

        for stat in locations_stats:
            statistics[stat.numero_terrain]['locations'] = stat.total_locations
            statistics[stat.numero_terrain]['montant_total'] = float(stat.total_montant or 0)

        for stat in seances_stats:
            if stat.terrain in statistics:
                statistics[stat.terrain]['seances'] = stat.total_seances

        return jsonify({
            'statistics': statistics,
            'period': {
                'start': date_start,
                'end': date_end
            },
            'saison_code': f"{season_type}{year}",
            'saison_type': season_type,
            'saison_year': year
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/terrains/historique')
@season_required
def get_terrain_history():
    try:
        # Récupérer la saison active de la session
        year = session.get('saison')
        season_type = session.get('saison_type')
        
        if not year:
            return jsonify({'error': 'Aucune saison sélectionnée'}), 400

        # Obtenir les dates de la saison active
        from filter_functions import get_active_season_dates
        season_dates = get_active_season_dates(year)
        
        if season_type == 'S':
            date_debut_saison = season_dates['normal']['start'].date()
            date_fin_saison = season_dates['normal']['end'].date()
        elif season_type == 'E':
            date_debut_saison = season_dates['summer']['start'].date()
            date_fin_saison = season_dates['summer']['end'].date()
        else:
            date_debut_saison = season_dates['normal']['start'].date()
            date_fin_saison = season_dates['summer']['end'].date()

        terrain_num = request.args.get('terrain')
        date_start = request.args.get('start_date')
        date_end = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        if not terrain_num:
            return jsonify({'error': 'Numéro de terrain requis'}), 400

        # Si pas de dates fournies, utiliser toute la saison
        if not date_start:
            date_start = date_debut_saison.strftime('%Y-%m-%d')
        if not date_end:
            date_end = date_fin_saison.strftime('%Y-%m-%d')

        start_date_obj = datetime.strptime(date_start, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(date_end, '%Y-%m-%d').date()

        # Vérifier que la plage demandée est dans la saison
        if start_date_obj < date_debut_saison or end_date_obj > date_fin_saison:
            return jsonify({'error': f'Plage de dates hors saison active ({date_debut_saison} à {date_fin_saison})'}), 400

        # Get locations - filtrer par plage de dates
        locations = LocationTerrain.query.filter(
            LocationTerrain.numero_terrain == int(terrain_num),
            LocationTerrain.date_location.between(start_date_obj, end_date_obj)
        ).all()

        # Get sessions - filtrer par plage de dates
        seances = Seance.query.filter(
            Seance.terrain == int(terrain_num),
            Seance.date.between(start_date_obj, end_date_obj)
        ).all()

        historique = []
        
        for loc in locations:
            historique.append({
                'date': loc.date_location.strftime('%Y-%m-%d'),
                'heure_debut': loc.heure_debut.strftime('%H:%M'),
                'heure_fin': loc.heure_fin.strftime('%H:%M'),
                'utilisateur': loc.locateur,
                'montant': float(loc.montant_location or 0),
                'type': 'location'
            })
        
        for seance in seances:
            historique.append({
                'date': seance.date.strftime('%Y-%m-%d'),
                'heure_debut': seance.heure_debut.strftime('%H:%M'),
                'heure_fin': seance.heure_fin.strftime('%H:%M'),
                'utilisateur': seance.groupe,
                'montant': None,
                'type': 'seance'
            })

        historique.sort(key=lambda x: (x['date'], x['heure_debut']), reverse=True)

        total = len(historique)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_historique = historique[start_idx:end_idx]
        
        return jsonify({
            'historique': paginated_historique,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page,
            'saison_code': f"{season_type}{year}",
            'saison_type': season_type,
            'saison_year': year
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/api/marquer_presence/<int:seance_id>', methods=['POST'])
@season_required
def api_marquer_presence(seance_id):
    # Get current season information
    current_season_code = session.get('saison_code')
    if not current_season_code:
        return jsonify({"error": "Aucune saison sélectionnée"}), 400

    data = request.get_json()
    presences = data.get('presences', [])

    # Create season contexts
    seance_season = SeasonContext(Seance)
    presence_season = SeasonContext(Presence)
    trainer_presence_season = SeasonContext(PresenceEntraineur)

    # Retrieve the seance with season filter
    seance = seance_season.filter_query(
        Seance.query.filter_by(seance_id=seance_id)
    ).first()
    
    if not seance:
        return jsonify({"error": "Séance introuvable ou hors saison"}), 404

    try:
        # Mark presence for adherents
        for presence in presences:
            existing_presence = presence_season.filter_query(
                Presence.query.filter_by(
                    groupe_nom=seance.groupe,
                    adherent_matricule=presence['matricule'],
                    date_seance=seance.date,
                    seance_id=seance.seance_id
                )
            ).first()

            if existing_presence:
                existing_presence.est_present = presence['est_present']
            else:
                new_presence = Presence(
                    groupe_nom=seance.groupe,
                    adherent_matricule=presence['matricule'],
                    entraineur_nom=seance.entraineur,
                    date_seance=seance.date,
                    heure_debut=seance.heure_debut,
                    est_present=presence['est_present'],
                    seance_id=seance.seance_id,
                    code_saison=current_season_code  # Add season code
                )
                db.session.add(new_presence)

        # Mark the trainer as present
        existing_trainer_presence = trainer_presence_season.filter_query(
            PresenceEntraineur.query.filter_by(
                groupe_nom=seance.groupe,
                entraineur_nom=seance.entraineur,
                date_seance=seance.date,
                seance_id=seance.seance_id
            )
        ).first()

        if not existing_trainer_presence:
            trainer_presence = PresenceEntraineur(
                groupe_nom=seance.groupe,
                entraineur_nom=seance.entraineur,
                date_seance=seance.date,
                heure_debut=seance.heure_debut,
                est_present='O',
                seance_id=seance.seance_id,
                code_saison=current_season_code  # Add season code
            )
            db.session.add(trainer_presence)

        db.session.commit()
        return jsonify({
            "message": "Présence enregistrée avec succès",
            "saison_code": current_season_code
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"Erreur lors de l'enregistrement des présences : {str(e)}"
        }), 500

@app.route('/presence', methods=['GET', 'POST'])
@season_required
def presence():
    current_season_code = session.get('saison_code')
    if not current_season_code:
        flash("Veuillez sélectionner une saison.", "warning")
        return redirect(url_for('login'))

    try:
        # Groupes et entraineurs : pas de filtre de saison
        groupes = Groupe.query.all()
        entraineurs = Entraineur.query.filter_by(status='Actif').all()
        
        # Adherents : filtrés par saison ET statut actif
        adherents = Adherent.query.filter(
            Adherent.status == 'Actif',
            Adherent.code_saison == current_season_code
        ).order_by(Adherent.nom).all()

        return render_template(
            'presence.html',
            groupes=groupes,
            entraineurs=entraineurs,
            adherents=adherents,
            saison_code=current_season_code,
            saison_type=session.get('saison_type'),
            saison_year=session.get('saison')
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Erreur lors du chargement des données: {str(e)}", "danger")
        return redirect(url_for('admin'))

# Ajoute ces imports en haut de ton fichier si pas déjà présents
from flask import request, jsonify
from sqlalchemy import or_, cast, String


import io
import xlsxwriter
from flask import send_file

@app.route("/export_presence_xlsx")
def export_presence_xlsx():
    search_term = (request.args.get("search_term") or "").strip()
    search_type = (request.args.get("type") or "adherent").strip().lower()

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Présences")

    # Styles
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})
    
    # En-têtes
    if search_type == "adherent":
        headers = ["Matricule", "Nom", "Prénom", "Présent", "Absent", "Dates Présent", "Dates Absent"]
    else:  # entraineur
        headers = ["Nom", "Prénom", "Présent", "Absent", "Dates Présent", "Dates Absent"]

    for col, h in enumerate(headers):
        worksheet.write(0, col, h, header_format)

    # Récupérer les données
    if search_type == "adherent":
        q = Adherent.query
        if search_term:
            like = f"%{search_term}%"
            q = q.filter(or_(
                Adherent.nom.ilike(like),
                Adherent.prenom.ilike(like),
                cast(Adherent.matricule, String).ilike(like)
            ))
        items = q.order_by(Adherent.nom, Adherent.prenom).all()
    else:
        q = Entraineur.query
        if search_term:
            like = f"%{search_term}%"
            q = q.filter(or_(
                Entraineur.nom.ilike(like),
                Entraineur.prenom.ilike(like)
            ))
        items = q.order_by(Entraineur.nom, Entraineur.prenom).all()

    row_num = 1
    for item in items:
        if search_type == "adherent":
            matricule_str = str(item.matricule)
            pres_rows = Presence.query.filter(Presence.adherent_matricule == matricule_str).order_by(Presence.date_seance).all()
            present_dates = ", ".join(p.date_seance.strftime('%Y-%m-%d') for p in pres_rows if p.est_present == 'O')
            absent_dates  = ", ".join(p.date_seance.strftime('%Y-%m-%d') for p in pres_rows if p.est_present == 'N')
            data = [
                item.matricule,
                item.nom,
                item.prenom,
                sum(1 for p in pres_rows if p.est_present == 'O'),
                sum(1 for p in pres_rows if p.est_present == 'N'),
                present_dates,
                absent_dates
            ]
        else:
            full_name = f"{item.nom} {item.prenom}"
            pres_rows = PresenceEntraineur.query.filter(PresenceEntraineur.entraineur_nom == full_name).order_by(PresenceEntraineur.date_seance).all()
            present_dates = ", ".join(p.date_seance.strftime('%Y-%m-%d') for p in pres_rows if p.est_present == 'O')
            absent_dates  = ", ".join(p.date_seance.strftime('%Y-%m-%d') for p in pres_rows if p.est_present == 'N')
            data = [
                item.nom,
                item.prenom,
                sum(1 for p in pres_rows if p.est_present == 'O'),
                sum(1 for p in pres_rows if p.est_present == 'N'),
                present_dates,
                absent_dates
            ]

        for col, val in enumerate(data):
            worksheet.write(row_num, col, val)
        row_num += 1

    workbook.close()
    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"presence_{search_type}.xlsx"
    )


@app.route('/search_presence_situation', methods=['GET', 'POST'])
@season_required
def search_presence_situation():
    # Get current season information
    current_season_code = session.get('saison_code')
    if not current_season_code:
        return jsonify({"error": "Aucune saison sélectionnée"}), 400

    search_term = (request.values.get("search_term") or "").strip()
    search_type = (request.values.get("type") or "adherent").strip().lower()

    # Create season contexts
    adherent_season = SeasonContext(Adherent)
    presence_season = SeasonContext(Presence)
    entraineur_season = SeasonContext(Entraineur)
    trainer_presence_season = SeasonContext(PresenceEntraineur)

    results = []

    # ------ ADHERENTS ------
    if search_type == "adherent":
        # Base query with season filter
        q = adherent_season.filter_query(
            Adherent.query.filter(
                Adherent.code_saison == current_season_code,
                Adherent.status == 'Actif'
            )
        )

        if search_term:
            like = f"%{search_term}%"
            q = q.filter(or_(
                Adherent.nom.ilike(like),
                Adherent.prenom.ilike(like),
                cast(Adherent.matricule, String).ilike(like)
            ))
        
        adherents = q.order_by(Adherent.nom, Adherent.prenom).all()

        for a in adherents:
            matricule_str = str(a.matricule)
            # Get presences with season filter
            pres_rows = presence_season.filter_query(
                Presence.query.filter(
                    Presence.adherent_matricule == matricule_str,
                    Presence.code_saison == current_season_code
                )
            ).order_by(Presence.date_seance).all()

            present_dates = [p.date_seance.strftime('%Y-%m-%d') for p in pres_rows if p.est_present == 'O']
            absent_dates = [p.date_seance.strftime('%Y-%m-%d') for p in pres_rows if p.est_present == 'N']

            results.append({
                "id": a.adherent_id,
                "matricule": a.matricule,
                "nom": a.nom,
                "prenom": a.prenom,
                "nb_present": len(present_dates),
                "nb_absent": len(absent_dates),
                "present_dates": present_dates,
                "absent_dates": absent_dates,
                "saison_code": current_season_code
            })

        return jsonify({
            "results": results,
            "saison_code": current_season_code,
            "saison_type": session.get('saison_type'),
            "saison_year": session.get('saison')
        })

    # ------ ENTRAINEURS ------
    elif search_type == "entraineur":
        q = entraineur_season.filter_query(
            Entraineur.query.filter_by(status='Actif')
        )
        
        if search_term:
            like = f"%{search_term}%"
            q = q.filter(or_(
                Entraineur.nom.ilike(like),
                Entraineur.prenom.ilike(like)
            ))
        
        entraineurs = q.order_by(Entraineur.nom, Entraineur.prenom).all()

        for t in entraineurs:
            full_name = f"{t.nom} {t.prenom}"
            # Get trainer presences with season filter
            pres_rows = trainer_presence_season.filter_query(
                PresenceEntraineur.query.filter(
                    PresenceEntraineur.entraineur_nom == full_name,
                    PresenceEntraineur.code_saison == current_season_code
                )
            ).order_by(PresenceEntraineur.date_seance).all()

            present_dates = [p.date_seance.strftime('%Y-%m-%d') for p in pres_rows if p.est_present == 'O']
            absent_dates = [p.date_seance.strftime('%Y-%m-%d') for p in pres_rows if p.est_present == 'N']

            results.append({
                "id": t.id_entraineur,
                "nom": t.nom,
                "prenom": t.prenom,
                "nb_present": len(present_dates),
                "nb_absent": len(absent_dates),
                "present_dates": present_dates,
                "absent_dates": absent_dates,
                "saison_code": current_season_code
            })

        return jsonify({
            "results": results,
            "saison_code": current_season_code,
            "saison_type": session.get('saison_type'),
            "saison_year": session.get('saison')
        })

    return jsonify({"error": "Type de recherche invalide"}), 400

@app.route('/search_presence', methods=['GET'])
@season_required
def search_presence():
    # Get current season information
    current_season_code = session.get('saison_code')
    if not current_season_code:
        return jsonify({"error": "Aucune saison sélectionnée"}), 400

    search_type = request.args.get('searchType')
    search_value = request.args.get('entraineur') or request.args.get('adherent')

    # Create season contexts
    presence_season = SeasonContext(Presence)
    trainer_presence_season = SeasonContext(PresenceEntraineur)

    results = []

    try:
        if search_type == 'entraineur':
            entraineur = Entraineur.query.filter_by(
                id_entraineur=search_value,
                status='Actif'
            ).first()
            
            if not entraineur:
                return jsonify({"error": "Entraineur non trouvé"}), 404

            search_value = f"{entraineur.nom} {entraineur.prenom}"

            # Query with season filter
            presences = trainer_presence_season.filter_query(
                PresenceEntraineur.query.filter(
                    PresenceEntraineur.entraineur_nom == search_value,
                    PresenceEntraineur.code_saison == current_season_code
                )
            ).order_by(PresenceEntraineur.date_seance.desc()).all()

            results = [{
                'date': presence.date_seance.strftime('%Y-%m-%d'),
                'heure': presence.heure_debut.strftime('%H:%M'),
                'groupe': presence.groupe_nom,
                'entraineur': presence.entraineur_nom,
                'presence': 'Présent' if presence.est_present == 'O' else 'Absent'
            } for presence in presences]

        elif search_type == 'adherent':
            # Query with season filter
            presences = presence_season.filter_query(
                Presence.query.filter(
                    Presence.adherent_matricule == search_value,
                    Presence.code_saison == current_season_code
                )
            ).order_by(Presence.date_seance.desc()).all()

            results = [{
                'date': presence.date_seance.strftime('%Y-%m-%d'),
                'heure': presence.heure_debut.strftime('%H:%M'),
                'groupe': presence.groupe_nom,
                'adherent': presence.adherent_matricule,
                'entraineur': presence.entraineur_nom,
                'presence': 'Présent' if presence.est_present == 'O' else 'Absent'
            } for presence in presences]

        return jsonify({
            "results": results,
            "saison_code": current_season_code,
            "saison_type": session.get('saison_type'),
            "saison_year": session.get('saison')
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


from flask import request, jsonify, send_file
import pandas as pd
from io import BytesIO

@app.route('/export_monthly_presence', methods=['GET'])
def export_monthly_presence():
    month = request.args.get('month')
    type = request.args.get('type')

    if not month or not type:
        return jsonify({"error": "Month and type are required."}), 400

    year, month = map(int, month.split('-'))

    if type == 'adherent':
        # Récupérer toutes les séances du mois
        seances = Seance.query.filter(
            db.extract('year', Seance.date) == year,
            db.extract('month', Seance.date) == month
        ).all()

        # Récupérer tous les adhérents
        adherents = Adherent.query.all()

        data = []
        for adherent in adherents:
            for seance in seances:
                # Vérifier si une présence existe pour cet adhérent à cette séance
                presence = Presence.query.filter_by(
                    adherent_matricule=adherent.matricule,
                    date_seance=seance.date,
                    heure_debut=seance.heure_debut
                ).first()

                data.append({
                    'Date': seance.date.strftime('%Y-%m-%d'),
                    'Heure': seance.heure_debut.strftime('%H:%M'),
                    'Groupe': seance.groupe_nom,
                    'Adhérent': f"{adherent.nom} {adherent.prenom}",
                    'Entraîneur': seance.entraineur_nom,
                    'Présence': 'Présent' if presence and presence.est_present == 'O' else 'Absent'
                })

    elif type == 'entraineur':
        presences = PresenceEntraineur.query.filter(
            db.extract('year', PresenceEntraineur.date_seance) == year,
            db.extract('month', PresenceEntraineur.date_seance) == month
        ).all()

        data = [{
            'Date': p.date_seance.strftime('%Y-%m-%d'),
            'Heure': p.heure_debut.strftime('%H:%M'),
            'Groupe': p.groupe_nom,
            'Entraîneur': p.entraineur_nom,
            'Présence': 'Présent' if p.est_present == 'O' else 'Absent'
        } for p in presences]

    else:
        return jsonify({"error": "Invalid type."}), 400

    # Export Excel
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Présence Mensuelle')

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=f'presence_{type}_{year}-{month:02d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )



from flask import Blueprint, render_template, send_file, jsonify
from sqlalchemy import extract, func
from io import BytesIO
import pandas as pd
from datetime import datetime





@app.route('/situation_financiere')
@season_required
def situation_financiere():
    # Get current season information
    current_season_code = session.get('saison_code')
    if not current_season_code:
        flash("Veuillez sélectionner une saison.", "warning")
        return redirect(url_for('login'))

    # Create season contexts
    payment_season = SeasonContext(Paiement)
    location_season = SeasonContext(LocationTerrain)

    try:
        # 1. Montant total des locations des terrains par mois
        locations_par_mois = (
            db.session.query(
                extract('year', LocationTerrain.date_location).label('annee'),
                extract('month', LocationTerrain.date_location).label('mois'),
                func.sum(LocationTerrain.montant_location).label('total_location')
            )
            .filter(
                # Filter for current season's date range
                LocationTerrain.date_location.between(
                    datetime(int(current_season_code[1:]), 10, 1) if current_season_code[0] == 'S' else datetime(int(current_season_code[1:]), 7, 1),
                    datetime(int(current_season_code[1:]) + 1, 6, 30) if current_season_code[0] == 'S' else datetime(int(current_season_code[1:]), 9, 30)
                )
            )
            .group_by('annee', 'mois')
            .order_by('annee', 'mois')
            .all()
        )

        # 2. Montant total des locations par terrain (filtered by season)
        locations_par_terrain = (
            db.session.query(
                LocationTerrain.numero_terrain,
                func.sum(LocationTerrain.montant_location).label('total_location')
            )
            .filter(
                LocationTerrain.date_location.between(
                    datetime(int(current_season_code[1:]), 10, 1) if current_season_code[0] == 'S' else datetime(int(current_season_code[1:]), 7, 1),
                    datetime(int(current_season_code[1:]) + 1, 6, 30) if current_season_code[0] == 'S' else datetime(int(current_season_code[1:]), 9, 30)
                )
            )
            .group_by(LocationTerrain.numero_terrain)
            .all()
        )

        # 3. Montant total payé par les adhérents par saison
        paiements_par_saison = (
            db.session.query(
                Paiement.code_saison,
                func.sum(Paiement.montant_paye).label('total_paye')
            )
            .filter(Paiement.code_saison == current_season_code)
            .group_by(Paiement.code_saison)
            .all()
        )

        # 4. Montant total payé par les adhérents par mois (filtered by season)
        paiements_par_mois = (
            db.session.query(
                extract('year', Paiement.date_paiement).label('annee'),
                extract('month', Paiement.date_paiement).label('mois'),
                func.sum(Paiement.montant_paye).label('total_paye')
            )
            .filter(Paiement.code_saison == current_season_code)
            .group_by('annee', 'mois')
            .order_by('annee', 'mois')
            .all()
        )

        # 5-8. Totals for current season
        season_totals = (
            db.session.query(
                func.sum(Paiement.cotisation).label('total_prevu'),
                func.sum(Paiement.montant_paye).label('total_paye'),
                func.sum(Paiement.montant_reste).label('total_restant'),
                func.sum(Paiement.remise).label('total_remise')
            )
            .filter(Paiement.code_saison == current_season_code)
            .first()
        )

        total_prevu = float(season_totals.total_prevu or 0)
        total_paye = float(season_totals.total_paye or 0)
        total_restant = float(season_totals.total_restant or 0)
        total_remise = float(season_totals.total_remise or 0)

        return render_template(
            'situation_financiere.html',
            locations_par_mois=locations_par_mois,
            locations_par_terrain=locations_par_terrain,
            paiements_par_saison=paiements_par_saison,
            paiements_par_mois=paiements_par_mois,
            total_prevu=total_prevu,
            total_paye=total_paye,
            total_restant=total_restant,
            total_remise=total_remise,
            saison_code=current_season_code,
            saison_type=session.get('saison_type'),
            saison_year=session.get('saison')
        )

    except Exception as e:
        flash(f"Erreur lors du chargement des données financières: {str(e)}", "danger")
        return redirect(url_for('admin'))
# --- Export endpoints for XLSX (1 per section) ---

def df_to_xlsx_response(df, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/export_xlsx/locations_par_mois')
def export_xlsx_locations_par_mois():
    data = db.session.query(
        extract('year', LocationTerrain.date_location).label('Année'),
        extract('month', LocationTerrain.date_location).label('Mois'),
        func.sum(LocationTerrain.montant_location).label('Montant total')
    ).group_by('Année', 'Mois').order_by('Année', 'Mois').all()
    df = pd.DataFrame(data, columns=['Année', 'Mois', 'Montant total'])
    return df_to_xlsx_response(df, 'locations_par_mois.xlsx')

@app.route('/export_xlsx/locations_par_terrain')
def export_xlsx_locations_par_terrain():
    data = db.session.query(
        LocationTerrain.numero_terrain,
        func.sum(LocationTerrain.montant_location).label('Montant total')
    ).group_by(LocationTerrain.numero_terrain).all()
    df = pd.DataFrame(data, columns=['Numéro terrain', 'Montant total'])
    return df_to_xlsx_response(df, 'locations_par_terrain.xlsx')

@app.route('/export_xlsx/paiements_par_saison')
def export_xlsx_paiements_par_saison():
    data = db.session.query(
        Paiement.code_saison,
        func.sum(Paiement.montant_paye).label('Montant payé')
    ).group_by(Paiement.code_saison).all()
    df = pd.DataFrame(data, columns=['Code saison', 'Montant payé'])
    return df_to_xlsx_response(df, 'paiements_par_saison.xlsx')

@app.route('/export_xlsx/paiements_par_mois')
def export_xlsx_paiements_par_mois():
    data = db.session.query(
        extract('year', Paiement.date_paiement).label('Année'),
        extract('month', Paiement.date_paiement).label('Mois'),
        func.sum(Paiement.montant_paye).label('Montant payé')
    ).group_by('Année', 'Mois').order_by('Année', 'Mois').all()
    df = pd.DataFrame(data, columns=['Année', 'Mois', 'Montant payé'])
    return df_to_xlsx_response(df, 'paiements_par_mois.xlsx')
@app.route('/export_xlsx/global')
def export_xlsx_global():
    # Export global summary
    total_prevu = db.session.query(func.sum(Paiement.cotisation)).scalar() or 0
    total_paye = db.session.query(func.sum(Paiement.montant_paye)).scalar() or 0
    total_restant = db.session.query(func.sum(Paiement.montant_reste)).scalar() or 0
   
    df = pd.DataFrame([
        {'Label': 'Total prévu', 'Montant': total_prevu},
        {'Label': 'Total payé', 'Montant': total_paye},
        {'Label': 'Total restant', 'Montant': total_restant},
        
    ])
    return df_to_xlsx_response(df, 'synthese_globale.xlsx')





class Depense(db.Model):
    __tablename__ = 'depense'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    libelle = db.Column(db.String(255), nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    type_depense = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Depense {self.libelle} {self.montant}>"



@app.route('/depenses')
def depenses():
    return render_template('depenses.html')

@app.route('/get_depenses', methods=['GET'])
def get_depenses():
    search = request.args.get('search', '')
    query = Depense.query
    if search:
        query = query.filter(Depense.libelle.ilike(f"%{search}%"))
    depenses_list = query.order_by(Depense.date.desc()).all()
    result = []
    for d in depenses_list:
        result.append({
            'id': d.id,
            'libelle': d.libelle,
            'montant': str(d.montant),
            'type_depense': d.type_depense,
            'date': d.date.strftime('%Y-%m-%d')
        })
    return jsonify(result)

@app.route('/add_depenses', methods=['POST'])
def add_depenses():
    libelle = request.form.get('libelle')
    montant = request.form.get('montant')
    date_str = request.form.get('date')
    type_depense = request.form.get('type_depense')
    if not (libelle and montant and date_str and type_depense):
        return jsonify({'status': 'error', 'message': 'Tous les champs sont obligatoires'})
    depense = Depense(
        libelle=libelle,
        montant=montant,
        date=datetime.strptime(date_str, '%Y-%m-%d').date(),
        type_depense=type_depense
    )
    db.session.add(depense)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/delete_depense/<int:id>', methods=['DELETE'])
def delete_depense(id):
    depense = Depense.query.get_or_404(id)
    db.session.delete(depense)
    db.session.commit()
    return jsonify({'status': 'success'})



from flask import request, jsonify, send_file
from sqlalchemy import func, and_, or_, cast, String, extract
from datetime import datetime, timedelta
import io
import pandas as pd
from collections import defaultdict
import xlsxwriter


# Routes API corrigées
from flask import Flask, request, jsonify, send_file
from datetime import datetime, timedelta
import io
import xlsxwriter
from sqlalchemy import and_, or_, func
from collections import defaultdict

# ============================================================================
# FONCTIONS DE RECHERCHE MANQUANTES
# ============================================================================

def search_adherent_presences(start_date, end_date, search_term):
    """
    Recherche les présences des adhérents avec les critères spécifiés
    """
    try:
        # Requête de base pour récupérer les présences d'adhérents
        query = db.session.query(
            Adherent.matricule,
            Adherent.nom,
            Adherent.prenom,
            Presence.date_seance,
            Presence.heure_debut,
            Presence.groupe_nom,
            Presence.entraineur_nom,
            Presence.est_present
        ).join(
            Presence, 
            func.find_in_set(Adherent.matricule, Presence.adherent_matricule) > 0
        ).filter(
            and_(
                Presence.date_seance >= start_date,
                Presence.date_seance <= end_date
            )
        )
        
        # Ajouter le filtre de recherche textuelle si fourni
        if search_term:
            search_pattern = f'%{search_term}%'
            query = query.filter(
                or_(
                    Adherent.nom.like(search_pattern),
                    Adherent.prenom.like(search_pattern),
                    Adherent.matricule.like(search_pattern)
                )
            )
        
        # Exécuter la requête
        results = query.all()
        
        # Organiser les résultats par adhérent
        adherent_dict = defaultdict(lambda: {
            'matricule': '',
            'nom': '',
            'prenom': '',
            'sessions': []
        })
        
        for row in results:
            key = row.matricule
            if not adherent_dict[key]['matricule']:
                adherent_dict[key]['matricule'] = str(row.matricule)
                adherent_dict[key]['nom'] = row.nom
                adherent_dict[key]['prenom'] = row.prenom
            
            adherent_dict[key]['sessions'].append({
                'date_seance': row.date_seance.strftime('%Y-%m-%d'),
                'heure_debut': row.heure_debut.strftime('%H:%M'),
                'groupe_nom': row.groupe_nom,
                'entraineur_nom': row.entraineur_nom,
                'est_present': row.est_present
            })
        
        return list(adherent_dict.values())
        
    except Exception as e:
        return []

def search_entraineur_presences(start_date, end_date, search_term):
    """
    Recherche les présences des entraîneurs
    """
    try:
        # Recherche via les séances et présences
        query = db.session.query(
            Presence.entraineur_nom,
            Presence.date_seance,
            Presence.heure_debut,
            Presence.groupe_nom,
            Presence.est_present
        ).filter(
            and_(
                Presence.date_seance >= start_date,
                Presence.date_seance <= end_date
            )
        )
        
        if search_term:
            search_pattern = f'%{search_term}%'
            query = query.filter(Presence.entraineur_nom.like(search_pattern))
        
        results = query.all()
        
        # Organiser par entraîneur
        entraineur_dict = defaultdict(lambda: {
            'nom': '',
            'sessions': []
        })
        
        for row in results:
            key = row.entraineur_nom
            if not entraineur_dict[key]['nom']:
                entraineur_dict[key]['nom'] = row.entraineur_nom
            
            entraineur_dict[key]['sessions'].append({
                'date_seance': row.date_seance.strftime('%Y-%m-%d'),
                'heure_debut': row.heure_debut.strftime('%H:%M'),
                'groupe_nom': row.groupe_nom,
                'est_present': row.est_present
            })
        
        return list(entraineur_dict.values())
        
    except Exception as e:
        return []

def search_groupe_presences(start_date, end_date, search_term):
    """
    Recherche les présences par groupe
    """
    try:
        query = db.session.query(
            Presence.groupe_nom,
            Presence.date_seance,
            Presence.heure_debut,
            Presence.entraineur_nom,
            Presence.est_present,
            Presence.adherent_matricule,
            Presence.seance_type
        ).filter(
            and_(
                Presence.date_seance >= start_date,
                Presence.date_seance <= end_date
            )
        )
        
        if search_term:
            search_pattern = f'%{search_term}%'
            query = query.filter(Presence.groupe_nom.like(search_pattern))
        
        results = query.all()
        
        # Organiser par groupe
        groupe_dict = defaultdict(lambda: {
            'nom': '',
            'sessions': []
        })
        
        for row in results:
            key = row.groupe_nom
            if not groupe_dict[key]['nom']:
                groupe_dict[key]['nom'] = row.groupe_nom
            
            # Compter le nombre de participants pour cette session
            nb_participants = len(row.adherent_matricule.split(',')) if row.adherent_matricule else 0
            
            groupe_dict[key]['sessions'].append({
                'date_seance': row.date_seance.strftime('%Y-%m-%d'),
                'heure_debut': row.heure_debut.strftime('%H:%M'),
                'entraineur_nom': row.entraineur_nom,
                'est_present': row.est_present,
                'type': row.seance_type,
                'participant': f'{nb_participants} participants'
            })
        
        return list(groupe_dict.values())
        
    except Exception as e:
        return []



@app.route('/api/presences/adherent/<matricule>/details')
def get_adherent_presence_details(matricule):
    """
    Récupère les détails des présences d'un adhérent spécifique
    """
    try:
        # Rechercher toutes les présences où le matricule apparaît
        presences = Presence.query.filter(
            func.find_in_set(matricule, Presence.adherent_matricule) > 0
        ).order_by(Presence.date_seance.desc()).all()

        details = []
        for presence in presences:
            details.append({
                "date": presence.date_seance.strftime('%d/%m/%Y'),
                "groupe": presence.groupe_nom,
                "entraineur": presence.entraineur_nom,
                "heure_debut": presence.heure_debut.strftime('%H:%M'),
                "etat": "Présent(e)" if presence.est_present == 'O' else "Absent(e)"
            })

        return jsonify({
            "success": True, 
            "details": details
        })

    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

# ============================================================================
# ROUTES PRINCIPALES CORRIGÉES
# ============================================================================

@app.route('/api/presences/search', methods=['POST'])
def search_presences():
    """
    Recherche les présences selon les critères spécifiés pour le dashboard
    """
    try:
        data = request.get_json()
        
        # Validation des paramètres requis
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Aucune donnée fournie'
            }), 400
            
        search_type = data.get('type')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        search_term = data.get('search_term', '').strip()
        
        # Validation des paramètres
        if not all([search_type, start_date, end_date]):
            return jsonify({
                'status': 'error',
                'message': 'Type de recherche, date de début et date de fin sont requis'
            }), 400
            
        if search_type not in ['adherent', 'entraineur', 'groupe']:
            return jsonify({
                'status': 'error',
                'message': 'Type de recherche invalide'
            }), 400
        
        # Conversion des dates
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Format de date invalide. Utilisez YYYY-MM-DD'
            }), 400
            
        # Validation de la période
        if start_date > end_date:
            return jsonify({
                'status': 'error',
                'message': 'La date de début doit être antérieure à la date de fin'
            }), 400
        
        # Recherche selon le type
        if search_type == 'adherent':
            results = search_adherent_presences(start_date, end_date, search_term)
        elif search_type == 'entraineur':
            results = search_entraineur_presences(start_date, end_date, search_term)
        elif search_type == 'groupe':
            results = search_groupe_presences(start_date, end_date, search_term)
        
        return jsonify({
            'status': 'success',
            'data': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la recherche: {str(e)}'
        }), 500

@app.route('/api/presences/export', methods=['GET'])
def export_presences():
    """
    Export des présences en format Excel
    """
    try:
        # Récupérer les paramètres
        search_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search_term = request.args.get('search_term', '')
        
        if not all([search_type, start_date, end_date]):
            return jsonify({'error': 'Paramètres manquants'}), 400
        
        # Conversion des dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Récupérer les données
        if search_type == 'adherent':
            data = search_adherent_presences(start_date, end_date, search_term)
        elif search_type == 'entraineur':
            data = search_entraineur_presences(start_date, end_date, search_term)
        elif search_type == 'groupe':
            data = search_groupe_presences(start_date, end_date, search_term)
        else:
            return jsonify({'error': 'Type invalide'}), 400
        
        # Créer le fichier Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Styles
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        present_format = workbook.add_format({
            'bg_color': '#C6EFCE',
            'font_color': '#006100',
            'border': 1
        })
        
        absent_format = workbook.add_format({
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006',
            'border': 1
        })
        
        cell_format = workbook.add_format({'border': 1})
        
        # Créer les feuilles selon le type
        if search_type == 'adherent':
            create_adherent_sheet(workbook, data, header_format, present_format, absent_format, cell_format)
        elif search_type == 'entraineur':
            create_entraineur_sheet(workbook, data, header_format, present_format, absent_format, cell_format)
        elif search_type == 'groupe':
            create_groupe_sheet(workbook, data, header_format, present_format, absent_format, cell_format)
        
        workbook.close()
        output.seek(0)
        
        filename = f'presences_{search_type}_{start_date}_{end_date}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export: {str(e)}'}), 500

# ============================================================================
# FONCTIONS D'EXPORT EXCEL CORRIGÉES
# ============================================================================

def create_adherent_sheet(workbook, data, header_format, present_format, absent_format, cell_format):
    """Créer la feuille Excel pour les adhérents"""
    worksheet = workbook.add_worksheet('Adhérents')
    
    # En-têtes
    headers = ['Matricule', 'Nom', 'Prénom', 'Date', 'Heure', 'Groupe', 'Entraîneur', 'Présence']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    row = 1
    for adherent in data:
        if 'sessions' in adherent:
            for session in adherent['sessions']:
                worksheet.write(row, 0, adherent['matricule'], cell_format)
                worksheet.write(row, 1, adherent['nom'], cell_format)
                worksheet.write(row, 2, adherent['prenom'], cell_format)
                worksheet.write(row, 3, session['date_seance'], cell_format)
                worksheet.write(row, 4, session['heure_debut'], cell_format)
                worksheet.write(row, 5, session['groupe_nom'], cell_format)
                worksheet.write(row, 6, session['entraineur_nom'], cell_format)
                
                presence_text = 'Présent' if session['est_present'] == 'O' else 'Absent'
                presence_format = present_format if session['est_present'] == 'O' else absent_format
                worksheet.write(row, 7, presence_text, presence_format)
                
                row += 1
    
    # Ajuster la largeur des colonnes
    worksheet.set_column('A:H', 15)

def create_entraineur_sheet(workbook, data, header_format, present_format, absent_format, cell_format):
    """Créer la feuille Excel pour les entraîneurs"""
    worksheet = workbook.add_worksheet('Entraîneurs')
    
    # En-têtes
    headers = ['Nom Entraîneur', 'Date', 'Heure', 'Groupe', 'Présence']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    row = 1
    for entraineur in data:
        if 'sessions' in entraineur:
            for session in entraineur['sessions']:
                worksheet.write(row, 0, entraineur['nom'], cell_format)
                worksheet.write(row, 1, session['date_seance'], cell_format)
                worksheet.write(row, 2, session['heure_debut'], cell_format)
                worksheet.write(row, 3, session['groupe_nom'], cell_format)
                
                presence_text = 'Présent' if session['est_present'] == 'O' else 'Absent'
                presence_format = present_format if session['est_present'] == 'O' else absent_format
                worksheet.write(row, 4, presence_text, presence_format)
                
                row += 1
    
    # Ajuster la largeur des colonnes
    worksheet.set_column('A:E', 15)

def create_groupe_sheet(workbook, data, header_format, present_format, absent_format, cell_format):
    """Créer la feuille Excel pour les groupes"""
    worksheet = workbook.add_worksheet('Groupes')
    
    # En-têtes
    headers = ['Groupe', 'Date', 'Heure', 'Type', 'Participant', 'Entraîneur', 'Présence']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    row = 1
    for groupe in data:
        if 'sessions' in groupe:
            for session in groupe['sessions']:
                worksheet.write(row, 0, groupe['nom'], cell_format)
                worksheet.write(row, 1, session['date_seance'], cell_format)
                worksheet.write(row, 2, session['heure_debut'], cell_format)
                worksheet.write(row, 3, session['type'], cell_format)
                worksheet.write(row, 4, session['participant'], cell_format)
                worksheet.write(row, 5, session.get('entraineur_nom', ''), cell_format)
                
                presence_text = 'Présent' if session['est_present'] == 'O' else 'Absent'
                presence_format = present_format if session['est_present'] == 'O' else absent_format
                worksheet.write(row, 6, presence_text, presence_format)
                
                row += 1
    
    # Ajuster la largeur des colonnes
    worksheet.set_column('A:G', 15)


@app.route('/situation-totale')
def situation_totale_page():
    return render_template("situation_total.html")

@app.route('/api/situation-totale')
def situation_totale():
    try:
        # Get season information from session
        year = session.get('saison')
        season_type = session.get('saison_type')
        
        if not year:
            return jsonify({'error': 'Aucune saison sélectionnée'}), 400

        # Generate season codes using your existing function
        from filter_functions import get_season_codes
        season_codes = get_season_codes(year)
        
        # Determine which season codes to filter by
        if season_type == 'S':
            season_codes_to_use = [season_codes['normal']]  # S{year}
        elif season_type == 'E':
            season_codes_to_use = [season_codes['summer']]  # E{year}
        else:
            # If no specific type, use both
            season_codes_to_use = [season_codes['normal'], season_codes['summer']]

        # Get saison from query parameter (for manual override)
        saison_param = request.args.get('saison')
        if saison_param:
            season_codes_to_use = [saison_param]

        # Query adherents with season filter
        adherents_query = Adherent.query.filter(Adherent.code_saison.in_(season_codes_to_use))
        adherents = adherents_query.all()

        # Query payments with season filter
        paiements_query = Paiement.query.filter(Paiement.code_saison.in_(season_codes_to_use))
        paiements = paiements_query.all()
        
        situation_par_adherent = []
        
        for a in adherents:
            # Paiements existants pour cet adhérent
            a_paiements = [
                p for p in paiements
                if str(p.matricule_adherent).strip() == str(a.matricule).strip()
            ]
            total_paye_adherent = sum(float(p.montant_paye or 0) for p in a_paiements)
            
            # Cotisation et remise depuis la table adherent
            cotisation = float(a.cotisation or 0)
            remise_pourcentage = float(a.remise) if a.remise is not None else 0
            remise_montant = (cotisation * remise_pourcentage) / 100
            reste_a_payer = cotisation - total_paye_adherent - remise_montant
            
            situation_par_adherent.append({
                'matricule': a.matricule,
                'nom': a.nom,
                'prenom': a.prenom,
                'cotisation': cotisation,
                'groupe': a.groupe or '',
                'type_abonnement': a.type_abonnement or '',
                'entraineur': a.entraineur or '',
                'total_a_payer': cotisation,
                'total_paye': total_paye_adherent if total_paye_adherent > 0 else 0,
                'total_remise': remise_pourcentage,
                'reste_a_payer': reste_a_payer,
                'aucun_paiement': len(a_paiements) == 0,
                'code_saison': a.code_saison
            })
        
        # Totaux généraux
        total_a_payer_general = sum(float(a.cotisation or 0) for a in adherents)
        total_paye_general = sum(sum(float(p.montant_paye or 0) for p in paiements if str(p.matricule_adherent).strip() == str(a.matricule).strip()) for a in adherents)
        total_remise_general = sum((float(a.cotisation or 0) * float(a.remise or 0)) / 100 for a in adherents)
        reste_a_payer_general = total_a_payer_general - total_paye_general - total_remise_general
        
        # Get available seasons for the dropdown
        saisons_disponibles = list(set(a.code_saison for a in Adherent.query.filter(Adherent.code_saison.isnot(None)).all() if a.code_saison))
        
        return jsonify({
            'totaux_generaux': {
                'total_a_payer': total_a_payer_general,
                'total_paye': total_paye_general,
                'total_remise': total_remise_general,
                'reste_a_payer': reste_a_payer_general
            },
            'situation_par_adherent': situation_par_adherent,
            'saisons_disponibles': saisons_disponibles,
            'saison_code': season_codes_to_use[0] if len(season_codes_to_use) == 1 else f"All_{year}",
            'saison_type': season_type,
            'saison_year': year
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/adherent-paiements/<matricule>')
def get_adherent_paiements(matricule):
    """Récupérer les détails des paiements pour un adhérent spécifique"""
    try:
        # Get season information from session
        year = session.get('saison')
        season_type = session.get('saison_type')
        
        if not year:
            return jsonify({'error': 'Aucune saison sélectionnée'}), 400

        # Generate season codes
        from filter_functions import get_season_codes
        season_codes = get_season_codes(year)
        
        # Determine which season codes to filter by
        if season_type == 'S':
            season_codes_to_use = [season_codes['normal']]
        elif season_type == 'E':
            season_codes_to_use = [season_codes['summer']]
        else:
            season_codes_to_use = [season_codes['normal'], season_codes['summer']]

        # Get saison from query parameter (for manual override)
        saison_param = request.args.get('saison')
        if saison_param:
            season_codes_to_use = [saison_param]

        # Récupérer tous les paiements pour cet adhérent avec filtre de saison
        paiements_query = Paiement.query.filter(
            Paiement.matricule_adherent == matricule,
            Paiement.code_saison.in_(season_codes_to_use)
        )
        
        paiements = paiements_query.all()
        
        paiements_list = []
        total_paye = 0
        
        for p in paiements:
            paiement_data = {
                'id_paiement': p.id_paiement,
                'date_paiement': p.date_paiement.isoformat() if p.date_paiement else None,
                'montant': float(p.montant or 0),
                'montant_paye': float(p.montant_paye or 0),
                'montant_reste': float(p.montant_reste or 0),
                'type_reglement': p.type_reglement,
                'numero_cheque': p.numero_cheque,
                'banque': p.banque,
                'cotisation': float(p.cotisation or 0),
                'remise': float(p.remise or 0),
                'numero_bon': p.numero_bon,
                'numero_carnet': p.numero_carnet,
                'code_saison': p.code_saison
            }
            paiements_list.append(paiement_data)
            total_paye += float(p.montant_paye or 0)
        
        return jsonify({
            'paiements': paiements_list,
            'total_paye': total_paye,
            'nombre_paiements': len(paiements_list),
            'saison_code': season_codes_to_use[0] if len(season_codes_to_use) == 1 else f"All_{year}",
            'saison_type': season_type,
            'saison_year': year
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/saisons')
def get_saisons():
    try:
        # Récupérer toutes les saisons distinctes depuis la base de données
        saisons_adherent = db.session.query(Adherent.code_saison).distinct().all()
        saisons_paiement = db.session.query(Paiement.code_saison).distinct().all()
        
        # Combiner et dédupliquer
        all_saisons = set([s[0] for s in saisons_adherent if s[0]] + [s[0] for s in saisons_paiement if s[0]])
        
        # Trier les saisons (S avant E, puis par année décroissante)
        def sort_key(saison):
            if not saison:
                return ('', 0)
            season_type = saison[0]  # S or E
            try:
                year = int(saison[1:])
            except:
                year = 0
            return (season_type, -year)  # Negative for descending year
        
        sorted_saisons = sorted(all_saisons, key=sort_key)
        
        return jsonify([{'code': s} for s in sorted_saisons])
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
        

from flask import request, jsonify
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, timedelta
from calendar import month_name
import locale

# Configurer la locale pour le français (optionnel)
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    pass

from flask import request, jsonify
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, timedelta
from calendar import month_name
import locale

# Configurer la locale pour le français (optionnel)
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    pass
@app.route('/api/financial-data')
@season_required
def get_financial_data():
    """Récupérer les données financières complètes pour le dashboard"""
    try:
        # Get current season information
        current_season_code = session.get('saison_code')
        year = session.get('saison')
        
        if not current_season_code:
            return jsonify({'error': 'Aucune saison sélectionnée'}), 400

        # Get filter parameters
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        saison_filter = request.args.get('saison', current_season_code)
        data_type = request.args.get('dataType', 'all')

        # Set default dates if not provided
        if not start_date:
            start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # Convert dates
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Validate dates
        if start_date_obj > end_date_obj:
            return jsonify({'error': 'La date de début ne peut pas être après la date de fin'}), 400

        # Calculate all financial data
        stats = calculate_financial_stats(start_date_obj, end_date_obj, saison_filter, data_type)
        monthly_data = get_monthly_data(start_date_obj, end_date_obj, saison_filter)
        revenue_by_type = get_revenue_by_type(start_date_obj, end_date_obj, saison_filter)
        recent_payments = get_recent_payments(start_date_obj, end_date_obj, saison_filter, data_type, 10)
        recent_locations = get_recent_locations(start_date_obj, end_date_obj, saison_filter, data_type, 10)

        return jsonify({
            'stats': stats,
            'monthlyData': monthly_data,
            'revenueByType': revenue_by_type,
            'recentPayments': recent_payments,
            'recentLocations': recent_locations,
            'saison_code': current_season_code,
            'saison_year': year
        })

    except Exception as e:
        logger.error(f"Erreur dans get_financial_data: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

def calculate_financial_stats(start_date, end_date, saison, data_type):
    """Calculer les statistiques financières globales"""
    try:
        total_revenus = 0
        
        # Revenus des paiements (cotisations et autres)
        if data_type in ['all', 'paiements']:
            # Cotisations des adhérents
            cotisations_query = db.session.query(func.coalesce(func.sum(Paiement.montant_paye), 0))
            
            if start_date and end_date:
                cotisations_query = cotisations_query.filter(
                    Paiement.date_paiement.between(start_date, end_date)
                )
            
            if saison:
                cotisations_query = cotisations_query.filter(Paiement.code_saison == saison)
                
            revenus_cotisations = float(cotisations_query.scalar() or 0)

            # Autres paiements
            autres_query = db.session.query(func.coalesce(func.sum(AutresPaiements.montant), 0))
            
            if start_date and end_date:
                autres_query = autres_query.filter(
                    AutresPaiements.date_paiement.between(start_date, end_date)
                )
            
            if saison:
                autres_query = autres_query.filter(AutresPaiements.code_saison == saison)
                
            revenus_autres = float(autres_query.scalar() or 0)
            
            total_revenus += revenus_cotisations + revenus_autres
        
        # Revenus des locations
        if data_type in ['all', 'locations']:
            locations_query = db.session.query(func.coalesce(func.sum(LocationTerrain.montant_location), 0))
            
            if start_date and end_date:
                locations_query = locations_query.filter(
                    LocationTerrain.date_location.between(start_date, end_date)
                )
            
            revenus_locations = float(locations_query.scalar() or 0)
            total_revenus += revenus_locations
        
        # Dépenses
        total_depenses = 0
        if data_type in ['all', 'depenses']:
            depenses_query = db.session.query(func.coalesce(func.sum(Depense.montant), 0))
            
            if start_date and end_date:
                depenses_query = depenses_query.filter(
                    Depense.date.between(start_date, end_date)
                )
            
            total_depenses = float(depenses_query.scalar() or 0)
        
        # Bénéfice net
        benefice_net = total_revenus - total_depenses
        
        # Adhérents actifs (uniquement si on filtre par saison)
        adherents_actifs = 0
        if saison:
            adherents_query = db.session.query(func.count(Adherent.matricule)).filter(
                Adherent.status == 'Actif',
                Adherent.code_saison == saison
            )
            adherents_actifs = adherents_query.scalar() or 0
        
        # Calcul des variations (comparaison avec période précédente)
        previous_stats = get_previous_period_stats(start_date, end_date, saison, data_type)
        
        revenus_change = calculate_percentage_change(total_revenus, previous_stats['previous_revenus'])
        depenses_change = calculate_percentage_change(total_depenses, previous_stats['previous_depenses'])
        benefice_change = calculate_percentage_change(benefice_net, previous_stats['previous_benefice'])
        adherents_change = calculate_percentage_change(adherents_actifs, previous_stats['previous_adherents'])

        return {
            'totalRevenus': round(total_revenus, 2),
            'totalDepenses': round(total_depenses, 2),
            'beneficeNet': round(benefice_net, 2),
            'adherentsActifs': adherents_actifs,
            'revenusChange': round(revenus_change, 1),
            'depensesChange': round(depenses_change, 1),
            'beneficeChange': round(benefice_change, 1),
            'adherentsChange': round(adherents_change, 1)
        }
        
    except Exception as e:
        logger.error(f"Erreur dans calculate_financial_stats: {str(e)}")
        return {
            'totalRevenus': 0,
            'totalDepenses': 0,
            'beneficeNet': 0,
            'adherentsActifs': 0,
            'revenusChange': 0,
            'depensesChange': 0,
            'beneficeChange': 0,
            'adherentsChange': 0
        }

def get_monthly_data(start_date, end_date, saison):
    """Obtenir les données mensuelles pour le graphique d'évolution"""
    try:
        # Limiter à 24 mois maximum pour éviter les problèmes de performance
        months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        if months_diff > 24:
            start_date = end_date.replace(year=end_date.year - 2, month=end_date.month, day=1)
        
        # Générer les mois
        labels = []
        revenues = []
        expenses = []
        
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            # Format du label
            month_names_fr = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                             'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            month_label = month_names_fr[current_date.month - 1]
            if current_date.year != datetime.now().year:
                month_label += f" {current_date.year}"
            labels.append(month_label)
            
            # Calculer le dernier jour du mois
            if current_date.month == 12:
                next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                next_month = current_date.replace(month=current_date.month + 1, day=1)
            month_end = next_month - timedelta(days=1)
            
            # Revenus du mois
            monthly_revenue = 0
            
            # Cotisations du mois
            cotisations_month = db.session.query(func.coalesce(func.sum(Paiement.montant_paye), 0)).filter(
                Paiement.date_paiement.between(current_date, month_end)
            )
            if saison:
                cotisations_month = cotisations_month.filter(Paiement.code_saison == saison)
            cotisations_month = cotisations_month.scalar() or 0
            
            # Autres paiements du mois
            autres_month = db.session.query(func.coalesce(func.sum(AutresPaiements.montant), 0)).filter(
                AutresPaiements.date_paiement.between(current_date, month_end)
            )
            if saison:
                autres_month = autres_month.filter(AutresPaiements.code_saison == saison)
            autres_month = autres_month.scalar() or 0
            
            # Locations du mois
            locations_month = db.session.query(func.coalesce(func.sum(LocationTerrain.montant_location), 0)).filter(
                LocationTerrain.date_location.between(current_date, month_end)
            ).scalar() or 0
            
            monthly_revenue = cotisations_month + autres_month + locations_month
            revenues.append(float(monthly_revenue))
            
            # Dépenses du mois
            monthly_expenses = db.session.query(func.coalesce(func.sum(Depense.montant), 0)).filter(
                Depense.date.between(current_date, month_end)
            ).scalar() or 0
            
            expenses.append(float(monthly_expenses))
            
            # Passer au mois suivant
            current_date = next_month
        
        return {
            'labels': labels,
            'revenues': revenues,
            'expenses': expenses
        }
        
    except Exception as e:
        logger.error(f"Erreur dans get_monthly_data: {str(e)}")
        return {
            'labels': [],
            'revenues': [],
            'expenses': []
        }

def get_revenue_by_type(start_date, end_date, saison):
    """Calculer la répartition des revenus par type"""
    try:
        # Revenus des cotisations
        cotisations_query = db.session.query(func.coalesce(func.sum(Paiement.montant_paye), 0))
        
        if start_date and end_date:
            cotisations_query = cotisations_query.filter(
                Paiement.date_paiement.between(start_date, end_date)
            )
        
        if saison:
            cotisations_query = cotisations_query.filter(Paiement.code_saison == saison)
            
        cotisations = cotisations_query.scalar() or 0
        
        # Revenus des autres paiements
        autres_query = db.session.query(func.coalesce(func.sum(AutresPaiements.montant), 0))
        
        if start_date and end_date:
            autres_query = autres_query.filter(
                AutresPaiements.date_paiement.between(start_date, end_date)
            )
        
        if saison:
            autres_query = autres_query.filter(AutresPaiements.code_saison == saison)
            
        autres = autres_query.scalar() or 0
        
        # Revenus des locations
        locations_query = db.session.query(func.coalesce(func.sum(LocationTerrain.montant_location), 0))
        
        if start_date and end_date:
            locations_query = locations_query.filter(
                LocationTerrain.date_location.between(start_date, end_date)
            )
        
        locations = locations_query.scalar() or 0
        
        # Préparer les données pour le graphique
        labels = []
        values = []
        
        if cotisations > 0:
            labels.append('Cotisations')
            values.append(float(cotisations))
        
        if locations > 0:
            labels.append('Locations')
            values.append(float(locations))
        
        if autres > 0:
            labels.append('Autres paiements')
            values.append(float(autres))
        
        # Si aucune donnée, créer des données par défaut
        if not labels:
            labels = ['Cotisations', 'Locations', 'Autres paiements']
            values = [0, 0, 0]
        
        return {
            'labels': labels,
            'values': values
        }
        
    except Exception as e:
        logger.error(f"Erreur dans get_revenue_by_type: {str(e)}")
        return {
            'labels': ['Cotisations', 'Locations', 'Autres paiements'],
            'values': [0, 0, 0]
        }

def get_recent_payments(start_date, end_date, saison, data_type, limit=10):
    """Obtenir les derniers paiements"""
    try:
        if data_type not in ['all', 'paiements']:
            return []
        
        # Base query avec jointure
        query = db.session.query(
            Paiement.date_paiement,
            Paiement.matricule_adherent,
            Paiement.montant_paye,
            Paiement.code_saison,
            Paiement.type_reglement,
            Adherent.nom,
            Adherent.prenom
        ).outerjoin(
            Adherent, Paiement.matricule_adherent == Adherent.matricule
        ).filter(
            Paiement.montant_paye.isnot(None),
            Paiement.montant_paye > 0
        )
        
        # Appliquer les filtres
        if start_date and end_date:
            query = query.filter(
                Paiement.date_paiement.between(start_date, end_date)
            )
        
        if saison:
            query = query.filter(Paiement.code_saison == saison)
        
        # Ordonner par date décroissante et limiter
        payments = query.order_by(Paiement.date_paiement.desc()).limit(limit).all()
        
        result = []
        for payment in payments:
            adherent_name = "Inconnu"
            if payment.nom and payment.prenom:
                adherent_name = f"{payment.nom} {payment.prenom}"
            elif payment.matricule_adherent:
                adherent_name = f"Matricule {payment.matricule_adherent}"
                
            result.append({
                'date': payment.date_paiement.strftime('%Y-%m-%d') if payment.date_paiement else '',
                'adherent': adherent_name,
                'montant': float(payment.montant_paye) if payment.montant_paye else 0,
                'type': payment.type_reglement or 'Cotisation',
                'saison': payment.code_saison or saison or ''
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur dans get_recent_payments: {str(e)}")
        return []

def get_recent_locations(start_date, end_date, saison, data_type, limit=10):
    """Obtenir les locations récentes"""
    try:
        if data_type not in ['all', 'locations']:
            return []
        
        # Base query
        query = db.session.query(LocationTerrain).filter(
            LocationTerrain.montant_location.isnot(None),
            LocationTerrain.montant_location > 0
        )
        
        # Appliquer les filtres de date
        if start_date and end_date:
            query = query.filter(
                LocationTerrain.date_location.between(start_date, end_date)
            )
        
        # Ordonner par date décroissante et limiter
        locations = query.order_by(LocationTerrain.date_location.desc()).limit(limit).all()
        
        result = []
        for location in locations:
            # Calculer la durée
            duree = "N/A"
            try:
                if location.heure_debut and location.heure_fin:
                    debut = datetime.combine(datetime.min.date(), location.heure_debut)
                    fin = datetime.combine(datetime.min.date(), location.heure_fin)
                    if fin < debut:
                        fin = fin.replace(day=fin.day + 1)
                    duree_seconds = (fin - debut).total_seconds()
                    duree_hours = duree_seconds / 3600
                    duree = f"{duree_hours:.1f}h"
            except Exception:
                duree = "N/A"
            
            result.append({
                'date': location.date_location.strftime('%Y-%m-%d') if location.date_location else '',
                'terrain': location.numero_terrain or 'N/A',
                'locateur': location.locateur or 'Inconnu',
                'montant': float(location.montant_location) if location.montant_location else 0,
                'duree': duree
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur dans get_recent_locations: {str(e)}")
        return []

def get_previous_period_stats(start_date, end_date, saison, data_type):
    """Obtenir les statistiques de la période précédente pour le calcul des variations"""
    try:
        # Calculer la durée de la période actuelle
        period_days = (end_date - start_date).days
        
        # Calculer les dates de la période précédente
        previous_end_date = start_date - timedelta(days=1)
        previous_start_date = previous_end_date - timedelta(days=period_days)
        
        # Recalculer les stats pour la période précédente
        previous_revenus = 0
        
        if data_type in ['all', 'paiements']:
            # Cotisations période précédente
            cotisations_prev = db.session.query(func.coalesce(func.sum(Paiement.montant_paye), 0)).filter(
                Paiement.date_paiement.between(previous_start_date, previous_end_date)
            )
            if saison:
                cotisations_prev = cotisations_prev.filter(Paiement.code_saison == saison)
            cotisations_prev = cotisations_prev.scalar() or 0
            
            # Autres paiements période précédente
            autres_prev = db.session.query(func.coalesce(func.sum(AutresPaiements.montant), 0)).filter(
                AutresPaiements.date_paiement.between(previous_start_date, previous_end_date)
            )
            if saison:
                autres_prev = autres_prev.filter(AutresPaiements.code_saison == saison)
            autres_prev = autres_prev.scalar() or 0
            
            previous_revenus += cotisations_prev + autres_prev
        
        if data_type in ['all', 'locations']:
            # Locations période précédente
            locations_prev = db.session.query(func.coalesce(func.sum(LocationTerrain.montant_location), 0)).filter(
                LocationTerrain.date_location.between(previous_start_date, previous_end_date)
            ).scalar() or 0
            previous_revenus += locations_prev
        
        # Dépenses période précédente
        previous_depenses = 0
        if data_type in ['all', 'depenses']:
            previous_depenses = db.session.query(func.coalesce(func.sum(Depense.montant), 0)).filter(
                Depense.date.between(previous_start_date, previous_end_date)
            ).scalar() or 0
        
        previous_benefice = previous_revenus - previous_depenses
        
        # Adhérents période précédente
        previous_adherents = 0
        if saison:
            previous_adherents = db.session.query(func.count(Adherent.matricule)).filter(
                Adherent.status == 'Actif',
                Adherent.code_saison == saison
            ).scalar() or 0
        
        return {
            'previous_revenus': previous_revenus,
            'previous_depenses': previous_depenses,
            'previous_benefice': previous_benefice,
            'previous_adherents': previous_adherents
        }
        
    except Exception as e:
        logger.error(f"Erreur dans get_previous_period_stats: {str(e)}")
        return {
            'previous_revenus': 0,
            'previous_depenses': 0,
            'previous_benefice': 0,
            'previous_adherents': 0
        }

def calculate_percentage_change(current_value, previous_value):
    """Calculer le pourcentage de changement entre deux valeurs"""
    if previous_value == 0:
        return 0 if current_value == 0 else 100
    return ((current_value - previous_value) / abs(previous_value)) * 100

@app.route('/rh')
def rh():
    return render_template("hr.html")


@app.route('/hr_entraineur_salaire', methods=['GET', 'POST'])
def hr_entraineur_salaire():
    """
    Route HR pour calculer les salaires des entraîneurs basés sur leur présence
    Paramètres acceptés (GET ou POST):
      - search_term : chaîne (optionnel) pour filtrer par nom/prenom
      - date_debut : date de début (optionnel, format YYYY-MM-DD)
      - date_fin : date de fin (optionnel, format YYYY-MM-DD)
    """
    search_term = (request.values.get("search_term") or "").strip()
    date_debut = request.values.get("date_debut")
    date_fin = request.values.get("date_fin")
    
    results = []
    
    # Query des entraîneurs
    q = Entraineur.query
    if search_term:
        like = f"%{search_term}%"
        q = q.filter(or_(
            Entraineur.nom.ilike(like),
            Entraineur.prenom.ilike(like)
        ))
    
    entraineurs = q.order_by(Entraineur.nom, Entraineur.prenom).all()
    
    for entraineur in entraineurs:
        full_name = f"{entraineur.nom} {entraineur.prenom}"
        
        # Query de base pour les présences
        pres_query = PresenceEntraineur.query.filter(
            PresenceEntraineur.entraineur_nom == full_name
        )
        
        # Appliquer les filtres de date si fournis
        if date_debut:
            try:
                date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
                pres_query = pres_query.filter(PresenceEntraineur.date_seance >= date_debut_obj)
            except ValueError:
                pass
                
        if date_fin:
            try:
                date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
                pres_query = pres_query.filter(PresenceEntraineur.date_seance <= date_fin_obj)
            except ValueError:
                pass
        
        pres_rows = pres_query.order_by(PresenceEntraineur.date_seance).all()
        
        # Calculer les heures présentes et absentes
        heures_presentes = 0
        heures_absentes = 0
        
        for pres in pres_rows:
            # Récupérer la séance correspondante pour calculer la durée
            seance = Seance.query.filter(
                and_(
                    Seance.date == pres.date_seance,
                    Seance.heure_debut == pres.heure_debut,
                    Seance.entraineur == full_name
                )
            ).first()
            
            if seance:
                # Calculer la durée de la séance en heures
                debut = datetime.combine(datetime.today(), seance.heure_debut)
                fin = datetime.combine(datetime.today(), seance.heure_fin)
                duree_heures = (fin - debut).total_seconds() / 3600
                
                if pres.est_present == 'O':
                    heures_presentes += duree_heures
                else:
                    heures_absentes += duree_heures
            else:
                # Si pas de séance trouvée, considérer 1.5h par défaut
                duree_heures = 1.5
                if pres.est_present == 'O':
                    heures_presentes += duree_heures
                else:
                    heures_absentes += duree_heures
        
        # Calculer le pourcentage d'absence
        total_heures = heures_presentes + heures_absentes
        pourcentage_absence = (heures_absentes / total_heures * 100) if total_heures > 0 else 0
        
        results.append({
            "id": entraineur.id_entraineur,
            "nom": entraineur.nom,
            "prenom": entraineur.prenom,
            "type_abonnement": entraineur.type_abonnement or "N/D",
            "heures_presentes": round(heures_presentes, 2),
            "heures_absentes": round(heures_absentes, 2),
            "total_heures": round(total_heures, 2),
            "pourcentage_absence": round(pourcentage_absence, 2)
        })
    
    return jsonify(results)




@app.route("/game")
def game():
    return render_template("game.html")

    
# Running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)