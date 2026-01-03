// ==========================
// 📌 Variables Globales
// ==========================
let currentGroupId = null;
let selectedAdherents = [];

// ==========================
// 📌 Initialisation Datepicker
// ==========================
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le datepicker une seule fois
    if (document.getElementById('sessionDate')) {
        flatpickr("#sessionDate", {
            locale: "fr",
            dateFormat: "Y-m-d",
            altInput: true,
            altFormat: "d/m/Y",
            disableMobile: true,
            allowInput: true,
            defaultDate: "today"
        });
    }

    // Event listeners pour changement entraîneur
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

    // Event listeners pour préparateur physique
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
                alert('Une erreur est survenue');
            });
        });
    });

    // Event listener pour recherche adhérents
    const searchButton = document.getElementById('searchButton');
    if (searchButton) {
        searchButton.addEventListener('click', searchAdherents);
    }

    const searchInput = document.getElementById('adherentSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchAdherents();
            }
        });
    }

    // Event listener pour changement mot de passe
    const changePasswordLink = document.getElementById('changePasswordLink');
    if (changePasswordLink) {
        changePasswordLink.addEventListener('click', ouvrirModal);
    }

    const submitMotDePasse = document.getElementById('submitMotDePasse');
    if (submitMotDePasse) {
        submitMotDePasse.addEventListener('click', changerMotDePasse);
    }
});

// ==========================
// 📌 Gestion des Séances
// ==========================


function openSessionModal(groupeId, typeSeance) {
    console.log('Opening session modal for group:', groupeId, 'type:', typeSeance);
    
    currentGroupId = groupeId;
    const type = typeSeance || 'entrainement';
    
    // 🎯 RÉCUPÉRER LE NOM DU GROUPE DEPUIS LA LIGNE DU TABLEAU
    const button = window.event.target.closest('button');
    const row = button.closest('tr');
    const groupeNom = row.querySelector('td:first-child').textContent.trim();
    
    console.log('Nom du groupe trouvé:', groupeNom);
    
    // Pré-remplir le groupe (ID caché + Nom visible)
    const groupeIdInput = document.getElementById('sessionGroupe');
    const groupeNomInput = document.getElementById('sessionGroupeNom');
    
    if (groupeIdInput) {
        groupeIdInput.value = groupeId;
    }
    
    if (groupeNomInput) {
        groupeNomInput.value = groupeNom;
        console.log('Valeur dans sessionGroupeNom:', groupeNomInput.value);
    } else {
        console.error('Element sessionGroupeNom non trouvé !');
    }
    
    // Pré-remplir le type de séance
    const typeSelect = document.getElementById('sessionType');
    if (typeSelect) {
        typeSelect.value = type;
    }
    
    // Définir les heures par défaut selon le type
    const heureDebut = document.getElementById('sessionHeureDebut');
    const heureFin = document.getElementById('sessionHeureFin');
    
    if (type === 'prep_physique') {
        if (heureDebut) heureDebut.value = '17:00';
        if (heureFin) heureFin.value = '18:00';
    } else {
        if (heureDebut) heureDebut.value = '18:00';
        if (heureFin) heureFin.value = '19:30';
    }
    
    // Afficher le modal
    const modal = document.getElementById('sessionModal');
    if (modal) {
        modal.style.display = 'block';
        console.log('Modal displayed');
    } else {
        console.error('Modal sessionModal not found!');
    }
}

function openPrepPhysiqueModal(groupeId) {
    console.log('Opening prep physique modal for group:', groupeId);
    openSessionModal(groupeId, 'prep_physique');
}



function closeSessionModal() {
    const modal = document.getElementById('sessionModal');
    if (modal) {
        modal.style.display = 'none';
    }
    currentGroupId = null;
}

