from flask import send_file
from flask import send_from_directory
from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import hashlib
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

    # Récupérer les groupes et adhérents
    groupes = Groupe.query.filter_by(entraineur_nom=f"{nom} {prenom}").all()
    adherents_disponibles = [
    {
        'adherent_id': adherent.adherent_id,
        'nom': adherent.nom,
        'prenom': adherent.prenom,
        'matricule': adherent.matricule,
        'type_abonnement': adherent.type_abonnement
    }
    for adherent in Adherent.query.filter(
        or_(Adherent.groupe == None, Adherent.groupe == ""),
        Adherent.type_abonnement == entraineur.type_abonnement
    ).all()
]


    groupes_data = []
    for groupe in groupes:
        adherents = Adherent.query.filter_by(groupe=groupe.nom_groupe).all()
        groupes_data.append({
            'groupe': groupe,
            'adherents': adherents
        })

    return render_template(
        'entraineur.html',
        entraineur=entraineur,
        groupes_data=groupes_data,
        adherents_disponibles=adherents_disponibles
    )




@app.route('/supprimer_adherent_groupe/<int:adherent_id>', methods=['POST', 'GET'])
def supprimer_adherent_groupe(adherent_id):
    if 'user_id' not in session or session.get('role') != 'entraineur':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))

    adherent = Adherent.query.get_or_404(adherent_id)
    adherent.groupe = None
    db.session.commit()
    flash("L'adhérent a été retiré du groupe.", "success")
    return redirect(url_for('entraineur'))  # Retour à la page de l'entraîneur

@app.route('/ajouter_adherent_groupe/<int:groupe_id>', methods=['POST'])
def ajouter_adherent_groupe(groupe_id):
    matricule = request.form.get('matricule')

    groupe = Groupe.query.get(groupe_id)
    if not groupe:
        return "Groupe non trouvé", 404

    adherent = Adherent.query.filter_by(matricule=matricule).first()
    if not adherent:
        return "Adhérent non trouvé", 404

    if adherent.groupe:
        return "Cet adhérent est déjà associé à un groupe.", 400

    adherent.groupe = groupe.nom_groupe
    adherent.entraineur = groupe.entraineur_nom
    db.session.commit()

    return "Adhérent ajouté avec succès", 200




@app.route('/ajouter_seance/<int:groupe_id>', methods=['POST'])
def ajouter_seance(groupe_id):
    data = request.get_json()

    # Vérification des données
    date = data.get('date')
    heure = data.get('time')
    entraineur = data.get('entraineur')

    if not date or not heure or not entraineur:
        return "Date, heure ou entraîneur manquant.", 400

    groupe = Groupe.query.get(groupe_id)
    if not groupe:
        return "Groupe introuvable.", 404

    # Ajouter la séance
    try:
        nouvelle_seance = Seance(
            date=date,
            heure=heure,
            groupe=groupe.nom_groupe,
            entraineur=entraineur
        )
        db.session.add(nouvelle_seance)
        db.session.commit()
        return "Séance ajoutée avec succès.", 200
    except Exception as e:
        db.session.rollback()
        return f"Erreur lors de l'ajout de la séance : {str(e)}", 500

@app.route('/ajouter_groupe', methods=['POST'])
def ajouter_groupe():
    data = request.get_json()

    # Récupérer les données du formulaire
    group_name = data.get('groupName')
    entraineur = data.get('entraineur')

    if not group_name or not entraineur:
        return "Le nom du groupe ou l'entraîneur est manquant.", 400

    # Vérifier si le groupe existe déjà
    if Groupe.query.filter_by(nom_groupe=group_name).first():
        return "Un groupe avec ce nom existe déjà.", 400

    # Ajouter le nouveau groupe
    try:
        type_abonnement = Entraineur.query.filter_by(nom=entraineur.split()[0], prenom=entraineur.split()[1]).first().type_abonnement
        nouveau_groupe = Groupe(
            nom_groupe=group_name,
            entraineur_nom=entraineur,
            type_abonnement=type_abonnement
        )
        db.session.add(nouveau_groupe)
        db.session.commit()
        return "Groupe ajouté avec succès.", 200
    except Exception as e:
        db.session.rollback()
        return f"Erreur lors de l'ajout du groupe : {str(e)}", 500

@app.route('/api/groupes_seances', methods=['GET'])
def api_groupes_seances():
    groupes = Groupe.query.all()
    groupes_data = []

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
            return redirect(url_for('admin'))  # Changez la redirection selon votre logique
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
        nom_groupe = request.form['groupe']
        entraineur_nom = request.form['entraineur']
        type_abonnement = request.form['type_abonnement']

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
                enfant=request.form.get('enfant'),
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
            user = str(nouveau_entraineur.nom) + '.' + str(nouveau_entraineur.prenom)
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


@app.route('/paiement')
def paiement():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('login'))
    return "Paiement"

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
    type_abonnement = db.Column(db.String(50), nullable=False)
    ancien_abonne = db.Column(db.String(50), nullable=False)
    matricule = db.Column(db.Integer, unique=True, nullable=False)
    groupe = db.Column(db.String(100), nullable=True)
    entraineur = db.Column(db.String(50), nullable=False)
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
    enfant = db.Column(db.Enum('Oui', 'Non'), nullable=False)
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

    def __repr__(self):
        return f'<Groupe {self.nom_groupe} géré par {self.entraineur_nom}>'

class Seance(db.Model):
    __tablename__ = 'seances'  # Nom de la table dans la base de données
    
    seance_id = db.Column(db.Integer, primary_key=True)  # Identifiant unique pour chaque séance
    date = db.Column(db.Date, nullable=False)  # Date de la séance
    heure = db.Column(db.Time, nullable=False)  # Heure de la séance
    groupe = db.Column(db.String(100), nullable=False)  # Nom du groupe
    entraineur = db.Column(db.String(100), nullable=False)  # Nom de l'entraîneur
    
    def __init__(self, date, heure, groupe, entraineur):
        self.date = date
        self.heure = heure
        self.groupe = groupe
        self.entraineur = entraineur
    
    def __repr__(self):
        return f"<Seance {self.seance_id} - {self.groupe} - {self.entraineur} - {self.date} {self.heure}>"


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


# Running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
