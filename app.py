from flask import send_file
from flask import send_from_directory
from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time, timedelta
import hashlib
import pytz


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

    return render_template('admin.html')

from sqlalchemy import or_

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


@app.route('/directeur_technique', methods=['GET', 'POST'])
def directeur_technique():
    if 'user_id' not in session or session.get('role') != 'directeur_technique':
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
        terrains=range(1, 8),
        seances_par_groupe=seances_par_groupe
    )
@app.route('/ajouter_seance', methods=['POST'])
def ajouter_seance():
    data = request.get_json()
    
    # Récupérer les données
    groupe = Groupe.query.get(data['groupe_id'])
    if not groupe:
        return jsonify({"error": "Groupe introuvable"}), 404

    try:
        # Conversion des dates/heures
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        heure_debut = datetime.strptime(data['heure_debut'], '%H:%M').time()
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
                # Conflit de terrain
                (Seance.terrain == data['terrain']) |
                # Conflit d'entraîneur ▼
                (Seance.entraineur == groupe.entraineur_nom) |
                # Conflit de groupe ▼
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
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_session/<int:session_id>', methods=['GET'])
def api_get_session(session_id):
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

@app.route('/supprimer_adherent_groupe/<int:adherent_id>', methods=['POST', 'GET'])
def supprimer_adherent_groupe(adherent_id):
    if 'user_id' not in session or session.get('role') != 'entraineur':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    adherent = Adherent.query.get_or_404(adherent_id)
    adherent.groupe = None
    adherent.entraineur = None
    db.session.commit()
    flash("L'adhérent a été retiré du groupe.", "success")
    return redirect(url_for('entraineur'))  # Retour à la page de l'entraîneur

@app.route('/ajouter_adherent_groupe/<int:groupe_id>', methods=['POST'])
def ajouter_adherent_groupe(groupe_id):
    matricule = request.json.get('matricule')
    groupe = Groupe.query.get(groupe_id)
    if not groupe:
        return jsonify({"error": "Groupe non trouvé"}), 404

    adherent = Adherent.query.filter_by(matricule=matricule).first()
    if not adherent:
        return jsonify({"error": "Adhérent non trouvé"}), 404

    if adherent.groupe:
        return jsonify({"error": "Cet adhérent est déjà associé à un groupe."}), 400

    adherent.groupe = groupe.nom_groupe
    adherent.entraineur = groupe.entraineur_nom
    db.session.commit()

    return jsonify({"message": "Adhérent ajouté avec succès"}), 200
@app.route('/ajouter_groupe', methods=['POST'])
def ajouter_groupe():
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
    if 'user_id' not in session or session.get('role') != 'directeur_technique':
        return jsonify({"error": "Accès non autorisé"}), 403

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

@app.route('/api/get_adherents_groupe/<int:groupe_id>', methods=['GET'])
def api_get_adherents_groupe(groupe_id):
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

    # Récupérer les données du front-end
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

        
        # Vérifier si le groupe est not None
        if nom_groupe is not None :
            # Vérifier si le groupe existe déjà
            groupe_exist = Groupe.query.filter_by(nom_groupe=nom_groupe).first()

            # Si le groupe n'existe pas, le créer
            if not groupe_exist:
                nouvel_groupe = Groupe(
                    nom_groupe=nom_groupe,
                    entraineur_nom=entraineur_nom,
                    type_abonnement=type_abonnement
                )
                db.session.add(nouvel_groupe)
                db.session.commit()

        
        

        try:
            db.session.add(nouveau_adherent)
            db.session.commit()
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
    return render_template('modifier_adherent.html', adherent=adherent, entraineurs=entraineurs)
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
                    numero_carnet=numero_carnet
                )

                db.session.add(nouveau_paiement)
                db.session.commit()

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
        numero_bon=numero_bon
    )

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

    def __init__(self, date, heure_debut, groupe, entraineur, terrain):
        self.date = date
        self.heure_debut = heure_debut
        
        # Ligne corrigée ▼
        start = datetime.combine(date.today(), heure_debut)  # Utilisez 'date.today()'
        
        self.heure_fin = (start + timedelta(minutes=90)).time()
        self.groupe = groupe
        self.entraineur = entraineur
        self.terrain = terrain


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
    def __repr__(self):
        return f"<Paiement {self.id_paiement} - Matricule: {self.matricule_adherent}>"




import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_bon_de_recette_pdf(adherent, numero_cheque, banque):
    # Créer le dossier "bon_de_recette" s'il n'existe pas
    directory = 'bon_de_recette'
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
    c.drawString(100, 690, f"Type de règlement : {adherent.type_reglement}")
    c.drawString(100, 670, f"Numéro de Chèque : {numero_cheque}")
    c.drawString(100, 650, f"Banque : {banque}")
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

# Running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
