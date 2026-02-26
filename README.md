<div align="center">

```
████████╗ ██████╗██╗  ██╗███████╗
╚══██╔══╝██╔════╝██║  ██║██╔════╝
   ██║   ██║     ███████║███████╗
   ██║   ██║     ██╔══██║╚════██║
   ██║   ╚██████╗██║  ██║███████║
   ╚═╝    ╚═════╝╚═╝  ╚═╝╚══════╝
```

# 🎾 Tennis Club Hammam Sousse

**La plateforme de gestion tout-en-un pensée pour votre club.**  
*Adhérents · Entraîneurs · Paiements · Planning · Présences · Finances*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

</div>

---

## 🌟 Pourquoi TCHS ?

> *Parce que gérer un club de tennis ne devrait pas vous empêcher de vous concentrer sur le tennis.*

TCHS est né d'un constat simple : les clubs manquent d'outils adaptés à leur réalité. Pas de tableurs éparpillés, pas de cahiers de présences perdus, pas de flou sur les finances — une seule application, claire, rapide, pensée de terrain.

---

## ✨ Ce que vous pouvez faire

<table>
<tr>
<td width="50%">

### 👥 Côté Membres
- **Adhérents** — inscription, renouvellement, fiche PDF, import inter-saisons
- **Groupes** — affectation automatique avec cotisations associées
- **Présences** — pointage par séance, suivi individuel ou collectif
- **Tournois** — organisation de compétitions internes

</td>
<td width="50%">

### ⚙️ Côté Administration
- **Entraîneurs** — comptes auto-générés, réinitialisation de mot de passe
- **Planning** — séances récurrentes, détection de conflits terrains
- **Locations** — réservations par des tiers, suivi des revenus
- **Messagerie** — communication interne multiparties

</td>
</tr>
<tr>
<td>

### 💳 Côté Finances
- Encaissement avec **reçu PDF instantané** (format 210×70 mm)
- Annulation de paiements, historique complet
- Enregistrement et catégorisation des dépenses
- **Export Excel** de tous les rapports

</td>
<td>

### 📊 Côté Données
- Tableaux de bord financiers **interactifs**
- Graphiques d'évolution en temps réel
- Gestion par **saison** (ex : S2025, E2025) — tout se filtre automatiquement
- API interne pour l'autocomplétion et les recherches avancées

</td>
</tr>
</table>

---

## 🛠️ Stack Technique

```
┌─────────────────────────────────────────────────────────┐
│                        FRONTEND                          │
│          HTML5 · CSS3 · Bootstrap 5 · JavaScript        │
│                     (Fetch API + Jinja2)                 │
├─────────────────────────────────────────────────────────┤
│                        BACKEND                           │
│              Python 3.8+ · Flask · SQLAlchemy            │
│            Sessions Flask · Hachage SHA-256              │
├─────────────────────────────────────────────────────────┤
│                       BASE DE DONNÉES                    │
│                  MySQL / MariaDB · PyMySQL               │
├─────────────────────────────────────────────────────────┤
│                        EXPORTS                           │
│           ReportLab (PDF) · Pandas · XlsxWriter          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prérequis

- Python **3.8+**
- MySQL **10.4+**
- pip

### 1 — Cloner

```bash
git clone https://github.com/votre-utilisateur/tchs.git
cd tchs
```

### 2 — Environnement virtuel

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

### 3 — Dépendances

```bash
pip install -r requirements.txt
```

> Si `requirements.txt` est absent :
> ```bash
> pip install flask flask-sqlalchemy pymysql reportlab pandas xlsxwriter pytz
> ```

### 4 — Base de données

```sql
CREATE DATABASE tchs CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

```bash
mysql -u root -p tchs < tchs.sql
```

### 5 — Configuration

Dans `app.py`, ajustez l'URI de connexion :

```python
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://utilisateur:motdepasse@localhost/tchs'
)
```

### 6 — Lancer 🎉

```bash
python app.py
```

Rendez-vous sur **[http://localhost:5001](http://localhost:5001)**

---

## 🔐 Comptes par défaut

> ⚠️ **Changez ces mots de passe dès la première connexion !**

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| 🔴 Administrateur | `Administrateur` | `****` |
| 🟠 Directeur technique | `Directeur` | `****` |
| 🟢 Entraîneur | `Nom.Prenom` | `****` |


---

## 📁 Structure du projet

```
tchs/
│
├── 📄 app.py                   ← Cœur de l'application
├── 🔧 filter_functions.py      ← Filtres par saison
├── 🗄️  tchs.sql                ← Structure + données de démo
├── 📦 requirements.txt         ← Dépendances Python
│
├── 🎨 static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── lib/
│
├── 🖼️  templates/
│   ├── admin.html
│   ├── paiement.html
│   ├── planning.html
│   ├── presence.html
│   ├── situation-adherent.html
│   └── ...
│
├── 📑 bon_de_recette/          ← PDFs générés
└── 📎 autres-paiements/        ← Documents uploadés
```

---

## 🌐 API Interne — Exemples

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/save_presences` | Enregistre les présences d'une séance |
| `GET` | `/api/recu_paiement/<id>` | Télécharge le reçu PDF |
| `POST` | `/api/search-paiements` | Recherche par matricule |
| `GET` | `/api/adherents-data` | Liste pour autocomplétion |
| `GET` | `/api/financial-data` | Données tableau de bord |
| `POST` | `/api/presences/search` | Recherche avancée de présences |

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Voici comment participer :

```bash
# 1. Forkez le projet sur GitHub
# 2. Créez votre branche
git checkout -b feature/ma-super-feature

# 3. Committez vos changements
git commit -am "feat: description claire de la feature"

# 4. Poussez
git push origin feature/ma-super-feature

# 5. Ouvrez une Pull Request 🎉
```

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**.  
Vous êtes libre de l'utiliser, le modifier et le redistribuer.

---

<div align="center">

**TCHS — Tennis Club Hammam Sousse**

*Gérez votre club simplement. Jouez plus, gérez moins.*

⭐ Si ce projet vous aide, n'oubliez pas de le **star** sur GitHub !

</div>