function addSession() {
    const groupeId = document.getElementById('sessionGroupe').value;
    const typeSeance = document.getElementById('sessionType').value;
    const date = document.getElementById('sessionDate').value;
    const heureDebut = document.getElementById('sessionHeureDebut').value;
    const heureFin = document.getElementById('sessionHeureFin').value;
    const terrain = document.getElementById('sessionTerrain').value;
    const repeatWeekly = document.getElementById('repeatWeekly').checked;

    // Validation
    if (!groupeId || !date || !heureDebut || !heureFin || !terrain) {
        alert("Veuillez remplir tous les champs obligatoires");
        return;
    }

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

// ==========================
// 📌 Gestion des Groupes
// ==========================

function showGroupForm() {
    const form = document.getElementById("groupForm");
    if (form) {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
    }
}

function confirmGroupAdd() {
    const category = document.getElementById("groupCategory").value;
    const number = document.getElementById("groupNumber").value;
    const letter = document.getElementById("groupLetter").value.toUpperCase();
    const entraineurId = document.getElementById("groupEntraineur").value;
    const prepPhysiqueId = document.getElementById("groupPrepPhysique").value;
    const cotisation = document.getElementById("groupCotisation").value; // Nouveau champ

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
            prepPhysiqueId,
            cotisation: cotisation ? parseFloat(cotisation) : null
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
        alert("Une erreur est survenue");
    });
}

function openEditGroupModal(groupeId) {
    console.log('Ouverture modal pour groupe ID:', groupeId);
    
    // Masquer d'abord le modal et le backdrop pendant le chargement
    const modal = document.getElementById('editGroupModal');
    const backdrop = document.getElementById('editGroupBackdrop');
    
    if (!modal || !backdrop) {
        console.error('Modal ou backdrop non trouvé');
        alert('Erreur : Éléments du modal non trouvés');
        return;
    }
    
    // Afficher immédiatement avec un loader
    modal.style.display = 'block';
    backdrop.style.display = 'block';
    
    // Afficher un message de chargement
    document.getElementById('edit_adherents_list').innerHTML = 
        '<div class="text-center p-3"><i class="fas fa-spinner fa-spin"></i> Chargement...</div>';
    
    document.getElementById('edit_groupe_id').value = groupeId;
    
    // Charger les informations du groupe
    fetch(`/api/get_groupe_details/${groupeId}`)
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Données reçues:', data);
            
            if (data.success) {
                // Remplir les champs du formulaire
                document.getElementById('edit_groupe_nom').value = data.groupe.nom_groupe || '';
                document.getElementById('edit_entraineur').value = data.groupe.entraineur_id || '';
                document.getElementById('edit_prep_physique').value = data.groupe.prep_physique_id || '';
                document.getElementById('edit_cotisation').value = data.cotisation || '';
                
                // Charger les adhérents
                loadAdherentsForEdit(data.adherents || []);
            } else {
                throw new Error(data.error || 'Erreur inconnue');
            }
        })
        .catch(err => {
            console.error('Erreur complète:', err);
            alert('Erreur lors du chargement des détails: ' + err.message);
            // Fermer le modal en cas d'erreur
            closeEditGroupModal();
        });
}

function loadAdherentsForEdit(adherents) {
    const container = document.getElementById('edit_adherents_list');
    
    if (!container) {
        console.error('Container edit_adherents_list non trouvé');
        return;
    }
    
    container.innerHTML = '';
    
    if (!adherents || adherents.length === 0) {
        container.innerHTML = '<div class="text-muted text-center p-2">Aucun adhérent dans ce groupe</div>';
        return;
    }
    
    adherents.forEach(adherent => {
        const div = document.createElement('div');
        div.className = 'd-flex justify-content-between align-items-center p-2 border-bottom';
        div.innerHTML = `
            <div>
                <strong>${adherent.matricule}</strong> - ${adherent.nom} ${adherent.prenom}
            </div>
            <button type="button" class="btn btn-sm btn-danger" 
                    onclick="removeAdherentFromGroupEdit('${adherent.matricule}')">
                <i class="fas fa-times"></i>
            </button>
        `;
        container.appendChild(div);
    });
}

