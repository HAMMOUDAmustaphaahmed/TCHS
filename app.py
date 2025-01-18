from flask import send_file
from flask import send_from_directory
from flask import Flask, render_template, request, redirect, url_for, flash, session
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


@app.route('/entraineur', methods=['GET', 'POST'])
def entraineur():
    # Récupérer l'ID de l'entraîneur depuis la session
    user_id = session.get('user_id')
    if not user_id:
        flash('Vous devez être connecté pour accéder à cette page.', 'danger')
        return redirect(url_for('login'))

    # Récupérer l'entraîneur connecté
    entraineur = Entraineur.query.get(user_id)
    if not entraineur:
        flash('Entraîneur introuvable.', 'danger')
        return redirect(url_for('login'))

    # Récupérer tous les groupes gérés par cet entraîneur
    groupes = Groupe.query.filter_by(entraineur_nom=entraineur.nom).all()

    stats = []
    for groupe in groupes:
        participants = Adherent.query.filter_by(groupe=groupe.nom_groupe).count()
        stats.append({
            'groupe': groupe.nom_groupe,
            'participants': participants
        })
    adherents_disponibles = Adherent.query.filter_by(groupe=None, type_abonnement=entraineur.type_abonnement).all()
    if request.method == 'POST':
        action = request.form.get('action')

        # Création d'un nouveau groupe
        if action == 'create_group':
            nom_groupe = request.form['nom_groupe']
            groupe_exist = Groupe.query.filter_by(nom_groupe=nom_groupe).first()

            if groupe_exist:
                flash("Le nom de groupe existe déjà.", "danger")
            else:
                nouveau_groupe = Groupe(
                    nom_groupe=nom_groupe,
                    entraineur_nom=entraineur.nom,
                    type_abonnement=entraineur.type_abonnement,
                    adherent_matricule=''
                )
                try:
                    db.session.add(nouveau_groupe)
                    db.session.commit()
                    flash("Groupe créé avec succès.", "success")
                except Exception as e:
                    db.session.rollback()
                    flash(f"Erreur lors de la création du groupe : {str(e)}", "danger")

        # Ajout d'un adhérent à un groupe
        elif action == 'add_adherent':
            adherent_id = request.form['adherent_id']
            groupe_nom = request.form['groupe_nom']
            adherent = Adherent.query.get(adherent_id)

            if not adherent:
                flash("Adhérent introuvable.", "danger")
            elif adherent.groupe:
                flash("Cet adhérent est déjà associé à un groupe.", "danger")
            elif adherent.type_abonnement != entraineur.type_abonnement:
                flash("Le type d'abonnement de l'adhérent ne correspond pas.", "danger")
            else:
                try:
                    adherent.groupe = groupe_nom
                    db.session.commit()
                    flash("Adhérent ajouté au groupe avec succès.", "success")
                except Exception as e:
                    db.session.rollback()
                    flash(f"Erreur lors de l'ajout de l'adhérent : {str(e)}", "danger")

        # Suppression d'un adhérent du groupe
        elif action == 'remove_adherent':
            adherent_id = request.form['adherent_id']
            adherent = Adherent.query.get(adherent_id)

            if not adherent:
                flash("Adhérent introuvable.", "danger")
            elif adherent.groupe != request.form['groupe_nom']:
                flash("Cet adhérent n'appartient pas à ce groupe.", "danger")
            else:
                try:
                    adherent.groupe = None
                    db.session.commit()
                    flash("Adhérent supprimé du groupe avec succès.", "success")
                except Exception as e:
                    db.session.rollback()
                    flash(f"Erreur lors de la suppression de l'adhérent : {str(e)}", "danger")
         # Récupérer les adhérents sans groupe et avec le même type d'abonnement que l'entraîneur
    return render_template('entraineur.html', entraineur=entraineur, stats=stats,adherents_disponibles=adherents_disponibles)

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

        # Vérifier si le groupe existe déjà
        groupe_exist = Groupe.query.filter_by(nom_groupe=nom_groupe).first()

        # Si le groupe n'existe pas, le créer
        if not groupe_exist:
            nouvel_groupe = Groupe(
                nom_groupe=nom_groupe,
                entraineur_nom=entraineur_nom,
                adherent_matricule='',  # Initialement vide
                type_abonnement=type_abonnement
            )
            db.session.add(nouvel_groupe)
            db.session.commit()

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
            db.session.add(nouveau_entraineur)
            db.session.commit()  # Commit avant d'avoir accès à l'ID généré

            password='entraineur'
            user=nouveau_entraineur.nom+'.'+nouveau_entraineur.prenom
            role='entraineur'
            # Hachage du mot de passe basé sur l'ID de l'entraîneur
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Création de l'utilisateur associé à l'entraîneur
            new_utuiisateur = User(utilisateur=user, password=hashed_password, role=role)
            db.session.add(new_utuiisateur)
            db.session.commit()
            flash("Utilisateur ajouté avec succès.", "success")

            

            flash('L\'entraîneur a été ajouté avec succès !', 'success')
            return redirect(url_for('admin'))  # Redirection vers la page d'administration

        except Exception as e:
            db.session.rollback()  # Annule les modifications en cas d'erreur
            flash(f"Erreur lors de l'ajout de l'entraîneur : {str(e)}", 'danger')

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
    entraineur = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    paye = db.Column(db.Enum('O', 'N'), nullable=False)
    status = db.Column(db.Enum('Actif', 'Non-Actif'), nullable=False)


    def __repr__(self):
        return f'<Adherent {self.nom} {self.prenom}>'

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
    heure_fin = db.Column(db.Time, nullable=False)
    est_present = db.Column(db.Enum('O', 'N'), nullable=False, default='N')

    def __repr__(self):
        return f'<Presence {self.groupe_nom} - {self.adherent_matricule} - {self.date_seance}>'

class Groupe(db.Model):
    __tablename__ = 'groupe'
    
    id_groupe = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_groupe = db.Column(db.String(100), nullable=False)
    entraineur_nom = db.Column(db.String(50), nullable=False)
    adherent_matricule = db.Column(db.String(50), nullable=True)
    type_abonnement = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Groupe {self.nom_groupe} géré par {self.entraineur_nom}>'


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
