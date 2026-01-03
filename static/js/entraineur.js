// ========================================
// GESTION DU CHANGEMENT DE MOT DE PASSE
// ========================================

// Fonction pour ouvrir la fenêtre modale
function ouvrirModal() {
    document.getElementById('modalChangerMotDePasse').style.display = 'block';
}

// Fonction pour fermer la fenêtre modale
function fermerModal() {
    document.getElementById('modalChangerMotDePasse').style.display = 'none';
}

// Initialisation des événements pour le changement de mot de passe
function initPasswordChange() {
    // Attacher un événement au clic sur le lien "Mot de Passe"
    const changePasswordLink = document.getElementById('changePasswordLink');
    if (changePasswordLink) {
        changePasswordLink.addEventListener('click', function() {
            ouvrirModal(); // Ouvre la modale lorsque le lien est cliqué
        });
    }

    // Soumettre le changement de mot de passe
    const submitMotDePasse = document.getElementById('submitMotDePasse');
    if (submitMotDePasse) {
        submitMotDePasse.addEventListener('click', function() {
            const nouveauMotDePasse = document.getElementById('nouveauMotDePasse').value;
            const confirmationMotDePasse = document.getElementById('confirmationMotDePasse').value;

            // Vérification des mots de passe
            if (nouveauMotDePasse !== confirmationMotDePasse) {
                alert("Les mots de passe ne correspondent pas.");
                return;
            }

            // Créer l'objet pour la requête
            const data = {
                nouveau_mot_de_passe: nouveauMotDePasse,
                confirmation_mot_de_passe: confirmationMotDePasse
            };

            // Envoyer la requête POST pour changer le mot de passe
            fetch('/changer_mot_de_passe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else {
                    alert(data.error);
                }
                fermerModal(); // Fermer la fenêtre modale après soumission
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Une erreur est survenue.');
                fermerModal(); // Fermer la fenêtre modale en cas d'erreur
            });
        });
    }
}

// ========================================
// GESTION DES RÉSERVATIONS DE TERRAIN
// ========================================

// Initialisation des réservations
function initReservations() {
    const showReservationButton = document.getElementById('showReservationSection');
    const reservationSection = document.getElementById('reservationSection');
    
    if (!showReservationButton || !reservationSection) {
        console.error('Required elements not found');
        return;
    }

    showReservationButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Toggle the display of the reservation section
        const currentDisplay = reservationSection.style.display;
        reservationSection.style.display = currentDisplay === 'none' ? 'block' : 'none';
        
        // Scroll reservationSection into view if it's being shown
        if (reservationSection.style.display === 'block') {
            reservationSection.scrollIntoView({ behavior: 'smooth' });
            chargerReservations(); // Load reservations when section is shown
        }
    });

    // Initial load of reservations
    chargerReservations();
}

// Réinitialiser le formulaire de réservation
function resetReservationForm() {
    document.getElementById('reservationForm').reset();
}

// Obtenir la classe CSS pour le badge selon le statut
function getBadgeClass(status) {
    switch(status) {
        case 'acceptée':
            return 'bg-success';
        case 'refusée':
            return 'bg-danger';
        default:
            return 'bg-warning';
    }
}

// Charger les réservations depuis l'API
function chargerReservations() {
    fetch('/api/mes_reservations', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur réseau');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            afficherReservations(data.reservations);
        } else {
            console.error('Erreur:', data.error);
        }
    })
    .catch(error => {
        console.error('Erreur lors du chargement des réservations:', error);
    });
}