function removeAdherentFromGroupEdit(matricule) {
    if (!confirm('Retirer cet adhérent du groupe ?')) return;
    
    const groupeId = document.getElementById('edit_groupe_id').value;
    
    if (!groupeId) {
        alert('Erreur : ID du groupe non trouvé');
        return;
    }
    
    fetch(`/retirer_adherent_groupe/${groupeId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ matricule })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Recharger la liste des adhérents
            openEditGroupModal(groupeId);
        } else {
            alert(data.error || 'Erreur lors du retrait');
        }
    })
    .catch(err => {
        console.error('Erreur:', err);
        alert('Erreur lors du retrait: ' + err.message);
    });
}

function saveGroupEdit() {
    const groupeId = document.getElementById('edit_groupe_id').value;
    const entraineurId = document.getElementById('edit_entraineur').value;
    const prepPhysiqueId = document.getElementById('edit_prep_physique').value;
    const cotisation = document.getElementById('edit_cotisation').value;
    
    if (!groupeId) {
        alert('Erreur : ID du groupe non trouvé');
        return;
    }
    
    if (!entraineurId) {
        alert('Veuillez sélectionner un entraîneur');
        return;
    }
    
    fetch(`/api/update_groupe/${groupeId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            entraineur_id: entraineurId,
            prep_physique_id: prepPhysiqueId || null,
            cotisation: cotisation ? parseFloat(cotisation) : null
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Groupe modifié avec succès');
            location.reload();
        } else {
            alert(data.error || 'Erreur lors de la sauvegarde');
        }
    })
    .catch(err => {
        console.error('Erreur:', err);
        alert('Erreur lors de la sauvegarde: ' + err.message);
    });
}

function closeEditGroupModal() {
    const modal = document.getElementById('editGroupModal');
    const backdrop = document.getElementById('editGroupBackdrop');
    
    if (modal) modal.style.display = 'none';
    if (backdrop) backdrop.style.display = 'none';
}

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

// ==========================
// 📌 Gestion des Adhérents
// ==========================

function openAddAdherentModal(groupId) {
    currentGroupId = groupId;
    selectedAdherents = [];

    // Charger les membres actuels
    fetch(`/api/get_adherents_groupe/${groupId}`)
        .then(r => r.json())
        .then(data => {
            console.log('Données reçues:', data); // Debug
            
            const container = document.getElementById('currentMembers');
            if (!container) {
                console.error('Container currentMembers non trouvé');
                return;
            }
            
            container.innerHTML = '';

            if (!data.adherents || data.adherents.length === 0) {
                container.innerHTML = '<div class="text-muted p-3 text-center">Aucun membre dans ce groupe</div>';
                return;
            }

            // Créer le tableau
            let tableHTML = `
                <table class="table table-sm table-hover">
                    <thead>
                        <tr>
                            <th>Matricule</th>
                            <th>Nom</th>
                            <th>Prénom</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            data.adherents.forEach(adherent => {
                tableHTML += `
                    <tr>
                        <td>${adherent.matricule}</td>
                        <td>${adherent.nom}</td>
                        <td>${adherent.prenom}</td>
                        <td>
                            <button class="btn btn-sm btn-danger remove-member-btn" 
                                    onclick="removeFromGroup('${adherent.matricule}')">
                                <i class="fas fa-times"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });

            tableHTML += `
                    </tbody>
                </table>
            `;

            container.innerHTML = tableHTML;
            console.log('Tableau créé avec', data.adherents.length, 'adhérents');
        })
        .catch(err => {
            console.error('Erreur lors du chargement:', err);
            const container = document.getElementById('currentMembers');
            if (container) {
                container.innerHTML = '<div class="text-danger p-3">Erreur lors du chargement des membres</div>';
            }
        });

    updateSelectedDisplay();
    
    const searchInput = document.getElementById('adherentSearchInput');
    if (searchInput) searchInput.value = '';
    
    const searchResults = document.getElementById('adherentSearchResults');
    if (searchResults) searchResults.innerHTML = '';
    
    const modal = document.getElementById('addAdherentModal');
    if (modal) {
        modal.style.display = 'block';
    } else {
        console.error('Modal addAdherentModal non trouvé');
    }
}

function closeAddAdherentModal() {
    document.getElementById('addAdherentModal').style.display = 'none';
    document.getElementById('adherentSearchInput').value = '';
    document.getElementById('adherentSearchResults').innerHTML = '';
    selectedAdherents = [];
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
        if (data.error) {
            alert(data.error);
        } else {
            openAddAdherentModal(currentGroupId);
        }
    })
    .catch(err => {
        console.error('Erreur:', err);
        alert('Une erreur est survenue');
    });
}

