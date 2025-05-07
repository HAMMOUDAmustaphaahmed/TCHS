from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from datetime import datetime, date, time, timedelta
import hashlib
from models import db, User, Adherent, Entraineur, Presence, Groupe, Seance, Message, Paiement
from functions import generate_bon_de_recette_pdf, get_totals_simple, generate_excel, generate_pdf
import pytz
from sqlalchemy import or_

# Create the blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('signin.html')

@main_bp.route('/presentation')
def presentation():
    return render_template('presentation.html')

@main_bp.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('main.login'))
    return render_template('admin.html')

@main_bp.route('/entraineur', methods=['GET', 'POST'])
def entraineur():
    if 'user_id' not in session or session.get('role') != 'entraineur':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('main.login'))

    username = session.get('username')
    if not username:
        flash("Session invalide.", "danger")
        return redirect(url_for('main.login'))

    try:
        nom, prenom = username.split('.')
    except ValueError:
        flash("Format du nom d'utilisateur invalide.", "danger")
        return redirect(url_for('main.login'))

    entraineur = Entraineur.query.filter_by(nom=nom, prenom=prenom).first()
    if not entraineur:
        flash("Entraîneur introuvable.", "danger")
        return redirect(url_for('main.login'))

    week_offset = request.args.get('week_offset', 0, type=int)
    day_offset = request.args.get('day_offset', 0, type=int)
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    day_offset = max(0, min(6, day_offset))
    current_day = start_of_week + timedelta(days=day_offset)

    seances = Seance.query.filter_by(entraineur=f"{nom} {prenom}").all()

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

@main_bp.route('/directeur_technique', methods=['GET', 'POST'])
def directeur_technique():
    if 'user_id' not in session or session.get('role') != 'directeur_technique':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('main.login'))

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

    week_offset = request.args.get('week_offset', 0, type=int)
    day_offset = request.args.get('day_offset', 0, type=int)
    
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    day_offset = max(0, min(6, day_offset))
    current_day = start_of_week + timedelta(days=day_offset)

    groupes = Groupe.query.all()
    entraineurs = Entraineur.query.all()
    
    seances_week = Seance.query.filter(
        Seance.date >= start_of_week.date(),
        Seance.date <= (start_of_week + timedelta(days=6)).date()
    ).all()
    
    seances_day = Seance.query.filter(
        Seance.date == current_day.date()
    ).all()

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
        seances=seances_day,
        seances_week=seances_week,
        creneaux=creneaux,
        terrains=range(1, 8),
        seances_par_groupe=seances_par_groupe
    )

@main_bp.route('/ajouter_seance', methods=['POST'])
def ajouter_seance():
    data = request.get_json()
    
    groupe = Groupe.query.get(data['groupe_id'])
    if not groupe:
        return jsonify({"error": "Groupe introuvable"}), 404

    try:
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        heure_debut = datetime.strptime(data['heure_debut'], '%H:%M').time()
        creneaux_valides = [
            time(8, 0), time(9, 30), time(11, 0), time(12, 30),
            time(14, 0), time(15, 30), time(17, 0), time(18, 30)
        ]
        
        if heure_debut not in creneaux_valides:
            return jsonify({"error": "Créneau horaire non valide"}), 400

        heure_fin = (datetime.combine(date_obj, heure_debut) + timedelta(minutes=90)).time()

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
# ... (previous routes continue here)

@main_bp.route('/api/get_session/<int:session_id>', methods=['GET'])
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

@main_bp.route('/edit_session', methods=['POST'])
def edit_session():
    data = request.get_json()
    seance_id = data['session_id']
    new_date = data['date']
    new_heure_debut = data['heure_debut']
    new_terrain = data['terrain']
    entraineur_id = data['entraineur']

    entraineur = Entraineur.query.filter_by(id_entraineur=entraineur_id).first()
    if not entraineur:
        return jsonify({"error": "Entraîneur introuvable"}), 404
    new_entraineur = f"{entraineur.nom} {entraineur.prenom}"

    session = Seance.query.get(seance_id)
    if not session:
        return jsonify({"error": "Séance non trouvée"}), 404

    try:
        new_date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()
        new_heure_debut_obj = datetime.strptime(new_heure_debut, '%H:%M').time()
        new_heure_fin_obj = (datetime.combine(new_date_obj, new_heure_debut_obj) + timedelta(minutes=90)).time()

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

@main_bp.route('/supprimer_adherent_groupe/<int:adherent_id>', methods=['POST', 'GET'])
def supprimer_adherent_groupe(adherent_id):
    if 'user_id' not in session or session.get('role') != 'entraineur':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('main.login'))

    adherent = Adherent.query.get_or_404(adherent_id)
    adherent.groupe = None
    adherent.entraineur = None
    db.session.commit()
    flash("L'adhérent a été retiré du groupe.", "success")
    return redirect(url_for('main.entraineur'))

