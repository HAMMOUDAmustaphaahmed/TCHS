from flask import send_file
from flask import send_from_directory
from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time, timedelta
import hashlib
import pytz
import json

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




# Home page
@app.route('/')
def home():
    return render_template('signin.html')

@app.route('/presentation')
def presentation():
    return render_template('presentation.html')



@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    # Statistiques de base
    paiements = Paiement.query.all()
    total_collecte=0
    total_reste =0
    moyenne_paiement = 0
    for p in paiements:
        total_collecte += p.montant_paye 
        total_reste += p.montant_reste
    paiements_count = len(paiements)
    if paiements_count > 0:
        moyenne_paiement = total_collecte / paiements_count
    else:
        return moyenne_paiement
    
    

    # Derniers paiements
    paiements_recent = Paiement.query.order_by(Paiement.date_paiement.desc()).limit(5).all()
    moyenne_paiement=f"{moyenne_paiement:.2f}"

    return render_template('admin.html',
        total_collecte=float(total_collecte),
        total_reste=float(total_reste),
        moyenne_paiement=float(moyenne_paiement),
        paiements_count=int(paiements_count),
        paiements_recent=paiements_recent)

from sqlalchemy import func, or_

@app.route('/entraineur', methods=['GET', 'POST'])
def entraineur():
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

   # Gestion de la navigation
    week_offset = request.args.get('week_offset', 0, type=int)
    day_offset = request.args.get('day_offset', 0, type=int)
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    day_offset = max(0, min(6, day_offset))  # Bloque entre 0 (lundi) et 6 (dimanche)
    current_day = start_of_week + timedelta(days=day_offset)

    # Récupérer les séances pour l'entraîneur actuel
    seances = Seance.query.filter_by(entraineur=f"{nom} {prenom}").all()

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

    return render_template(
        'entraineur.html',
        current_day=current_day,
        week_offset=week_offset,
        day_offset=day_offset,
        entraineur=entraineur,
        seances=seances,
        creneaux=creneaux
    )


from sqlalchemy import and_, or_


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
                print("Les heures doivent être entre 08:00 et 20:00", "danger")
                return redirect(url_for('locations_terrains'))

            if heure_debut >= heure_fin:
                print("L'heure de fin doit être après l'heure de début", "danger")
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
                print("Conflit de réservation pour ce créneau", "danger")
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
            print("Réservation enregistrée avec succès", "success")

        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la réservation : {str(e)}", "danger")

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


@app.route('/directeur_technique', methods=['GET', 'POST'])
def directeur_technique():
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

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

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'changer_entraineur':
            groupe_id = request.form.get('groupe_id')
            nouvel_entraineur_id = request.form.get('entraineur_id')
            groupe = Groupe.query.get(groupe_id)
            ancien_entraineur = groupe.entraineur_nom
            nouveau_entraineur = Entraineur.query.get(nouvel_entraineur_id)
            
            # Mettre à jour toutes les séances concernées
            Seance.query.filter_by(entraineur=ancien_entraineur).update({'entraineur': nouveau_entraineur.nom + ' ' + nouveau_entraineur.prenom})
            groupe.entraineur_nom = nouveau_entraineur.nom + ' ' + nouveau_entraineur.prenom
            db.session.commit()
            flash("Entraîneur modifié avec succès", "success")

        elif action == 'supprimer_seance':
            seance_id = request.form.get('seance_id')
            seance = Seance.query.get(seance_id)
            db.session.delete(seance)
            db.session.commit()
            flash("Séance supprimée", "success")
    
    # Gestion de la navigation
    week_offset = request.args.get('week_offset', 0, type=int)
    day_offset = request.args.get('day_offset', 0, type=int)
    
    # Calcul des dates
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    day_offset = max(0, min(6, day_offset))  # Bloque entre 0 (lundi) et 6 (dimanche)
    current_day = start_of_week + timedelta(days=day_offset)

    # Récupération des données
    groupes = Groupe.query.all()
    entraineurs = Entraineur.query.all()
    
    # Séances pour la semaine entière (pour les stats)
    seances_week = Seance.query.filter(
        Seance.date >= start_of_week.date(),
        Seance.date <= (start_of_week + timedelta(days=6)).date()
    ).all()
    
    # Séances pour le jour actuel (pour l'emploi du temps)
    seances_day = Seance.query.filter(
        Seance.date == current_day.date()
    ).all()

    # Calcul des séances par groupe
    seances_par_groupe = {}
    for seance in seances_week:
        if seance.groupe not in seances_par_groupe:
            seances_par_groupe[seance.groupe] = 0
        seances_par_groupe[seance.groupe] += 1

    # Récupérer tous les adhérents pour la recherche
    all_adherents = Adherent.query.all()
    adherents_list = [{
        'matricule': a.matricule,
        'nom': a.nom,
        'prenom': a.prenom
    } for a in all_adherents]

    return render_template(
        'directeur_technique.html',
        current_day=current_day,
        week_offset=week_offset,
        day_offset=day_offset,
        groupes=groupes,
        entraineurs=entraineurs,
        seances=seances_day,  # Utilise les séances du jour seulement
        seances_week=seances_week,  # Pour les stats hebdomadaires
        creneaux=creneaux,
        terrains=range(1, 10),
        seances_par_groupe=seances_par_groupe,
        all_adherents=adherents_list,  
        adherents_json=json.dumps(adherents_list)
    )


@app.route('/update_seance_adherents/<int:seance_id>', methods=['POST'])
def update_seance_adherents(seance_id):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    seance = Seance.query.get_or_404(seance_id)
    
    # Mettre à jour les informations de base
    seance.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    seance.heure_debut = datetime.strptime(request.form['heure_debut'], '%H:%M').time()
    seance.terrain = request.form['terrain']
    
    # Mettre à jour l'entraîneur
    entraineur = Entraineur.query.get(request.form['entraineur'])
    seance.entraineur = f"{entraineur.nom} {entraineur.prenom}"
    
    # Mettre à jour les adhérents
    adherents = request.form.getlist('adherents[]')
    seance.adherents_matricules = ','.join(adherents) if adherents else None
    
    db.session.commit()
    
    return jsonify({"message": "Séance mise à jour avec succès"}), 200