function searchAdherents() {
    const searchTerm = document.getElementById('adherentSearchInput').value.trim();
    if (searchTerm.length < 1) {
        alert("Veuillez entrer un nom, prénom ou matricule");
        return;
    }

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
        })
        .catch(err => {
            console.error('Erreur:', err);
            alert('Erreur lors de la recherche');
        });
}

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
    if (!container) return;
    
    container.innerHTML = '';
    
    if (selectedAdherents.length === 0) {
        container.innerHTML = '<div class="text-muted p-2">Aucun adhérent sélectionné</div>';
        return;
    }
    
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
    if (selectedAdherents.length === 0) {
        alert('Veuillez sélectionner au moins un adhérent');
        return;
    }

    const matricules = selectedAdherents.map(a => a.matricule);

    fetch(`/ajouter_adherents_groupe/${currentGroupId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ matricules })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(`${data.added_count} adhérent(s) ajouté(s) avec succès`);
            closeAddAdherentModal();
            location.reload();
        }
    })
    .catch(err => {
        console.error('Erreur:', err);
        alert('Une erreur est survenue');
    });
}

// ==========================
// 📌 Modal Liste Adhérents
// ==========================

function openAdherentsListModal(nomGroupe) {
    document.getElementById('adherentsListContainer').innerHTML = "<p class='text-muted'>Chargement...</p>";
    document.getElementById('adherentsListModal').style.display = 'block';

    fetch(`/api/get_adherents_groupe/${encodeURIComponent(nomGroupe)}`)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('adherentsListContainer');
            if (!data.adherents || data.adherents.length === 0) {
                container.innerHTML = '<div class="text-muted">Aucun adhérent dans ce groupe</div>';
                return;
            }
            let table = `<table class="table table-striped">
                <thead>
                    <tr>
                        <th>Matricule</th>
                        <th>Nom</th>
                        <th>Prénom</th>
                    </tr>
                </thead>
                <tbody>`;
            data.adherents.forEach(a => {
                table += `<tr>
                    <td>${a.matricule}</td>
                    <td>${a.nom}</td>
                    <td>${a.prenom}</td>
                </tr>`;
            });
            table += '</tbody></table>';
            container.innerHTML = table;
        })
        .catch(err => {
            console.error('Erreur:', err);
            document.getElementById('adherentsListContainer').innerHTML = 
                '<div class="text-danger">Erreur lors du chargement</div>';
        });
}

function closeAdherentsListModal() {
    document.getElementById('adherentsListModal').style.display = 'none';
}

// ==========================
// 📌 Gestion Mot de Passe
// ==========================

function ouvrirModal() {
    document.getElementById('modalChangerMotDePasse').style.display = 'block';
}

function fermerModal() {
    document.getElementById('modalChangerMotDePasse').style.display = 'none';
    document.getElementById('nouveauMotDePasse').value = '';
    document.getElementById('confirmationMotDePasse').value = '';
}

function changerMotDePasse() {
    const nouveauMotDePasse = document.getElementById('nouveauMotDePasse').value;
    const confirmationMotDePasse = document.getElementById('confirmationMotDePasse').value;

    if (!nouveauMotDePasse || !confirmationMotDePasse) {
        alert("Veuillez remplir tous les champs");
        return;
    }

    if (nouveauMotDePasse !== confirmationMotDePasse) {
        alert("Les mots de passe ne correspondent pas.");
        return;
    }

    fetch('/changer_mot_de_passe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            nouveau_mot_de_passe: nouveauMotDePasse,
            confirmation_mot_de_passe: confirmationMotDePasse
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            fermerModal();
        } else {
            alert(data.error || 'Erreur lors du changement de mot de passe');
        }
    })
    .catch(err => {
        console.error('Erreur:', err);
        alert('Une erreur est survenue.');
    });
}

// ==========================
// 📌 Utilitaires
// ==========================

// Fermer les modals en cliquant en dehors
window.onclick = function(event) {
    const sessionModal = document.getElementById('sessionModal');
    const addAdherentModal = document.getElementById('addAdherentModal');
    const adherentsListModal = document.getElementById('adherentsListModal');
    const passwordModal = document.getElementById('modalChangerMotDePasse');
    
    if (event.target === sessionModal) {
        closeSessionModal();
    }
    if (event.target === addAdherentModal) {
        closeAddAdherentModal();
    }
    if (event.target === adherentsListModal) {
        closeAdherentsListModal();
    }
    if (event.target === passwordModal) {
        fermerModal();
    }
}