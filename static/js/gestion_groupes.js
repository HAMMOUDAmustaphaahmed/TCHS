// ==========================
// 📌 Gestion des Séances
// ==========================

// Datepicker (format français)
const frenchDatepicker = flatpickr("#sessionDate", {
    locale: "fr",
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "d/m/Y",
    minDate: "today",
    disableMobile: true
});

// ⚡️ Créneaux
const creneauxNormaux = [
    '08:00', '09:30', '11:00','12:30', '14:00', '15:30','17:00','18:30','20:00','21:30'
];

const creneauxPrepPhysique = [
    '08:00', '09:00', '10:00', '11:00', '12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00'
];

let currentGroupId = null;
let isPrepPhysique = false; // pour gérer le type de séance

function populateCreneaux() {
    const select = document.getElementById('sessionTime');
    select.innerHTML = ''; // clear previous options

    const creneaux = isPrepPhysique ? creneauxPrepPhysique : creneauxNormaux;

    creneaux.forEach(time => {
        const option = document.createElement('option');
        option.value = time;
        option.text = time;
        select.appendChild(option);
    });
}

// --------------------------
// 🔹 Modal Séance
// --------------------------
function openSessionModal(groupId) {
    currentGroupId = groupId;
    isPrepPhysique = false;
    populateCreneaux();
    document.getElementById('sessionModal').style.display = 'block';
}

function openPrepPhysiqueModal(groupId) {
    currentGroupId = groupId;
    isPrepPhysique = true;
    populateCreneaux();
    document.getElementById('sessionModal').style.display = 'block';
}

function closeSessionModal() {
    document.getElementById('sessionModal').style.display = 'none';
    isPrepPhysique = false;
}

// --------------------------
// 🔹 Ajouter séance
// --------------------------
function addSession() {
    const date = document.getElementById('sessionDate').value;
    const time = document.getElementById('sessionTime').value;
    const terrain = document.getElementById('sessionTerrain').value;
    const repeatWeekly = document.getElementById('repeatWeekly').checked;

    if (!date || !time || !terrain) {
        alert('Veuillez remplir tous les champs');
        return;
    }

    const typeSeance = isPrepPhysique ? "prep_physique" : "normale";

    fetch('/ajouter_seance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            groupe_id: currentGroupId,
            date: date,
            heure_debut: time,
            terrain: terrain,
            repeat_weekly: repeatWeekly,
            type_seance: typeSeance
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            location.reload();
        } else {
            alert(data.error);
        }
        closeSessionModal();
    })
    .catch(err => {
        console.error('Erreur:', err);
        alert('Une erreur est survenue');
        closeSessionModal();
    });
}

// ==========================
// 📌 Gestion des Groupes
// ==========================
function showGroupForm() {
    document.getElementById("groupForm").style.display = "block";
}

function confirmGroupAdd() {
    const category = document.getElementById("groupCategory").value;
    const number = document.getElementById("groupNumber").value;
    const letter = document.getElementById("groupLetter").value.toUpperCase();
    const entraineurId = document.getElementById("groupEntraineur").value;
    const prepPhysiqueId = document.getElementById("groupPrepPhysique").value;

    if (!category || !number || !letter || !entraineurId) {
        alert("Veuillez remplir tous les champs obligatoires");
        return;
    }

    const groupName = `${category}-${number}-${letter}`;

    fetch('/ajouter_groupe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            groupName, 
            entraineurId,
            prepPhysiqueId  // Nouveau champ
        })
    })
    .then(response => {
        if (response.ok) {
            alert("Groupe créé avec succès!");
            location.reload();
        } else {
            response.text().then(text => alert("Erreur: " + text));
        }
    })
    .catch(err => {
        console.error('Erreur:', err);
        alert("Une erreur est survenue lors de la création du groupe");
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Event listener existant pour les entraîneurs
    document.querySelectorAll('.entraineur-select').forEach(select => {
        select.addEventListener('change', function() {
            const groupeId = this.dataset.groupeId;
            const entraineurId = this.value;
            
            const formData = new FormData();
            formData.append('action', 'changer_entraineur');
            formData.append('groupe_id', groupeId);
            formData.append('entraineur_id', entraineurId);

            fetch('/directeur_technique', {
                method: 'POST',
                body: formData
            })
            .then(() => location.reload())
            .catch(err => {
                console.error('Erreur:', err);
                alert('Une erreur est survenue lors du changement d\'entraîneur');
            });
        });
    });

    // Nouvel event listener pour les préparateurs physiques
    document.querySelectorAll('.prep-physique-select').forEach(select => {
        select.addEventListener('change', function() {
            const groupeId = this.dataset.groupeId;
            const prepPhysiqueId = this.value;
            
            const formData = new FormData();
            formData.append('action', 'changer_prep_physique');
            formData.append('groupe_id', groupeId);
            formData.append('prep_physique_id', prepPhysiqueId);

            fetch('/directeur_technique', {
                method: 'POST',
                body: formData
            })
            .then(() => {
                alert('Préparateur physique modifié avec succès');
                location.reload();
            })
            .catch(err => {
                console.error('Erreur:', err);
                alert('Une erreur est survenue lors du changement de préparateur physique');
            });
        });
    });
});