@app.route('/ajouter_seance', methods=['POST'])
def ajouter_seance():
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    data = request.get_json()
    
    # Récupérer les données
    groupe = Groupe.query.get(data['groupe_id'])
    if not groupe:
        return jsonify({"error": "Groupe introuvable"}), 404

    try:
        # Gestion plus robuste des formats de date
        date_str = data['date']
        try:
            # Essayer d'abord le format ISO
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            try:
                # Essayer le format français si le format ISO échoue
                date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
            except ValueError:
                return jsonify({"error": "Format de date invalide. Utilisez YYYY-MM-DD ou DD/MM/YYYY"}), 400

        # Conversion de l'heure
        try:
            heure_debut = datetime.strptime(data['heure_debut'], '%H:%M').time()
        except ValueError:
            return jsonify({"error": "Format d'heure invalide. Utilisez HH:MM"}), 400

        # Vérification des créneaux valides
        creneaux_valides = [
            time(8, 0), time(9, 30), time(11, 0), time(12, 30),
            time(14, 0), time(15, 30), time(17, 0), time(18, 30)
        ]
        
        if heure_debut not in creneaux_valides:
            return jsonify({"error": "Créneau horaire non valide"}), 400

        heure_fin = (datetime.combine(date_obj, heure_debut) + timedelta(minutes=90)).time()

        # Vérification des conflits
        conflits = Seance.query.filter(
            (
                (Seance.terrain == data['terrain']) |
                (Seance.entraineur == groupe.entraineur_nom) |
                (Seance.groupe == groupe.nom_groupe)
            ),
            Seance.date == date_obj,
            (
                (Seance.heure_debut <= heure_debut) & (Seance.heure_fin > heure_debut) |
                (Seance.heure_debut < heure_fin) & (Seance.heure_fin >= heure_fin)
            )
        ).first()

        if conflits:
            messages = []
            if conflits.terrain == data['terrain']:
                messages.append("Conflit de planning sur ce terrain")
            if conflits.entraineur == groupe.entraineur_nom:
                messages.append("L'entraîneur a déjà une séance à ce créneau")
            if conflits.groupe == groupe.nom_groupe:
                messages.append("Le groupe a déjà une séance à ce créneau")
            
            return jsonify({"error": " | ".join(messages)}), 400

        # Création de la séance
        nouvelle_seance = Seance(
            date=date_obj,
            heure_debut=heure_debut,
            groupe=groupe.nom_groupe,
            entraineur=groupe.entraineur_nom,
            terrain=data['terrain']
        )
        
        db.session.add(nouvelle_seance)
        db.session.commit()
        return jsonify({"message": "Séance ajoutée avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de l'ajout de la séance: {str(e)}"}), 500


@app.route('/api/get_session/<int:session_id>', methods=['GET'])
def api_get_session(session_id):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    session = Seance.query.get(session_id)
    if not session:
        return jsonify({"error": "Séance non trouvée"}), 404

    return jsonify({
        "session": {
            "date": session.date.strftime('%Y-%m-%d'),
            "heure_debut": session.heure_debut.strftime('%H:%M'),
            "terrain": session.terrain,
            "entraineur_id": session.entraineur
        }
    }), 200


@app.route('/edit_session', methods=['POST'])
def edit_session():
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    data = request.get_json()
    seance_id = data['session_id']  # ID de la séance
    new_date = data['date']
    new_heure_debut = data['heure_debut']
    new_terrain = data['terrain']
    entraineur_id = data['entraineur']

    # Récupérer l'entraîneur par ID
    entraineur = Entraineur.query.filter_by(id_entraineur=entraineur_id).first()
    if not entraineur:
        return jsonify({"error": "Entraîneur introuvable"}), 404
    new_entraineur = f"{entraineur.nom} {entraineur.prenom}"

    # Trouver la séance
    session = Seance.query.get(seance_id)
    if not session:
        return jsonify({"error": "Séance non trouvée"}), 404

    try:
        # Mise à jour des données
        new_date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()
        new_heure_debut_obj = datetime.strptime(new_heure_debut, '%H:%M').time()
        new_heure_fin_obj = (datetime.combine(new_date_obj, new_heure_debut_obj) + timedelta(minutes=90)).time()

        # Vérification des conflits
        terrain_conflit = Seance.query.filter(
            Seance.seance_id != seance_id,
            Seance.terrain == new_terrain,
            Seance.date == new_date_obj,
            (Seance.heure_debut < new_heure_fin_obj) & (Seance.heure_fin > new_heure_debut_obj)
        ).first()

        if terrain_conflit:
            return jsonify({"error": "Conflit de planning sur ce terrain"}), 400

        entraineur_conflit = Seance.query.filter(
            Seance.seance_id != seance_id,
            Seance.entraineur == new_entraineur,
            Seance.date == new_date_obj,
            (Seance.heure_debut < new_heure_fin_obj) & (Seance.heure_fin > new_heure_debut_obj)
        ).first()

        if entraineur_conflit:
            return jsonify({"error": "L'entraîneur est occupé à ce créneau"}), 400

        # Mise à jour de la séance
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

