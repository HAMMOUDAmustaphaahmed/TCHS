TCHS - Tennis Club Hammam Sousse
Application web de gestion complète pour un club de tennis.
Elle permet de gérer les adhérents, les entraîneurs, les paiements, les présences, les plannings, les locations de terrains, les dépenses, et bien plus encore.

🚀 Technologies utilisées
Backend : Python 3.8+, Flask, SQLAlchemy

Base de données : MySQL (MariaDB) avec PyMySQL

Frontend : HTML5, CSS3, Bootstrap 5, JavaScript (fetch API)

Génération de PDF : ReportLab

Export Excel : Pandas, XlsxWriter

Templates : Jinja2

Authentification : Sessions Flask, hash SHA-256

Gestion des fichiers : Upload de documents (autres paiements)

✅ Fonctionnalités principales
Saisons sportives : Gestion par saison (S2025, E2025...)

Adhérents : Ajout, modification, suppression, import depuis une saison antérieure, génération de fiche PDF

Entraîneurs : Gestion avec création automatique de compte utilisateur

Paiements : Encaissement des cotisations, historique, annulation, reçu PDF automatique

Présences : Pointage par séance (entraînement ou préparation physique), suivi individuel et par groupe

Planning : Création de séances récurrentes, gestion des terrains

Locations de terrains : Réservation par des tiers, suivi financier

Dépenses : Enregistrement et catégorisation

Statistiques financières : Tableaux de bord, graphiques

Messagerie interne : Communication entre utilisateurs

Gestion des groupes : Affectation des adhérents, cotisations associées

Tournois : Création et gestion de tournois internes

Rôles : Admin, Directeur technique, Entraîneur

📋 Prérequis
Python 3.8 ou supérieur

MySQL / MariaDB (version 10.4+ recommandée)

pip (gestionnaire de paquets Python)

Git (optionnel)

⚙️ Installation
1. Cloner le dépôt
bash
git clone https://github.com/votre-utilisateur/tchs.git
cd tchs
2. Créer un environnement virtuel (recommandé)
bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
3. Installer les dépendances
bash
pip install -r requirements.txt
Si le fichier requirements.txt n'existe pas, installez manuellement les paquets principaux :

bash
pip install flask flask-sqlalchemy pymysql reportlab pandas xlsxwriter pytz
4. Configurer la base de données
Créez une base de données MySQL nommée tchs (par exemple) :

sql
CREATE DATABASE tchs CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
Importez la structure et les données de démonstration :

bash
mysql -u root -p tchs < tchs.sql
Remarque : le fichier tchs.sql fourni contient déjà des données de test (adhérents, entraîneurs, paiements…).

5. Adapter la configuration
Dans app.py, modifiez l'URI de connexion si nécessaire :

python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/tchs'
Utilisateur/mot de passe : adaptez root et éventuellement le mot de passe.

🚀 Lancement de l'application
bash
python app.py
L'application démarre sur http://0.0.0.0:5001 (par défaut).
Ouvrez votre navigateur à l'adresse http://localhost:5001.

🔐 Comptes par défaut
Le fichier tchs.sql crée plusieurs utilisateurs avec le mot de passe 1234 (sauf pour les entraîneurs qui ont entraineur par défaut) :

Rôle	Identifiant	Mot de passe
Administrateur	admin	1234
Directeur technique	manager	1234
Entraîneur	Zallila.Adam	entraineur
Entraîneur	jaber.ons	entraineur
...	...	...
Important : changez ces mots de passe après la première connexion.

📁 Structure du projet
text
tchs/
│
├── app.py                  # Application principale Flask
├── filter_functions.py     # Fonctions de filtrage par saison
├── tchs.sql                # Dump de la base de données (structure + données)
├── requirements.txt        # Dépendances Python
│
├── static/                 # Fichiers statiques (CSS, JS, images)
│   ├── css/
│   ├── js/
│   ├── images/
│   └── lib/                # Librairies tierces (Bootstrap, Owl Carousel...)
│
├── templates/              # Templates Jinja2
│   ├── admin.html
│   ├── ajouter_adherent.html
│   ├── ajouter_entraineur.html
│   ├── paiement.html
│   ├── planning.html
│   ├── presence.html
│   ├── situation-adherent.html
│   ├── ... (tous les autres templates)
│
├── bon_de_recette/         # Dossier pour stocker les PDF générés (optionnel)
├── autres-paiements/       # Uploads pour les autres paiements
└── README.md               # Ce fichier
📡 API internes
Quelques routes JSON utilisées par l'interface :

POST /api/save_presences – Enregistre les présences d'une séance

GET /api/recu_paiement/<int:paiement_id> – Génère le reçu PDF d'un paiement

POST /api/search-paiements – Recherche des paiements par matricule

GET /api/adherents-data – Liste des adhérents (pour autocomplétion)

GET /api/financial-data – Données pour le tableau de bord financier

POST /api/presences/search – Recherche avancée de présences

🧪 Tests
Aucune suite de tests automatisés n'est encore intégrée.
Vous pouvez tester manuellement les fonctionnalités via l'interface.

🤝 Contribution
Les contributions sont les bienvenues !
Pour proposer une amélioration :

Forkez le projet

Créez une branche (git checkout -b feature/ma-feature)

Committez vos changements (git commit -am 'Ajout de ma feature')

Poussez la branche (git push origin feature/ma-feature)

Ouvrez une Pull Request

📄 Licence
Ce projet est sous licence MIT.
Vous êtes libre de l'utiliser, le modifier et le distribuer.

📧 Contact
Pour toute question ou suggestion, veuillez contacter l'administrateur du dépôt.

TCHS – Tennis Club Hammam Sousse
Gérez votre club simplement et efficacement.