function deleteGroup(groupId) {
    if (confirm("Supprimer ce groupe et toutes ses séances ?")) {
        fetch(`/supprimer_groupe/${groupId}`, { method: 'DELETE' })
        .then(r => r.ok ? location.reload() : r.json().then(data => alert(data.error)))
        .catch(err => console.error('Erreur:', err));
    }
}

function deleteSession(seanceId) {
    if (confirm("Supprimer cette séance ?")) {
        fetch('/directeur_technique', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `action=supprimer_seance&seance_id=${seanceId}`
        }).then(() => location.reload());
    }
}

// Changement entraîneur
document.querySelectorAll('.entraineur-select').forEach(select => {
    select.addEventListener('change', function() {
        const groupeId = this.dataset.groupeId;
        const entraineurId = this.value;
        fetch('/directeur_technique', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `action=changer_entraineur&groupe_id=${groupeId}&entraineur_id=${entraineurId}`
        }).then(() => location.reload());
    });
});

// ==========================
// 📌 Gestion des Adhérents
// ==========================
let selectedAdherents = [];

function openAddAdherentModal(groupId) {
    currentGroupId = groupId;
    selectedAdherents = [];

    fetch(`/api/get_adherents_groupe/${groupId}`)
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('currentMembers');
            container.innerHTML = '';

            if (!data.adherents || data.adherents.length === 0) {
                container.innerHTML = '<div class="text-muted p-2">Aucun membre dans ce groupe</div>';
                return;
            }

            data.adherents.forEach(adherent => {
                const div = document.createElement('div');
                div.className = 'd-flex justify-content-between align-items-center p-2 border-bottom';
                div.innerHTML = `
                    <div>${adherent.matricule} - ${adherent.nom} ${adherent.prenom}</div>
                    <button class="btn btn-sm btn-danger" onclick="removeFromGroup('${adherent.matricule}')">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                container.appendChild(div);
            });
        });

    updateSelectedDisplay();
    document.getElementById('adherentSearchInput').value = '';
    document.getElementById('adherentSearchResults').innerHTML = '';
    document.getElementById('addAdherentModal').style.display = 'block';
}

function closeAddAdherentModal() {
    document.getElementById('addAdherentModal').style.display = 'none';
    document.getElementById('adherentSearchInput').value = '';
    document.getElementById('adherentSearchResults').innerHTML = '';
}

function removeFromGroup(matricule) {
    if (!confirm("Retirer cet adhérent du groupe ?")) return;

    fetch(`/retirer_adherent_groupe/${currentGroupId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ matricule })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) alert(data.error);
        else openAddAdherentModal(currentGroupId);
    });
}