// Afficher les réservations dans le tableau
function afficherReservations(reservations) {
    const tbody = document.getElementById('reservationsList');
    tbody.innerHTML = ''; // Clear the table

    reservations.forEach(reservation => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${reservation.date}</td>
            <td>${reservation.heure_debut} - ${reservation.heure_fin}</td>
            <td>${reservation.numero_terrain}</td>
            <td>
                <span class="badge ${getBadgeClass(reservation.status)}">
                    ${reservation.status}
                </span>
            </td>
            <td>${reservation.commentaire || ''}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Soumettre une nouvelle réservation
function soumettreReservation() {
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;

    // Get form values
    const dateReservation = document.getElementById('dateReservation').value;
    const heureDebut = document.getElementById('heureDebut').value;
    const heureFin = document.getElementById('heureFin').value;
    const numeroTerrain = document.getElementById('numeroTerrain').value;
    const commentaire = document.getElementById('commentaire').value;

    // Validation
    if (!dateReservation || !heureDebut || !heureFin || !numeroTerrain) {
        alert('Veuillez remplir tous les champs obligatoires');
        submitBtn.disabled = false;
        return;
    }

    // Check end time is after start time
    if (heureDebut >= heureFin) {
        alert("L'heure de fin doit être après l'heure de début");
        submitBtn.disabled = false;
        return;
    }

    // Create data object
    const data = {
        date: dateReservation,
        heure_debut: heureDebut,
        heure_fin: heureFin,
        numero_terrain: parseInt(numeroTerrain),
        commentaire: commentaire
    };

    // Send request
    fetch('/api/reserver_terrain', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(data),
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Réservation créée avec succès');
            resetReservationForm();
            chargerReservations(); // Reload reservations instead of page refresh
        } else {
            alert('Erreur : ' + (data.error || 'Une erreur est survenue'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la création de la réservation : ' + (error.message || error));
    })
    .finally(() => {
        submitBtn.disabled = false;
    });
}

// ========================================
// GESTION DE L'EXPORTATION
// ========================================

let currentExportType = null;

// Préparer l'exportation
function prepareExport(type) {
    currentExportType = type;
    document.getElementById('exportScope').style.display = 'block';
}

// Déclencher l'exportation
function triggerExport(scope) {
    const url = new URL(window.location.href);
    const weekOffset = new URLSearchParams(window.location.search).get('week_offset') || 0;
    const dayOffset = new URLSearchParams(window.location.search).get('day_offset') || 0;
    
    const params = {
        week_offset: weekOffset,
        day_offset: dayOffset,
        export_type: currentExportType,
        scope: scope
    };

    window.location.href = `/export-schedule?${new URLSearchParams(params)}`;
    document.getElementById('exportScope').style.display = 'none';
}

// ========================================
// GESTION DES PRÉSENCES
// ========================================

// Ouvrir le modal de présence
function openPresenceModal(button) {
    const groupe = button.dataset.groupe;
    const date = button.dataset.date;
    const heure = button.dataset.heure;
    const entraineur = button.dataset.entraineur;
    const seanceId = button.dataset.seanceId;

    // Mettre à jour les champs du modal
    document.getElementById('modalGroupe').textContent = groupe;
    document.getElementById('modalDate').textContent = date;
    document.getElementById('modalHeure').textContent = heure;

    // Charger les adhérents du groupe
    fetch(`/api/adherents/${groupe}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch adherents.");
            }
            return response.json();
        })
        .then(adherents => {
            const adherentsList = document.getElementById('adherentsList');
            adherentsList.innerHTML = '';

            adherents.forEach(adherent => {
                const row = `
                    <tr>
                        <td>${adherent.matricule}</td>
                        <td>${adherent.nom}</td>
                        <td>${adherent.prenom}</td>
                        <td class="text-center">
                            <div class="btn-group" role="group">
                                <input type="radio" class="btn-check" name="presence_${adherent.matricule}" id="present_${adherent.matricule}" value="O" required>
                                <label class="btn btn-outline-success" for="present_${adherent.matricule}">
                                    <i class="fas fa-check"></i> Présent(e)
                                </label>
                                <input type="radio" class="btn-check" name="presence_${adherent.matricule}" id="absent_${adherent.matricule}" value="N" required>
                                <label class="btn btn-outline-danger" for="absent_${adherent.matricule}">
                                    <i class="fas fa-times"></i> Absent(e)
                                </label>
                            </div>
                        </td>
                    </tr>
                `;
                adherentsList.insertAdjacentHTML('beforeend', row);
            });
        })
        .catch(error => {
            console.error('Erreur lors du chargement des adhérents:', error);
            alert("Une erreur s'est produite lors du chargement des adhérents.");
        });

    // Afficher le modal
    const presenceModal = new bootstrap.Modal(document.getElementById('presenceModal'));
    presenceModal.show();
}

// Sauvegarder les présences
function savePresences() {
    const groupe = document.getElementById('modalGroupe').textContent;
    const date = document.getElementById('modalDate').textContent;
    const heure = document.getElementById('modalHeure').textContent;

    const trainerPresence = document.querySelector('input[name="trainerPresence"]:checked');
    if (!trainerPresence) {
        alert("Veuillez marquer votre présence en tant qu'entraîneur.");
        return;
    }

    const presences = [];
    document.querySelectorAll('#adherentsList tr').forEach(row => {
        const matricule = row.cells[0].textContent;
        const presence = row.querySelector('input[type="radio"]:checked');
        const seanceId = document.querySelector('[data-seance-id]').dataset.seanceId; // Fetch seance_id dynamically
        if (presence && seanceId) {
            presences.push({
                groupe_nom: groupe,
                adherent_matricule: matricule,
                date_seance: date,
                heure_debut: heure,
                est_present: presence.value,
                seance_id: seanceId
            });
        }
    });

    const data = {
        trainerPresence: {
            groupe_nom: groupe,
            entraineur_nom: document.querySelector('[data-entraineur]').dataset.entraineur,
            date_seance: date,
            heure_debut: heure,
            est_present: trainerPresence.value
        },
        adherentsPresence: presences
    };

    // Send the data to the server
    fetch('/api/presences', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to save presences.");
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert("Présences enregistrées avec succès!");
            bootstrap.Modal.getInstance(document.getElementById('presenceModal')).hide();
        } else {
            alert(`Erreur: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Erreur lors de l\'enregistrement des présences:', error);
        alert("Une erreur est survenue lors de l'enregistrement des présences.");
    });
}

// ========================================
// INITIALISATION PRINCIPALE
// ========================================

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le changement de mot de passe
    initPasswordChange();
    
    // Initialiser les réservations
    initReservations();
    
    console.log('Entraineur dashboard initialized successfully');
});

// Rendre les fonctions globalement accessibles
window.ouvrirModal = ouvrirModal;
window.fermerModal = fermerModal;
window.chargerReservations = chargerReservations;
window.soumettreReservation = soumettreReservation;
window.prepareExport = prepareExport;
window.triggerExport = triggerExport;
window.openPresenceModal = openPresenceModal;
window.savePresences = savePresences;
window.debugPresenceButtons = debugPresenceButtons;
window.addTestPresenceButton = addTestPresenceButton;