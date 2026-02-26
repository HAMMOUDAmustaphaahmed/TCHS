🎾 TCHS – Tennis Club Hammam Sousse
La solution tout-en-un pour gérer votre club de tennis
Adhérents, entraîneurs, paiements, planning, présences, finances… centralisez tout en un clic !

https://img.shields.io/badge/Python-3.8%252B-blue?logo=python&logoColor=white
https://img.shields.io/badge/Flask-2.0%252B-lightgrey?logo=flask
https://img.shields.io/badge/MySQL-8.0%252B-orange?logo=mysql
https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap
https://img.shields.io/badge/PDF-ReportLab-red
https://img.shields.io/badge/license-MIT-green

✨ Aperçu
TCHS est une application web complète développée avec Flask pour répondre aux besoins spécifiques d’un club de tennis.
Elle offre une interface intuitive et des fonctionnalités avancées pour :

📋 Gérer les adhérents (inscriptions, renouvellements, historique)

👨‍🏫 Administrer les entraîneurs et leurs comptes

💳 Suivre les paiements et générer automatiquement des reçus PDF

📅 Planifier les séances d’entraînement et de préparation physique

✅ Pointer les présences (adhérents & entraîneurs)

🏟️ Gérer les locations de terrains

📊 Visualiser des statistiques financières en temps réel

💬 Communiquer via une messagerie interne

🚀 Fonctionnalités clés
Domaine	Fonctionnalités
Saisons	Gestion par saison (S2025, E2025…) – tout est filtré automatiquement
Adhérents	Ajout, modification, suppression, import depuis une saison antérieure, fiche PDF
Entraîneurs	Création automatique de compte, réinitialisation de mot de passe
Paiements	Encaissement, historique, annulation, reçu PDF instantané (format 210×70 mm)
Présences	Pointage par séance, suivi individuel/groupe, statistiques
Planning	Création de séances récurrentes, gestion des conflits de terrains
Locations	Réservation par des tiers, suivi des revenus
Dépenses	Enregistrement et catégorisation
Finances	Tableaux de bord interactifs, graphiques d’évolution, export Excel
Groupes	Affectation des adhérents, cotisations associées
Tournois	Création et gestion de tournois internes
Messagerie	Communication entre administrateur, directeur technique et entraîneurs
Rôles	Admin, Directeur technique, Entraîneur – chacun a ses permissions
🛠️ Stack technique
Backend : Python 3.8+, Flask, SQLAlchemy (ORM)

Base de données : MySQL / MariaDB avec PyMySQL

Frontend : HTML5, CSS3, Bootstrap 5, JavaScript (fetch API)

Génération PDF : ReportLab

Exports Excel : Pandas, XlsxWriter

Templating : Jinja2

Authentification : Sessions Flask, hash SHA-256

Fichiers : Upload sécurisé (autres paiements, documents)

📦 Installation en 5 minutes
1. Prérequis
Python 3.8+

MySQL 10.4+

pip

2. Cloner le projet
bash
git clone https://github.com/votre-utilisateur/tchs.git
cd tchs
3. Environnement virtuel (recommandé)
bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
4. Installer les dépendances
bash
pip install -r requirements.txt
Si le fichier requirements.txt est absent, installez manuellement :
pip install flask flask-sqlalchemy pymysql reportlab pandas xlsxwriter pytz

5. Base de données
Créez la base :

sql
CREATE DATABASE tchs CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
Importez le dump fourni :

bash
mysql -u root -p tchs < tchs.sql
6. Configuration
Dans app.py, ajustez l’URI de connexion si besoin :

python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://utilisateur:motdepasse@localhost/tchs'
7. Lancer l’application
bash
python app.py
Rendez-vous sur http://localhost:5001

🔐 Comptes par défaut
Rôle	Identifiant	Mot de passe
Administrateur	admin	1234
Directeur technique	manager	1234
Entraîneur	Zallila.Adam	entraineur
Entraîneur	jaber.ons	entraineur
…	…	…
⚠️ Changez ces mots de passe dès la première connexion !

📁 Structure du projet
text
tchs/
├── app.py                  # Cœur de l'application
├── filter_functions.py     # Filtres par saison
├── tchs.sql                # Structure + données de démo
├── requirements.txt        # Dépendances Python
├── static/                 # CSS, JS, images, librairies
│   ├── css/
│   ├── js/
│   ├── images/
│   └── lib/
├── templates/              # Tous les templates Jinja2
│   ├── admin.html
│   ├── paiement.html
│   ├── planning.html
│   ├── presence.html
│   ├── situation-adherent.html
│   └── ...
├── bon_de_recette/         # Dossier pour les PDF générés
├── autres-paiements/       # Uploads de documents
└── README.md
🌐 API internes (quelques exemples)
POST /api/save_presences – Enregistre les présences d’une séance

GET /api/recu_paiement/<int:paiement_id> – Télécharge le reçu PDF

POST /api/search-paiements – Recherche de paiements par matricule

GET /api/adherents-data – Liste des adhérents (autocomplétion)

GET /api/financial-data – Données pour le tableau de bord financier

POST /api/presences/search – Recherche avancée de présences

🧪 Tests
Aucune suite automatisée pour l’instant. Vous pouvez tester manuellement toutes les fonctionnalités via l’interface.

🤝 Contribution
Les contributions sont les bienvenues !

Forkez le projet

Créez une branche (git checkout -b feature/ma-feature)

Committez (git commit -am 'Ajout de ma feature')

Poussez (git push origin feature/ma-feature)

Ouvrez une Pull Request

📄 Licence
Ce projet est sous licence MIT. Vous êtes libre de l’utiliser, le modifier et le distribuer.

📧 Contact
Pour toute question ou suggestion, ouvrez une issue sur GitHub ou contactez l’administrateur du dépôt.

TCHS – Tennis Club Hammam Sousse
Gérez votre club simplement et efficacement. ⭐