// Recherche adhérents
document.getElementById('searchButton').addEventListener('click', function() {
    const searchTerm = document.getElementById('adherentSearchInput').value.trim();
    if (searchTerm.length < 1) { alert("Veuillez entrer un nom, prénom ou matricule"); return; }

    fetch(`/api/search-adherent?term=${encodeURIComponent(searchTerm)}`)
        .then(r => r.json())
        .then(data => {
            const resultsDiv = document.getElementById('adherentSearchResults');
            resultsDiv.innerHTML = '';

            if (!data || data.length === 0) {
                resultsDiv.innerHTML = '<div class="text-muted p-2">Aucun résultat trouvé</div>';
                return;
            }

            data.forEach(adherent => {
                if (!selectedAdherents.find(a => a.matricule === adherent.matricule)) {
                    const div = document.createElement('div');
                    div.className = 'search-result-item';
                    div.innerHTML = `
                        <div class="d-flex justify-content-between align-items-center">
                            <div>${adherent.matricule} - ${adherent.nom} ${adherent.prenom}</div>
                            <button class="btn btn-sm btn-success"
                                onclick="addToSelected('${adherent.matricule}', '${adherent.nom}', '${adherent.prenom}')">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    `;
                    resultsDiv.appendChild(div);
                }
            });
        });
});

document.getElementById('adherentSearchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') document.getElementById('searchButton').click();
});

function addToSelected(matricule, nom, prenom) {
    if (!selectedAdherents.some(a => a.matricule === matricule)) {
        selectedAdherents.push({ matricule, nom, prenom });
        updateSelectedDisplay();
    }
    document.getElementById('adherentSearchInput').value = '';
    document.getElementById('adherentSearchResults').innerHTML = '';
}

function removeFromSelected(matricule) {
    selectedAdherents = selectedAdherents.filter(a => a.matricule !== matricule);
    updateSelectedDisplay();
}

function updateSelectedDisplay() {
    const container = document.getElementById('selectedAdherents');
    container.innerHTML = '';
    selectedAdherents.forEach(adherent => {
        const div = document.createElement('div');
        div.className = 'selected-adherent mb-2';
        div.innerHTML = `
            <span>${adherent.matricule} - ${adherent.nom} ${adherent.prenom}</span>
            <button class="btn btn-sm btn-danger" onclick="removeFromSelected('${adherent.matricule}')">
                <i class="fas fa-times"></i>
            </button>
        `;
        container.appendChild(div);
    });
}