@app.route('/retirer_adherent_groupe/<int:groupe_id>', methods=['POST'])
def retirer_adherent_groupe(groupe_id):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    data = request.get_json()
    matricule = data.get('matricule')
    
    adherent = Adherent.query.filter_by(matricule=matricule).first()
    if not adherent:
        return jsonify({"error": "Adhérent non trouvé dans ce groupe"}), 404

    try:
        adherent.groupe = None
        adherent.entraineur = None
        db.session.commit()
        return jsonify({"message": "Adhérent retiré avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/ajouter_adherents_groupe/<int:groupe_id>', methods=['POST'])
def ajouter_adherents_groupe(groupe_id):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    groupe = Groupe.query.get(groupe_id)
    if not groupe:
        return jsonify({"error": "Groupe non trouvé"}), 404

    data = request.get_json()
    matricules = data.get('matricules', [])

    added_count = 0
    errors = []

    for matricule in matricules:
        adherent = Adherent.query.filter_by(matricule=matricule).first()
        if not adherent:
            errors.append(f"Adhérent {matricule} non trouvé")
            continue
            
        if adherent.groupe:
            errors.append(f"{adherent.nom} {adherent.prenom} déjà dans un groupe")
            continue

        try:
            adherent.groupe = groupe.nom_groupe
            adherent.entraineur = groupe.entraineur_nom
            db.session.commit()
            added_count += 1
        except Exception as e:
            db.session.rollback()
            errors.append(f"Erreur avec {matricule}: {str(e)}")

    if errors:
        return jsonify({
            "added_count": added_count,
            "error": "Certains adhérents n'ont pas pu être ajoutés",
            "details": errors
        }), 207  # Status code 207 Multi-Status

    return jsonify({
        "message": "Tous les adhérents ont été ajoutés avec succès",
        "added_count": added_count
    }), 200

@app.route('/ajouter_groupe', methods=['POST'])
def ajouter_groupe():
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    data = request.get_json()

    # Récupérer les données avec les bons noms de clés
    group_name = data.get('groupName')
    entraineur_id = data.get('entraineurId')  # Changé de 'entraineur' à 'entraineurId'

    if not group_name or not entraineur_id:
        return "Le nom du groupe ou l'entraîneur est manquant.", 400

    # Vérifier l'existence du groupe
    if Groupe.query.filter_by(nom_groupe=group_name).first():
        return "Un groupe avec ce nom existe déjà.", 400

    try:
        # Récupérer l'entraîneur par ID
        entraineur = Entraineur.query.get(entraineur_id)
        if not entraineur:
            return "Entraîneur introuvable.", 404

        # Créer le groupe avec les bonnes données
        nouveau_groupe = Groupe(
            nom_groupe=group_name,
            entraineur_nom=f"{entraineur.nom} {entraineur.prenom}",
            type_abonnement=entraineur.type_abonnement,
            categorie=group_name.split('-')[0]  # Ajout de la catégorie
        )
        
        db.session.add(nouveau_groupe)
        db.session.commit()
        return "Groupe ajouté avec succès.", 200

    except Exception as e:
        db.session.rollback()
        return f"Erreur lors de l'ajout du groupe : {str(e)}", 500

@app.route('/supprimer_groupe/<int:id>', methods=['DELETE'])
def supprimer_groupe(id):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    groupe = Groupe.query.get_or_404(id)
    
    try:
        # Supprimer toutes les séances associées
        Seance.query.filter_by(groupe=groupe.nom_groupe).delete()
        
        # Supprimer le groupe
        db.session.delete(groupe)
        db.session.commit()
        return jsonify({"message": "Groupe et séances associées supprimés avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/groupes_seances', methods=['GET'])
def api_groupes_seances():
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    username = session.get('username')
    nom, prenom = username.split('.')
    entraineur = Entraineur.query.filter_by(nom=nom, prenom=prenom).first()
    groupes = Groupe.query.filter_by(entraineur_nom=f"{nom} {prenom}").all()
    groupes_data = []
    if groupes :
        for groupe in groupes:
            seances = Seance.query.filter_by(groupe=groupe.nom_groupe).all()
            groupes_data.append({
                'groupe': {
                    'id': groupe.id_groupe,
                    'nom': groupe.nom_groupe,
                },
                'seances': [
                    {
                        'id': seance.seance_id,
                        'date': seance.date.strftime('%Y-%m-%d'),
                        'heure': seance.heure.strftime('%H:%M')
                    }
                    for seance in seances
                ]
            })

        return jsonify(groupes_data), 200
    else :
        return jsonify(groupes_data), 200


@app.route('/api/get_adherents_groupe/<int:groupe_id>', methods=['GET'])
def api_get_adherents_groupe(groupe_id):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    groupe = Groupe.query.get(groupe_id)
    if not groupe:
        return jsonify({"error": "Groupe non trouvé"}), 404

    adherents = Adherent.query.filter_by(groupe=groupe.nom_groupe).all()
    adherents_list = [
        {"matricule": adherent.matricule, "nom": adherent.nom, "prenom": adherent.prenom}
        for adherent in adherents
    ]
    return jsonify({"adherents": adherents_list}), 200

@app.route('/api/get_adherents/<int:seance_id>', methods=['GET'])
def api_get_adherents(seance_id):
    if 'user_id' not in session or session.get('role') not in ['admin', 'directeur_technique']:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    seance = Seance.query.get(seance_id)
    if not seance:
        return jsonify({"error": "Séance introuvable"}), 404

    adherents = Adherent.query.filter_by(groupe=seance.groupe).all()
    if not adherents:
        return jsonify({"error": "Aucun adhérent trouvé pour cette séance"}), 404

    adherents_list = [
        {"matricule": adherent.matricule, "nom": adherent.nom, "prenom": adherent.prenom}
        for adherent in adherents
    ]
    return jsonify({"adherents": adherents_list}), 200

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
    print(nouveau_mot_de_passe)
    print(confirmation_mot_de_passe)

    # Vérification des champs
    if not nouveau_mot_de_passe or not confirmation_mot_de_passe:
        return jsonify({"error": "Veuillez remplir tous les champs."}), 400

    if nouveau_mot_de_passe != confirmation_mot_de_passe:
        return jsonify({"error": "Les mots de passe ne correspondent pas."}), 400

    # Rechercher l'utilisateur par username
    user = User.query.filter_by(utilisateur=username).first()
    print(user)

    if not user:
        return jsonify({"error": "Utilisateur introuvable."}), 404

    # Hachage du nouveau mot de passe
    hashed_password = hashlib.sha256(nouveau_mot_de_passe.encode()).hexdigest()
    print(hashed_password)

    # Mettre à jour le mot de passe de l'utilisateur
    user.password = hashed_password

    # Sauvegarder les modifications dans la base de données
    db.session.commit()

    return jsonify({"message": "Mot de passe mis à jour avec succès."}), 200

@app.route('/api/marquer_presence/<int:seance_id>', methods=['POST'])
def api_marquer_presence(seance_id):
    data = request.get_json()
    presences = data.get('presences', [])

    seance = Seance.query.get(seance_id)
    if not seance:
        return "Séance introuvable", 404

    try:
        for presence in presences:
            new_presence = Presence(
                groupe_nom=seance.groupe,
                adherent_matricule=presence['matricule'],
                entraineur_nom=seance.entraineur,
                date_seance=seance.date,
                heure_debut=seance.heure,
                est_present=presence['est_present']
            )
            db.session.add(new_presence)
        db.session.commit()
        return "Présence enregistrée avec succès", 200
    except Exception as e:
        db.session.rollback()
        return f"Erreur lors de l'enregistrement des présences : {str(e)}", 500




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
        user = User.query.filter_by(utilisateur=utilisateur).first()
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user and user.password == hashed_password and user.role == 'admin':
            session['user_id'] = user.id
            session['username'] = user.utilisateur
            session['role'] = user.role
            flash('Connexion réussie.', 'success')
            return redirect(url_for('admin'))  
        elif user and user.password == hashed_password and user.role == 'directeur_technique':
            session['user_id'] = user.id
            session['username'] = user.utilisateur
            session['role'] = user.role
            flash('Connexion réussie.', 'success')
            return redirect(url_for('directeur_technique'))
        elif user and user.password == hashed_password and user.role == 'entraineur':
            session['user_id'] = user.id
            session['username'] = user.utilisateur
            session['role'] = user.role
            flash('Connexion réussie.', 'success')
            return redirect(url_for('entraineur'))
        else:
            flash('Nom d’utilisateur ou mot de passe incorrect.', 'danger')
    
    return render_template('signin.html')




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




@app.route('/ajouter_adherent', methods=['POST', 'GET'])
def ajouter_adherent():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    entraineurs = Entraineur.query.all()
    groupes = Groupe.query.all()  # Récupérer tous les groupes pour le formulaire

    if request.method == 'POST':
        nom_groupe = request.form.get('groupe') or None
        entraineur_nom = request.form.get('entraineur') or None
        type_abonnement = request.form.get('type_abonnement') or None



        # Calculer le matricule de l'adhérent
        dernier_adherent = Adherent.query.order_by(Adherent.matricule.desc()).first()
        matricule = dernier_adherent.matricule + 1 if dernier_adherent else 1
        # Ajouter un nouvel adhérent
        nouveau_adherent = Adherent(
            nom=request.form['Nom'],
            prenom=request.form['Prénom'],
            date_naissance=request.form['date_naissance'],
            date_inscription=request.form['date_inscription'],
            sexe=request.form['sexe'],
            tel1=request.form['tel1'],
            tel2=request.form['tel2'],
            type_abonnement=type_abonnement,
            ancien_abonne=request.form['ancien_abonne'],
            matricule=matricule,
            groupe=nom_groupe,
            entraineur=entraineur_nom,
            email=request.form['email'],
            paye='N',
            status='Actif'
        )

        
        

        try:
            db.session.add(nouveau_adherent)
            db.session.commit()
            generate_abonnement(nouveau_adherent)
            flash('Adhérent ajouté avec succès.', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l\'ajout : {str(e)}", 'danger')

    return render_template('ajouter_adherent.html', entraineurs=entraineurs, groupes=groupes)

@app.route('/gerer_adherent', methods=['POST','GET'])
def gerer_adherent():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    adherents=Adherent.query.all()
    return render_template('gerer_adherent.html',adherents=adherents)


@app.route('/modifier_adherent/<int:id>', methods=['GET', 'POST'])
def modifier_adherent(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    # Récupérer l'adhérent par son ID, sinon retourner une erreur 404 si non trouvé
    groupes = Groupe.query.all()
    nom_groupes = [groupe.nom_groupe for groupe in groupes]
    adherent = Adherent.query.get_or_404(id)

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
        return redirect(url_for('gerer_adherent'))

    # Get list of all trainers
    entraineurs = Entraineur.query.all()
    return render_template('modifier_adherent.html', adherent=adherent, entraineurs=entraineurs,nom_groupes=nom_groupes)
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
            # Création d'un nouvel entraîneur
            nouveau_entraineur = Entraineur(
                nom=request.form['nom'],
                prenom=request.form['prenom'],
                sexe=request.form['sexe'],
                type_abonnement=request.form['type_abonnement'],
                tel=request.form.get('tel'),
                addresse =request.form.get('addresse'),
                compte_bancaire=request.form.get('compte_bancaire'),
                status='Actif',
            )
            # Ajout de l'entraîneur dans la base de données
            print('nouveau entraineur')
            print(nouveau_entraineur)
            
            # Création de l'utilisateur
            print('nouveau user')
            print(nouveau_entraineur.nom)
            print(nouveau_entraineur.prenom)

            # Mot de passe par défaut pour l'entraîneur
            password = 'entraineur'
            user_nom = nouveau_entraineur.nom
            user_nom=user_nom.replace(" ", "").lower()
            user_prenom = nouveau_entraineur.prenom
            user_prenom=user_prenom.replace(" ", "").lower()
            user = str(user_nom) + '.' + str(user_prenom)
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            print(f"Mot de passe haché : {hashed_password}")

            # Assignation du rôle
            role = 'entraineur'

            # Création de l'utilisateur associé à l'entraîneur
            new_utilisateur = User(utilisateur=user, password=hashed_password, role=role)
            print(f"Utilisateur créé : {new_utilisateur}")

            # Ajout de l'utilisateur et de l'entraîneur à la base de données
            db.session.add(new_utilisateur)
            db.session.add(nouveau_entraineur)
            db.session.commit()  # Commit pour enregistrer dans la base de données

            # Confirmation de l'ajout
            flash("Utilisateur ajouté avec succès.", "success")
            flash('L\'entraîneur a été ajouté avec succès !', 'success')

            return redirect(url_for('admin'))  # Redirection vers la page d'administration

        except Exception as e:
            db.session.rollback()  # Annule les modifications en cas d'erreur
            flash(f"Erreur lors de l'ajout de l'entraîneur ou de l'utilisateur : {str(e)}", 'danger')
            print(f"Erreur : {str(e)}")

    return render_template('ajouter_entraineur.html')



@app.route('/gerer_entraineur',methods=['POST','GET'])
def gerer_entraineur():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    entraineurs=Entraineur.query.all()
    return render_template('gerer_entraineur.html',entraineurs=entraineurs)

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
        entraineur.type_abonnement = request.form['type_abonnement']
        entraineur.enfant = request.form['enfant']
        entraineur.status = request.form['status']
        
        try:
            db.session.commit()
            flash("Les informations de l'entraîneur ont été mises à jour avec succès.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la mise à jour : {str(e)}", "danger")
        return redirect(url_for('gerer_entraineur'))
    
    return render_template('modifier_entraineur.html', entraineur=entraineur)

@app.route('/supprimer_entraineur/<int:id>', methods=['POST', 'GET'])
def supprimer_entraineur(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    
    entraineur = Entraineur.query.get_or_404(id)
    
    try:
        db.session.delete(entraineur)
        db.session.commit()
        flash("L'entraîneur a été supprimé avec succès.", "success")
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

@app.route('/paiement', methods=['GET', 'POST'])
def paiement():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    adherent = None
    paiements = []
    cotisation = 0
    remise = 0  # Remise en pourcentage
    remise_montant = 0  # Montant de la remise en valeur absolue
    reste_a_payer = 0  # Nouvelle variable pour le reste à payer
    numero_carnet = 1  # Initialisation par défaut
    numero_bon = 1  # Initialisation par défaut
    #generation de code saison
    aujourdhui = datetime.now()
    debut_saison = datetime(aujourdhui.year, 9, 1)  # 1er septembre de l'année en cours
    
    if aujourdhui < debut_saison:
        code_saison= f"S{aujourdhui.year}"
    else:
        code_saison= f"S{aujourdhui.year + 1}"  # Génération dynamique du code saison

    cotisations = Cotisation.query.all()

    if request.method == 'POST':
        # Recherche de l'adhérent
        matricule = request.form.get('matricule')
        adherent = Adherent.query.filter_by(matricule=matricule).first()

        if adherent:
            # Récupérer les paiements associés à cet adhérent
            paiements = Paiement.query.filter_by(matricule_adherent=matricule).all()

            # Si c'est le premier paiement, initialisez la cotisation et la remise
            if not paiements:
                cotisation = float(request.form.get('cotisation', 0))
                remise = float(request.form.get('remise', 0))  # Remise en pourcentage
                remise_montant = cotisation * (remise / 100)  # Calcul du montant de la remise
            else:
                cotisation = paiements[0].cotisation
                remise = paiements[0].remise  # Remise en pourcentage
                remise_montant = cotisation * (remise / 100)  # Calcul du montant de la remise

            # Récupérer le dernier paiement de la table paiements
            dernier_paiement = Paiement.query.order_by(Paiement.id_paiement.desc()).first()
            if dernier_paiement:
                numero_carnet = dernier_paiement.numero_carnet
                numero_bon = dernier_paiement.numero_bon + 1

                # Si le numéro de bon dépasse 50, passer au carnet suivant
                if numero_bon > 50:
                    numero_carnet += 1
                    numero_bon = 1

            # Calcul du reste à payer
            reste_a_payer = cotisation - remise_montant - sum([p.montant_paye for p in paiements])

            # Gestion du paiement
            if request.form.get('montant_paye'):
                montant_paye = float(request.form.get('montant_paye'))
                type_reglement = request.form.get('type_reglement')
                numero_cheque = request.form.get('numero_cheque') if type_reglement == 'chèque' else None
                banque = request.form.get('banque') if type_reglement == 'chèque' else None

                paiement_total = cotisation - remise_montant
                montant_restant = paiement_total - sum([p.montant_paye for p in paiements]) - montant_paye

                # Créer un nouveau paiement
                nouveau_paiement = Paiement(
                    matricule_adherent=matricule,
                    montant=paiement_total,
                    montant_paye=montant_paye,
                    montant_reste=montant_restant,
                    type_reglement=type_reglement,
                    numero_cheque=numero_cheque,
                    banque=banque,
                    cotisation=cotisation,
                    remise=remise,  # Stocker le pourcentage de remise
                    numero_bon=numero_bon,
                    numero_carnet=numero_carnet,
                    code_saison=code_saison
                )

                db.session.add(nouveau_paiement)
                db.session.commit()
                # Exemple d'utilisation
                generer_bon_paiement(matricule_adherent=matricule, montant_paye=montant_paye, type_paiement=type_reglement, code_saison=code_saison, id_bon=numero_bon, id_carnet=numero_carnet)


                # Recharger les paiements pour mise à jour
                paiements = Paiement.query.filter_by(matricule_adherent=matricule).all()
                flash("Paiement enregistré avec succès.", "success")
        else:
            flash("Adhérent non trouvé.", "danger")

    # Calcul des sommes
    total_montant_paye = sum([p.montant_paye for p in paiements])

    return render_template(
        'paiement.html',
        adherent=adherent,
        paiements=paiements,
        cotisation=cotisation,
        remise=remise,
        remise_montant=remise_montant,
        reste_a_payer=reste_a_payer,
        total_montant_paye=total_montant_paye,
        numero_carnet=numero_carnet,
        numero_bon=numero_bon,
        code_saison=code_saison,
        cotisations=cotisations
    )



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
    print("Payment types:", types_paiement)
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

# Define the models here
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
    ancien_abonne = db.Column(db.String(50), nullable=False)
    matricule = db.Column(db.Integer, unique=True, nullable=False)
    groupe = db.Column(db.String(100), nullable=True)
    entraineur = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    paye = db.Column(db.Enum('O', 'N'), nullable=False)
    status = db.Column(db.Enum('Actif', 'Non-Actif'), nullable=False)

    def __repr__(self):
        return f'<Adherent {self.nom} {self.prenom}>'

    def to_dict(self):
        return {
            "adherent_id": self.adherent_id,
            "nom": self.nom,
            "prenom": self.prenom,
            "date_naissance": self.date_naissance.isoformat(),  # Convert date to string format
            "date_inscription": self.date_inscription.isoformat(),
            "sexe": self.sexe,
            "tel1": self.tel1,
            "tel2": self.tel2,
            "type_abonnement": self.type_abonnement,
            "ancien_abonne": self.ancien_abonne,
            "matricule": self.matricule,
            "groupe": self.groupe,
            "entraineur": self.entraineur,
            "email": self.email,
            "paye": self.paye,
            "status": self.status
        }

class Entraineur(db.Model):
    __tablename__ = 'entraineur'
    
    id_entraineur = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    sexe = db.Column(db.Enum('M', 'F'), nullable=False)
    type_abonnement = db.Column(db.String(50), nullable=True, default=None)
    tel = db.Column(db.String(100), nullable=True)
    addresse = db.Column(db.String(100), nullable=True)
    compte_bancaire = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Enum('Actif', 'Non-Actif'), nullable=False)

    def __repr__(self):
        return f'<Entraineur {self.nom} {self.prenom}>'



class Groupe(db.Model):
    __tablename__ = 'groupe'
    
    id_groupe = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_groupe = db.Column(db.String(100), nullable=False)
    entraineur_nom = db.Column(db.String(50), nullable=False)
    type_abonnement = db.Column(db.String(50), nullable=False)
    categorie = db.Column(db.String(50), nullable=False)

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
    terrain = db.Column(db.Integer, nullable=False)
    adherents_matricules = db.Column(db.Text,nullable=True)

    def __init__(self, date, heure_debut, groupe, entraineur, terrain):
        self.date = date
        self.heure_debut = heure_debut
        
        # Ligne corrigée ▼
        start = datetime.combine(date.today(), heure_debut)  # Utilisez 'date.today()'
        
        self.heure_fin = (start + timedelta(minutes=90)).time()
        self.groupe = groupe
        self.entraineur = entraineur
        self.terrain = terrain


class Presence(db.Model):
    __tablename__ = 'presence'
    
    id_presence = db.Column(db.Integer, primary_key=True, autoincrement=True)
    groupe_nom = db.Column(db.String(100), nullable=False)
    adherent_matricule = db.Column(db.String(50), nullable=False)
    entraineur_nom = db.Column(db.String(100), nullable=False)
    date_seance = db.Column(db.Date, nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    est_present = db.Column(db.Enum('O', 'N'), nullable=False, default='N')

    def __repr__(self):
        return f'<Presence {self.groupe_nom} - {self.adherent_matricule} - {self.date_seance}>'

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

def generer_bon_paiement(matricule_adherent, montant_paye, type_paiement, code_saison, id_bon, id_carnet):
    """
    Génère un bon de paiement en PDF et en PNG avec les informations de l'adhérent.

    :param matricule_adherent: ID de l'adhérent
    :param montant_paye: Montant payé
    :param type_paiement: Méthode de paiement (ex: "Espèce", "Chèque")
    :param code_saison: Code de la saison (ex: "S2025")
    :param id_bon: Numéro du bon de paiement
    :param id_carnet: Numéro du carnet
    """
    # Récupérer les infos de l'adhérent depuis la base de données
    adherent = Adherent.query.filter_by(matricule=matricule_adherent).first()
    if not adherent:
        print(f"Erreur : Aucun adhérent trouvé avec le matricule {matricule_adherent}")
        return

    nom_complet = f"{adherent.prenom} {adherent.nom}"  # Ex: "Ahmed Mustapha"

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

    # Convertir le PDF en PNG avec PyMuPDF (sans Poppler)
    
    page = doc[0]  # Première page
    pix = page.get_pixmap()  # Conversion en image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save(png_filename, "PNG")  # Sauvegarde l'image
    doc.close()

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

    # Afficher les totaux
    print(f"Total Montant: {results.total_montant:.2f}")
    print(f"Total Montant Payé: {results.total_montant_paye:.2f}")
    print(f"Total Montant Restant: {results.total_montant_reste:.2f}")



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
            print(int(data['qualifies_par_groupe']))
            print(int(data['joueurs_par_groupe']))
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


class AutresPaiements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    company_name = db.Column(db.String(100), nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    rib = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    documents = db.Column(db.JSON, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.isoformat(),
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'company_name': self.company_name,
            'bank_name': self.bank_name,
            'rib': self.rib,
            'location': self.location,
            'documents': self.documents or []
        }

    @staticmethod
    def from_dict(data):
        return AutresPaiements(
            amount=float(data['amount']),
            category=data['category'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            description=data['description'],
            company_name=data['company_name'],
            bank_name=data['bank_name'],
            rib=data.get('rib'),
            location=data.get('location'),
            documents=[]
        )

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

@app.route('/autres-paiements')
def show_autres_paiements():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    return render_template('autres_paiements.html')

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
        print("Received form data:", request.form)
        print("Received files:", request.files)

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
        print("Error adding transaction:", str(e))
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
        print(f"Error serving document: {str(e)}")
        return jsonify({'error': 'Error serving document'}), 500







from flask import jsonify, render_template, request
from sqlalchemy import or_
from datetime import datetime, timedelta
import pytz

@app.route('/situation-adherent')
def show_situation_adherent():
    return render_template('situation-adherent.html')

@app.route('/api/search-adherent')
def search_adherent():
    search_term = request.args.get('term', '')
    if not search_term:
        return jsonify([])

    adherents = Adherent.query.filter(
        or_(
            Adherent.matricule.cast(db.String).like(f'%{search_term}%'),
            Adherent.nom.ilike(f'%{search_term}%'),
            Adherent.prenom.ilike(f'%{search_term}%')
        )
    ).limit(10).all()

    return jsonify([{
        'id': a.adherent_id,
        'matricule': a.matricule,
        'nom': a.nom,
        'prenom': a.prenom,
        'label': f"{a.matricule} - {a.nom} {a.prenom}"
    } for a in adherents])

@app.route('/api/situation-adherent/<int:matricule>')
def get_situation_adherent(matricule):
    # Get adherent basic info
    adherent = Adherent.query.filter_by(matricule=matricule).first_or_404()
    
    # Get payment information
    paiements = Paiement.query.filter_by(matricule_adherent=str(matricule)).all()
    total_paye = sum(p.montant_paye for p in paiements)
    total_a_payer = sum(p.montant for p in paiements)
    total_remise = sum(p.remise for p in paiements)
    
    # Get presence information
    presences = Presence.query.filter_by(adherent_matricule=str(matricule)).all()
    nombre_presences = sum(1 for p in presences if p.est_present == 'O')
    
    # Get next session
    now = datetime.now(pytz.timezone('Europe/Paris'))
    prochaine_seance = Presence.query.filter(
        Presence.adherent_matricule == str(matricule),
        Presence.date_seance >= now.date()
    ).order_by(Presence.date_seance, Presence.heure_debut).first()
    
    # Prepare payment history
    historique_paiements = [{
        'date': p.date_paiement.strftime('%Y-%m-%d'),
        'montant': p.montant,
        'montant_paye': p.montant_paye,
        'type_reglement': p.type_reglement,
        'numero_cheque': p.numero_cheque,
        'banque': p.banque,
        'numero_bon': p.numero_bon,
        'numero_carnet': p.numero_carnet,
        'remise': p.remise
    } for p in paiements]

    return jsonify({
        'adherent': adherent.to_dict(),
        'paiements': {
            'total_paye': total_paye,
            'total_a_payer': total_a_payer,
            'total_remise': total_remise,
            'reste_a_payer': total_a_payer - total_paye - total_remise,
            'historique': historique_paiements
        },
        'presences': {
            'total': len(presences),
            'present': nombre_presences,
            'absent': len(presences) - nombre_presences
        },
        'prochaine_seance': {
            'date': prochaine_seance.date_seance.strftime('%Y-%m-%d') if prochaine_seance else None,
            'heure': prochaine_seance.heure_debut.strftime('%H:%M') if prochaine_seance else None,
            'groupe': prochaine_seance.groupe_nom if prochaine_seance else None
        } if prochaine_seance else None
    })




from flask import jsonify, render_template, request
from sqlalchemy import func
from datetime import datetime, timedelta
import pytz

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
def get_paiement_summary():
    try:
        date_start = request.args.get('start_date', datetime.now().replace(day=1).strftime('%Y-%m-%d'))
        date_end = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        start_date = datetime.strptime(date_start, '%Y-%m-%d')
        end_date = datetime.strptime(date_end, '%Y-%m-%d')

        # Obtenir les remises uniques par adhérent
        adherents_remises = db.session.query(
            Paiement.matricule_adherent,
            func.max(Paiement.cotisation).label('cotisation'),  # Une seule cotisation par adhérent
            func.max(Paiement.remise).label('remise')  # Un seul pourcentage de remise par adhérent
        ).filter(
            Paiement.date_paiement.between(start_date, end_date + timedelta(days=1))
        ).group_by(Paiement.matricule_adherent).all()

        # Calculer le total des remises
        total_remise = sum(
            (adherent.cotisation * adherent.remise / 100.0)
            for adherent in adherents_remises
        )

        # Obtenir les totaux généraux
        totals = db.session.query(
            func.sum(Paiement.montant).label('total_a_payer'),
            func.sum(Paiement.montant_paye).label('total_paye'),
            func.count(distinct(Paiement.matricule_adherent)).label('nombre_adherents'),
            func.count(Paiement.id_paiement).label('nombre_transactions')
        ).filter(
            Paiement.date_paiement.between(start_date, end_date + timedelta(days=1))
        ).first()

        # Get payment methods distribution
        payment_methods = db.session.query(
            Paiement.type_reglement,
            func.count(Paiement.id_paiement).label('count'),
            func.sum(Paiement.montant_paye).label('total')
        ).filter(
            Paiement.date_paiement.between(start_date, end_date + timedelta(days=1))
        ).group_by(Paiement.type_reglement).all()

        # Get daily payments
        daily_payments = db.session.query(
            func.date(Paiement.date_paiement).label('date'),
            func.sum(Paiement.montant_paye).label('total')
        ).filter(
            Paiement.date_paiement.between(start_date, end_date + timedelta(days=1))
        ).group_by(func.date(Paiement.date_paiement)).all()

        return jsonify({
            'summary': {
                'total_a_payer': float(totals.total_a_payer or 0),
                'total_paye': float(totals.total_paye or 0),
                'total_remise': float(total_remise),
                'reste_a_payer': float((totals.total_a_payer or 0) - (totals.total_paye or 0) - total_remise),
                'nombre_adherents': totals.nombre_adherents or 0,
                'nombre_transactions': totals.nombre_transactions or 0
            },
            'payment_methods': [{
                'method': method.type_reglement or 'Non spécifié',
                'count': method.count,
                'total': float(method.total or 0)
            } for method in payment_methods],
            'daily_payments': [{
                'date': payment.date.strftime('%Y-%m-%d'),
                'total': float(payment.total or 0)
            } for payment in daily_payments]
        })
    except Exception as e:
        print(f"Error in get_paiement_summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/situation-paiement/transactions')
def get_paiement_transactions():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        date_start = request.args.get('start_date')
        date_end = request.args.get('end_date')
        search_term = request.args.get('search', '')

        # Obtenir les informations de base des transactions
        query = db.session.query(
            Paiement,
            # Sous-requête pour obtenir la remise une seule fois par adhérent
            db.session.query(
                (Paiement.cotisation * Paiement.remise / 100.0).label('montant_remise')
            ).filter(
                Paiement.matricule_adherent == Paiement.matricule_adherent
            ).order_by(
                Paiement.date_paiement
            ).limit(1).as_scalar().label('montant_remise_adherent')
        )

        if date_start and date_end:
            start_date = datetime.strptime(date_start, '%Y-%m-%d')
            end_date = datetime.strptime(date_end, '%Y-%m-%d')
            query = query.filter(Paiement.date_paiement.between(start_date, end_date + timedelta(days=1)))

        if search_term:
            query = query.filter(
                db.or_(
                    Paiement.matricule_adherent.ilike(f'%{search_term}%'),
                    Paiement.type_reglement.ilike(f'%{search_term}%'),
                    Paiement.banque.ilike(f'%{search_term}%')
                )
            )

        # Get total count for pagination
        total_count = query.count()

        # Apply pagination
        transactions = query.order_by(Paiement.date_paiement.desc())\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()

        return jsonify({
            'total': total_count,
            'pages': (total_count + per_page - 1) // per_page,
            'current_page': page,
            'transactions': [{
                'id': t.Paiement.id_paiement,
                'matricule': t.Paiement.matricule_adherent,
                'date': t.Paiement.date_paiement.strftime('%Y-%m-%d %H:%M:%S'),
                'montant': float(t.Paiement.montant),
                'montant_paye': float(t.Paiement.montant_paye),
                'montant_reste': float(t.Paiement.montant_reste),
                'type_reglement': t.Paiement.type_reglement,
                'numero_cheque': t.Paiement.numero_cheque,
                'banque': t.Paiement.banque,
                'remise': float(t.Paiement.remise),
                'montant_remise': float(t.montant_remise_adherent if t.montant_remise_adherent else 0),
                'cotisation': float(t.Paiement.cotisation),
                'numero_bon': t.Paiement.numero_bon,
                'numero_carnet': t.Paiement.numero_carnet
            } for t in transactions]
        })
    except Exception as e:
        print(f"Error in get_paiement_transactions: {str(e)}")
        return jsonify({'error': str(e)}), 500


from sqlalchemy import text, literal

@app.route('/situation-terrains')
def show_situation_terrains():
    if 'user_id' not in session:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    return render_template('situation-terrains.html')


@app.route('/api/terrains/disponibilite')
def check_terrain_availability():
    try:
        date_str = request.args.get('date')  # Format attendu: YYYY-MM-DD
        heure_debut_str = request.args.get('heure_debut')
        heure_fin_str = request.args.get('heure_fin')
        
        print("Données reçues de l'utilisateur:")
        print(f"date_str: {date_str}")
        print(f"heure_debut_str: {heure_debut_str}")
        print(f"heure_fin_str: {heure_fin_str}")

        if not date_str or not heure_debut_str:
            return jsonify({'error': 'Date et heure de début requises'}), 400

        # Conversion simple des chaînes en date et heures
        date_check = datetime.strptime(date_str, '%Y-%m-%d').date()
        heure_debut = datetime.strptime(heure_debut_str, '%H:%M').time()
        heure_fin = datetime.strptime(heure_fin_str, '%H:%M').time() if heure_fin_str else None

        terrains_status = []
        for terrain_num in range(1, 10):
            # Vérification des locations
            locations = LocationTerrain.query.filter(
                LocationTerrain.numero_terrain == terrain_num,
                LocationTerrain.date_location == date_check
            ).all()

            print(f"\nTerrain {terrain_num} - Date vérifiée: {date_check}")
            print(f"Locations trouvées: {len(locations)}")
            for loc in locations:
                print(f"Location: date={loc.date_location}, {loc.heure_debut}-{loc.heure_fin}, {loc.locateur}")

            # Vérifier si une location chevauche l'horaire demandé
            location_conflict = any(
                (loc.heure_debut <= heure_debut < loc.heure_fin) or
                (loc.heure_debut < heure_fin <= loc.heure_fin) or
                (heure_debut <= loc.heure_debut and heure_fin >= loc.heure_fin)
                for loc in locations
            )

            # Vérification des séances
            seances = Seance.query.filter(
                Seance.terrain == terrain_num,
                Seance.date == date_check
            ).all()

            seance_conflict = any(
                (seance.heure_debut <= heure_debut < seance.heure_fin) or
                (seance.heure_debut < heure_fin <= seance.heure_fin) or
                (heure_debut <= seance.heure_debut and heure_fin >= seance.heure_fin)
                for seance in seances
            )

            # Création du statut du terrain
            terrain_status = {
                'numero': terrain_num,
                'disponible': not (location_conflict or seance_conflict),
                'occupation': None
            }

            # Ajout des informations d'occupation si le terrain est occupé
            if location_conflict:
                location = next(loc for loc in locations if 
                    (loc.heure_debut <= heure_debut < loc.heure_fin) or
                    (loc.heure_debut < heure_fin <= loc.heure_fin) or
                    (heure_debut <= loc.heure_debut and heure_fin >= loc.heure_fin)
                )
                terrain_status['occupation'] = {
                    'type': 'location',
                    'heure_debut': location.heure_debut.strftime('%H:%M'),
                    'heure_fin': location.heure_fin.strftime('%H:%M'),
                    'locateur': location.locateur
                }
            elif seance_conflict:
                seance = next(seance for seance in seances if 
                    (seance.heure_debut <= heure_debut < seance.heure_fin) or
                    (seance.heure_debut < heure_fin <= seance.heure_fin) or
                    (heure_debut <= seance.heure_debut and heure_fin >= seance.heure_fin)
                )
                terrain_status['occupation'] = {
                    'type': 'seance',
                    'heure_debut': seance.heure_debut.strftime('%H:%M'),
                    'heure_fin': seance.heure_fin.strftime('%H:%M'),
                    'groupe': seance.groupe,
                    'entraineur': seance.entraineur
                }

            terrains_status.append(terrain_status)

        return jsonify(terrains_status)
    except Exception as e:
        print(f"Erreur dans check_terrain_availability: {str(e)}")
        return jsonify({'error': str(e)}), 500 

@app.route('/api/terrains/stats')
def get_terrain_stats():
    try:
        date_start = request.args.get('start_date', 
            (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        date_end = request.args.get('end_date', 
            datetime.now().strftime('%Y-%m-%d'))

        # Statistiques des locations
        locations_stats = db.session.query(
            LocationTerrain.numero_terrain,
            func.count(LocationTerrain.id_location).label('total_locations'),
            func.sum(LocationTerrain.montant_location).label('total_montant')
        ).filter(
            LocationTerrain.date_location.between(date_start, date_end)
        ).group_by(LocationTerrain.numero_terrain).all()

        # Statistiques des séances
        seances_stats = db.session.query(
            Seance.terrain,
            func.count(Seance.seance_id).label('total_seances')
        ).filter(
            Seance.date.between(date_start, date_end)
        ).group_by(Seance.terrain).all()

        statistics = {}
        for terrain_num in range(1, 10):
            statistics[terrain_num] = {
                'locations': 0,
                'montant_total': 0,
                'seances': 0
            }

        for stat in locations_stats:
            statistics[stat.numero_terrain]['locations'] = stat.total_locations
            statistics[stat.numero_terrain]['montant_total'] = float(stat.total_montant or 0)

        for stat in seances_stats:
            statistics[stat.terrain]['seances'] = stat.total_seances

        return jsonify({
            'statistics': statistics,
            'period': {
                'start': date_start,
                'end': date_end
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/terrains/historique')
def get_terrain_history():
    try:
        terrain_num = request.args.get('terrain')
        date_start = request.args.get('start_date')
        date_end = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        print(f"\nRequête historique reçue:")
        print(f"Terrain: {terrain_num}")
        print(f"Date début: {date_start}")
        print(f"Date fin: {date_end}")

        if not terrain_num:
            return jsonify({'error': 'Numéro de terrain requis'}), 400

        # Convertir les dates
        start_date = datetime.strptime(date_start, '%Y-%m-%d').date()
        end_date = datetime.strptime(date_end, '%Y-%m-%d').date()

        print(f"Dates après conversion:")
        print(f"Start: {start_date}")
        print(f"End: {end_date}")

        # Récupérer les locations
        locations = LocationTerrain.query.filter(
            LocationTerrain.numero_terrain == int(terrain_num),
            LocationTerrain.date_location.between(start_date, end_date)
        ).all()

        print(f"Locations trouvées: {len(locations)}")
        for loc in locations:
            print(f"Location: {loc.date_location}, {loc.heure_debut}-{loc.heure_fin}, {loc.locateur}")

        # Récupérer les séances
        seances = Seance.query.filter(
            Seance.terrain == int(terrain_num),
            Seance.date.between(start_date, end_date)
        ).all()

        print(f"Séances trouvées: {len(seances)}")
        for seance in seances:
            print(f"Séance: {seance.date}, {seance.heure_debut}-{seance.heure_fin}, {seance.groupe}")

        # Combiner les résultats
        historique = []
        
        for loc in locations:
            historique.append({
                'date': loc.date_location.strftime('%Y-%m-%d'),
                'heure_debut': loc.heure_debut.strftime('%H:%M'),
                'heure_fin': loc.heure_fin.strftime('%H:%M'),
                'utilisateur': loc.locateur,
                'montant': float(loc.montant_location),
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

        # Trier par date et heure
        historique.sort(key=lambda x: (x['date'], x['heure_debut']), reverse=True)

        # Pagination
        total = len(historique)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_historique = historique[start_idx:end_idx]

        print(f"Nombre total d'entrées: {total}")
        print(f"Entrées paginées: {len(paginated_historique)}")

        return jsonify({
            'historique': paginated_historique,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page
        })

    except Exception as e:
        print(f"Erreur dans get_terrain_history: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



@app.route('/api/adherents/<groupe>')
def get_adherents_groupe(groupe):
    adherents = Adherent.query.filter_by(groupe=groupe).all()
    return jsonify([{
        'matricule': a.matricule,
        'nom': a.nom,
        'prenom': a.prenom
    } for a in adherents])

@app.route('/api/presences', methods=['POST'])
def save_presences():
    presences = request.json
    try:
        for p in presences:
            presence = Presence(
                groupe_nom=p['groupe_nom'],
                adherent_matricule=p['adherent_matricule'],
                entraineur_nom=p['entraineur_nom'],
                date_seance=datetime.strptime(p['date_seance'], '%Y-%m-%d').date(),
                heure_debut=datetime.strptime(p['heure_debut'], '%H:%M').time(),
                est_present=p['est_present']
            )
            db.session.add(presence)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})




@app.route('/situation_presence')
def situation_presence():
    # Récupérer les données pour les listes déroulantes
    groupes = db.session.query(Groupe.categorie).distinct().all()
    entraineurs = db.session.query(Entraineur.nom, Entraineur.prenom).distinct().all()
    terrains = list(range(1, 10))  # Terrains de 1 à 9

    return render_template('situation_presence.html',
                         groupes=[g[0] for g in groupes],
                         entraineurs=entraineurs,
                         terrains=terrains)

@app.route('/api/search_adherent_presence')
def search_adherent_presence():
    search_type = request.args.get('type')  # 'matricule' ou 'nom'
    query = request.args.get('query', '').strip()
    
    if not query:
        return jsonify([])

    if search_type == 'matricule':
        adherents = Adherent.query.filter(
            Adherent.matricule.ilike(f'%{query}%')
        ).limit(10).all()
    else:
        adherents = Adherent.query.filter(
            or_(
                Adherent.nom.ilike(f'%{query}%'),
                Adherent.prenom.ilike(f'%{query}%')
            )
        ).limit(10).all()

    return jsonify([{
        'matricule': a.matricule,
        'nom': a.nom,
        'prenom': a.prenom
    } for a in adherents])

@app.route('/api/presences/search')
def search_presences():
    # Récupérer les paramètres
    date = request.args.get('date')
    groupe = request.args.get('groupe')
    entraineur = request.args.get('entraineur')
    adherent = request.args.get('adherent')
    heure_debut = request.args.get('heure_debut')
    heure_fin = request.args.get('heure_fin')
    terrain = request.args.get('terrain')

    # Construire la requête de base
    query = db.session.query(
        Presence,
        Adherent.nom.label('adherent_nom'),
        Adherent.prenom.label('adherent_prenom')
    ).join(Adherent, Presence.adherent_matricule == Adherent.matricule)

    # Appliquer les filtres
    if date:
        query = query.filter(Presence.date_seance == datetime.strptime(date, '%Y-%m-%d').date())
    
    if groupe:
        query = query.filter(Presence.groupe_nom == groupe)
    
    if entraineur:
        query = query.filter(Presence.entraineur_nom == entraineur)
    
    if adherent:
        query = query.filter(Presence.adherent_matricule == adherent)
    
    if heure_debut:
        query = query.filter(Presence.heure_debut >= datetime.strptime(heure_debut, '%H:%M').time())
    
    if heure_fin:
        query = query.filter(Presence.heure_debut <= datetime.strptime(heure_fin, '%H:%M').time())

    # Exécuter la requête
    presences = query.all()

    # Formater les résultats
    results = []
    for p, nom, prenom in presences:
        results.append({
            'date': p.date_seance.strftime('%Y-%m-%d'),
            'heure': p.heure_debut.strftime('%H:%M'),
            'groupe': p.groupe_nom,
            'adherent': f"{nom} {prenom}",
            'matricule': p.adherent_matricule,
            'entraineur': p.entraineur_nom,
            'statut': 'Présent(e)' if p.est_present == 'O' else 'Absent(e)',
            'classe_statut': 'present' if p.est_present == 'O' else 'absent'
        })

    return jsonify(results)

@app.route('/export_presences')
def export_presences():
    # Logique d'exportation similaire à la recherche mais au format Excel
    # Utilisez pandas pour créer le fichier Excel
    results = search_presences().get_json()
    
    df = pd.DataFrame(results)
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Présences')
    
    # Formatage du fichier Excel
    workbook = writer.book
    worksheet = writer.sheets['Présences']
    
    # Formats
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'bg_color': '#D9EAD3',
        'border': 1
    })
    
    # Appliquer les formats
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(col_num, col_num, 15)
    
    writer.save()
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'presences_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )


# Running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