@main_bp.route('/ajouter_adherent_groupe/<int:groupe_id>', methods=['POST'])
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

@main_bp.route('/ajouter_groupe', methods=['POST'])
def ajouter_groupe():
    data = request.get_json()
    group_name = data.get('groupName')
    entraineur_id = data.get('entraineurId')

    if not group_name or not entraineur_id:
        return "Le nom du groupe ou l'entraîneur est manquant.", 400

    if Groupe.query.filter_by(nom_groupe=group_name).first():
        return "Un groupe avec ce nom existe déjà.", 400

    try:
        entraineur = Entraineur.query.get(entraineur_id)
        if not entraineur:
            return "Entraîneur introuvable.", 404

        nouveau_groupe = Groupe(
            nom_groupe=group_name,
            entraineur_nom=f"{entraineur.nom} {entraineur.prenom}",
            type_abonnement=entraineur.type_abonnement,
            categorie=group_name.split('-')[0]
        )
        
        db.session.add(nouveau_groupe)
        db.session.commit()
        return "Groupe ajouté avec succès.", 200

    except Exception as e:
        db.session.rollback()
        return f"Erreur lors de l'ajout du groupe : {str(e)}", 500
# ... (previous routes continue here)

@main_bp.route('/supprimer_groupe/<int:id>', methods=['DELETE'])
def supprimer_groupe(id):
    if 'user_id' not in session or session.get('role') != 'directeur_technique':
        return jsonify({"error": "Accès non autorisé"}), 403

    groupe = Groupe.query.get_or_404(id)
    
    try:
        Seance.query.filter_by(groupe=groupe.nom_groupe).delete()
        db.session.delete(groupe)
        db.session.commit()
        return jsonify({"message": "Groupe et séances associées supprimés avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@main_bp.route('/api/groupes_seances', methods=['GET'])
def api_groupes_seances():
    username = session.get('username')
    nom, prenom = username.split('.')
    entraineur = Entraineur.query.filter_by(nom=nom, prenom=prenom).first()
    groupes = Groupe.query.filter_by(entraineur_nom=f"{nom} {prenom}").all()
    groupes_data = []
    if groupes:
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
                        'heure': seance.heure_debut.strftime('%H:%M')
                    }
                    for seance in seances
                ]
            })
        return jsonify(groupes_data), 200
    else:
        return jsonify(groupes_data), 200

@main_bp.route('/api/marquer_presence/<int:seance_id>', methods=['POST'])
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
                heure_debut=seance.heure_debut,
                est_present=presence['est_present']
            )
            db.session.add(new_presence)
        db.session.commit()
        return "Présence enregistrée avec succès", 200
    except Exception as e:
        db.session.rollback()
        return f"Erreur lors de l'enregistrement des présences : {str(e)}", 500

@main_bp.route('/api/get_adherents_groupe/<int:groupe_id>', methods=['GET'])
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

@main_bp.route('/api/get_adherents/<int:seance_id>', methods=['GET'])
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

@main_bp.route('/api/search_adherent/<string:matricule>', methods=['GET'])
def api_search_adherent(matricule):
    adherents = Adherent.query.filter(Adherent.matricule.like(f"%{matricule}%")).all()
    adherents_list = [
        {"matricule": adherent.matricule, "nom": adherent.nom, "prenom": adherent.prenom}
        for adherent in adherents
    ]
    return jsonify({"adherents": adherents_list}), 200

@main_bp.route('/changer_mot_de_passe', methods=['POST'])
def changer_mot_de_passe():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Vous devez être connecté pour changer votre mot de passe."}), 401

    data = request.get_json()
    nouveau_mot_de_passe = data.get('nouveau_mot_de_passe')
    confirmation_mot_de_passe = data.get('confirmation_mot_de_passe')

    if not nouveau_mot_de_passe or not confirmation_mot_de_passe:
        return jsonify({"error": "Veuillez remplir tous les champs."}), 400

    if nouveau_mot_de_passe != confirmation_mot_de_passe:
        return jsonify({"error": "Les mots de passe ne correspondent pas."}), 400

    user = User.query.filter_by(utilisateur=username).first()
    if not user:
        return jsonify({"error": "Utilisateur introuvable."}), 404

    hashed_password = hashlib.sha256(nouveau_mot_de_passe.encode()).hexdigest()
    user.password = hashed_password
    db.session.commit()

    return jsonify({"message": "Mot de passe mis à jour avec succès."}), 200