function confirmAddAdherents() {
    if (selectedAdherents.length === 0) { alert('Veuillez sélectionner au moins un adhérent'); return; }

    const matricules = selectedAdherents.map(a => a.matricule);

    fetch(`/ajouter_adherents_groupe/${currentGroupId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ matricules })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) alert(data.error);
        else {
            alert(`${data.added_count} adhérent(s) ajouté(s) avec succès`);
            closeAddAdherentModal();
            location.reload();
        }
    })
    .catch(err => { console.error('Erreur:', err); alert('Une erreur est survenue'); });
}

// ==========================
// 📌 Gestion du Mot de Passe
// ==========================
function ouvrirModal() { document.getElementById('modalChangerMotDePasse').style.display = 'block'; }
function fermerModal() { document.getElementById('modalChangerMotDePasse').style.display = 'none'; }

document.getElementById('changePasswordLink').addEventListener('click', ouvrirModal);
document.getElementById('submitMotDePasse').addEventListener('click', function() {
    const nouveauMotDePasse = document.getElementById('nouveauMotDePasse').value;
    const confirmationMotDePasse = document.getElementById('confirmationMotDePasse').value;

    if (nouveauMotDePasse !== confirmationMotDePasse) {
        alert("Les mots de passe ne correspondent pas.");
        return;
    }

    fetch('/changer_mot_de_passe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nouveau_mot_de_passe: nouveauMotDePasse, confirmation_mot_de_passe: confirmationMotDePasse })
    })
    .then(r => r.json())
    .then(data => {
        if (data.message) alert(data.message);
        else alert(data.error);
        fermerModal();
    })
    .catch(err => { console.error('Erreur:', err); alert('Une erreur est survenue.'); fermerModal(); });
});

// --------------------------
// 🔹 Bouton fermeture modal séance
// --------------------------
document.querySelectorAll('.closeSessionModal').forEach(btn => {
    btn.addEventListener('click', closeSessionModal);
});



// Variables globales pour les modals
let currentGroupeId = null;
let currentSessionType = null;

// Initialisation du datepicker
const sessionDatepicker = flatpickr("#sessionDate", {
    locale: "fr",
    dateFormat: "d/m/Y",
    altInput: true,
    altFormat: "j F Y",
    disableMobile: true,
    allowInput: true,
    defaultDate: "today"
});

// Fonctions pour ouvrir le modal d'ajout de séance
function openSessionModal(groupeId, typeSeance) {
    currentGroupeId = groupeId;
    currentSessionType = typeSeance || 'entrainement';
    
    // Pré-remplir le groupe
    document.getElementById('sessionGroupe').value = groupeId;
    
    // Pré-remplir le type de séance
    document.getElementById('sessionType').value = currentSessionType;
    
    // Définir les heures par défaut selon le type de séance
    if (currentSessionType === 'prep_physique') {
        document.getElementById('sessionHeureDebut').value = '17:00';
        document.getElementById('sessionHeureFin').value = '18:00';
    } else {
        document.getElementById('sessionHeureDebut').value = '18:00';
        document.getElementById('sessionHeureFin').value = '19:30';
    }
    
    // Afficher le modal
    document.getElementById('sessionModal').style.display = 'block';
    document.getElementById('modalBackdrop').style.display = 'block';
}

function openPrepPhysiqueModal(groupeId, typeSeance) {
    openSessionModal(groupeId, 'prep_physique');
}

function closeSessionModal() {
    document.getElementById('sessionModal').style.display = 'none';
    document.getElementById('modalBackdrop').style.display = 'none';
    currentGroupeId = null;
    currentSessionType = null;
}

// Fonction pour ajouter une séance
function addSession() {
    const groupeId = document.getElementById('sessionGroupe').value;
    const typeSeance = document.getElementById('sessionType').value;
    const date = document.getElementById('sessionDate').value;
    const heureDebut = document.getElementById('sessionHeureDebut').value;
    const heureFin = document.getElementById('sessionHeureFin').value;
    const terrain = document.getElementById('sessionTerrain').value;
    const repeatWeekly = document.getElementById('repeatWeekly').checked;

    // Validation des champs
    if (!groupeId || !date || !heureDebut || !heureFin || !terrain) {
        alert("Veuillez remplir tous les champs obligatoires");
        return;
    }

    // Validation que l'heure de fin est après l'heure de début
    if (heureFin <= heureDebut) {
        alert("L'heure de fin doit être après l'heure de début");
        return;
    }

    const data = {
        groupe_id: groupeId,
        type_seance: typeSeance,
        date: date,
        heure_debut: heureDebut,
        heure_fin: heureFin,
        terrain: terrain,
        repeat_weekly: repeatWeekly
    };

    // Envoyer la requête AJAX
    fetch('/ajouter_seance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur réseau');
        }
        return response.json();
    })
    .then(data => {
        if (data.message) {
            alert(data.message);
            closeSessionModal();
            // Recharger la page pour voir la nouvelle séance
            location.reload();
        } else {
            alert(data.error || "Erreur lors de l'ajout de la séance");
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert("Une erreur est survenue lors de l'ajout de la séance");
    });
}

// Fonction pour fermer tous les modals
function closeAllModals() {
    closeSessionModal();
    closeAddAdherentModal();
    closeAdherentsListModal();
}

// Créer le backdrop modal s'il n'existe pas
if (!document.getElementById('modalBackdrop')) {
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.id = 'modalBackdrop';
    backdrop.style.display = 'none';
    backdrop.onclick = closeAllModals;
    document.body.appendChild(backdrop);
}

// Ajouter le CSS pour le backdrop
const style = document.createElement('style');
style.textContent = `
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 999;
    }
    #sessionModal {
        z-index: 1000;
    }
`;
document.head.appendChild(style);