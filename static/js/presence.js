// Module pattern pour éviter les conflits de variables - VERSION COMPLÈTE AVEC GROUPES AMÉLIORÉS
const PresenceModule = (function() {
    // Variables privées
    let currentSearchType = null;
    let searchResults = [];
    let currentDetails = null;
    let currentName = '';
    let currentExpandedRows = new Set(); // Pour garder trace des lignes expandées
    
    const API_BASE_URL = '/api';

    // Initialisation
    function init() {
        setupEventListeners();
        setDefaultDates();
    }

    // Configuration des écouteurs d'événements
    function setupEventListeners() {
        // Sélection type
        $('input[name="searchType"]').on('change', function() {
            currentSearchType = $(this).val();
            $('#searchSection').addClass('visible');
            updateSearchPlaceholder();
        });

        // Toggle recherche spécifique
        $('#searchToggle').on('change', function() {
            if ($(this).is(':checked')) {
                $('#searchInputGroup').show();
            } else {
                $('#searchInputGroup').hide();
                $('#searchInput').val('');
            }
        });

        // Rechercher
        $('#searchBtn').on('click', performSearchHandler);

        // Export Excel global
        $('#exportBtn').on('click', exportGlobalData);

        // Export Excel des détails
        $('#exportDetailsBtn').on('click', exportDetailsData);
        
        // Enter key sur le champ de recherche
        $('#searchInput').on('keypress', function(e) {
            if (e.which === 13) {
                performSearchHandler();
            }
        });
    }

    // Mise à jour du placeholder de recherche
    function updateSearchPlaceholder() {
        const labels = {
            'adherent': 'Rechercher un adhérent par nom, prénom ou matricule...',
            'entraineur': 'Rechercher un entraîneur par nom ou prénom...',
            'groupe': 'Rechercher un groupe par nom...'
        };
        $('#searchInput').attr('placeholder', labels[currentSearchType] || 'Rechercher...');
        $('#searchLabel').text(`Rechercher ${currentSearchType}`);
    }

    // Gestionnaire de recherche
    function performSearchHandler() {
        if (!currentSearchType) {
            showError('Veuillez sélectionner un type de recherche');
            return;
        }

        const startDate = $('#startDate').val();
        const endDate = $('#endDate').val();
        const searchTerm = $('#searchToggle').is(':checked') ? $('#searchInput').val() : '';

        if (!startDate || !endDate) {
            showError('Veuillez sélectionner les dates de début et fin');
            return;
        }

        if (new Date(startDate) > new Date(endDate)) {
            showError('La date de début doit être antérieure à la date de fin');
            return;
        }

        performSearch(startDate, endDate, searchTerm);
    }

    // Exécution de la recherche
    function performSearch(startDate, endDate, searchTerm) {
        $('#loadingSpinner').show();
        $('#resultsContent').empty();
        $('#resultsSection').addClass('visible');
        $('#exportBtn').prop('disabled', true);

        const requestData = {
            type: currentSearchType,
            start_date: startDate,
            end_date: endDate,
            search_term: searchTerm
        };

        $.ajax({
            url: `${API_BASE_URL}/presences/search`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(requestData),
            success: function(response) {
                $('#loadingSpinner').hide();
                
                if (response.status === 'success') {
                    displayResults(response.data || []);
                    $('#exportBtn').prop('disabled', response.data.length === 0);
                } else {
                    showError(response.message || 'Erreur lors de la recherche');
                }
            },
            error: function(xhr, status, error) {
                console.error('Erreur lors de la recherche:', error);
                $('#loadingSpinner').hide();
                
                let errorMessage = 'Erreur serveur. Veuillez réessayer plus tard.';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
                }
                showError(errorMessage);
            }
        });
    }

    // Affichage des résultats
    function displayResults(data) {
        searchResults = data;
        $('#resultsCount').text(`${data.length} résultat(s)`);

        if (data.length === 0) {
            $('#resultsContent').html(`
                <div class="empty-state">
                    <i class="fas fa-search empty-icon"></i>
                    <p>Aucun résultat trouvé pour les critères sélectionnés</p>
                </div>
            `);
            return;
        }

        let tableHtml = `
            <div class="table-container">
                <table class="results-table">
                    <thead><tr>`;

        if (currentSearchType === 'adherent') {
            tableHtml += `<th>Matricule</th><th>Nom</th><th>Prénom</th><th>Statistiques & Présences</th><th>Actions</th>`;
        } else if (currentSearchType === 'entraineur') {
            tableHtml += `<th>Nom Entraîneur</th><th>Statistiques & Présences</th><th>Actions</th>`;
        } else if (currentSearchType === 'groupe') {
            tableHtml += `<th>Nom du Groupe</th><th>Statistiques & Présences</th><th>Actions</th>`;
        }

        tableHtml += `</tr></thead><tbody>`;

        data.forEach(item => {
            let presentCount = 0;
            let absentCount = 0;
            let totalHeures = 0;
            let attendanceHtml = '';

            if (item.sessions && item.sessions.length > 0) {
                item.sessions.forEach(session => {
                    const isPresent = (session.est_present === 'O');
                    if (isPresent) {
                        presentCount++;
                    } else {
                        absentCount++;
                    }

                    let dureeHeures = session.duree_heures || 1.5;
                    if (isPresent) {
                        totalHeures += dureeHeures;
                    }

                    const date = new Date(session.date_seance);
                    const day = date.getDate();
                    const month = date.getMonth() + 1;

                    // Pour les groupes, ajouter un attribut data pour le clic
                    const clickableClass = currentSearchType === 'groupe' ? 'attendance-day-clickable' : '';
                    const dataAttrs = currentSearchType === 'groupe' ? 
                        `data-groupe="${item.nom}" data-date="${session.date_seance}" data-heure="${session.heure_debut}"` : '';

                    attendanceHtml += `
                        <div class="attendance-day ${isPresent ? 'present' : 'absent'} ${clickableClass}" 
                             ${dataAttrs}
                             title="${formatDateForDisplay(session.date_seance)} - ${session.heure_debut} - ${isPresent ? 'Présent' : 'Absent'}
${session.groupe_nom ? 'Groupe: ' + session.groupe_nom : ''}
${session.entraineur_nom ? 'Entraîneur: ' + session.entraineur_nom : ''}">
                            ${day}/${month}
                        </div>
                    `;
                });
            }

            tableHtml += '<tr>';

            if (currentSearchType === 'adherent') {
                tableHtml += `<td><strong>${item.matricule || 'N/A'}</strong></td>
                              <td><strong>${item.nom || 'N/A'}</strong></td>
                              <td>${item.prenom || 'N/A'}</td>`;
            } else if (currentSearchType === 'entraineur') {
                tableHtml += `<td><strong>${item.nom || 'N/A'}</strong></td>`;
            } else if (currentSearchType === 'groupe') {
                tableHtml += `<td><strong>${item.nom || 'N/A'}</strong></td>`;
            }

            tableHtml += `
                <td>
                    <div class="stats-summary">
                        <div class="stat-card present">
                            <div class="stat-number">${presentCount}</div>
                            <div class="stat-label">Présent(e)${presentCount > 1 ? 's' : ''}</div>
                        </div>
                        <div class="stat-card absent">
                            <div class="stat-number">${absentCount}</div>
                            <div class="stat-label">Absent(e)${absentCount > 1 ? 's' : ''}</div>
                        </div>
                        <div class="stat-card total">
                            <div class="stat-number">${presentCount + absentCount}</div>
                            <div class="stat-label">Total séances</div>
                        </div>
                        <div class="stat-card hours">
                            <div class="stat-number">${totalHeures.toFixed(1)}h</div>
                            <div class="stat-label">Heures totales de Présence</div>
                        </div>
                    </div>
                    <div class="attendance-grid">${attendanceHtml}</div>
                </td>
            `;

            tableHtml += '<td>';
            if (currentSearchType === 'adherent') {
                tableHtml += `<button class="btn btn-sm btn-outline-primary view-details-btn" 
                            data-matricule="${item.matricule}" data-nom="${item.nom}" data-prenom="${item.prenom}">
                        <i class="fas fa-eye"></i> Voir détails</button>`;
            } else if (currentSearchType === 'entraineur') {
                tableHtml += `<button class="btn btn-sm btn-outline-primary view-details-btn-entraineur" data-nom="${item.nom}">
                        <i class="fas fa-eye"></i> Voir détails</button>`;
            } else if (currentSearchType === 'groupe') {
                tableHtml += `<button class="btn btn-sm btn-outline-primary view-details-btn-groupe" data-nom="${item.nom}">
                        <i class="fas fa-eye"></i> Voir détails</button>`;
            }
            tableHtml += '</td></tr>';
        });

        tableHtml += `</tbody></table></div>`;
        $('#resultsContent').html(tableHtml);
        
        $('.view-details-btn').on('click', function() {
            showAdherentDetails($(this).data('matricule'), $(this).data('nom'), $(this).data('prenom'));
        });
        $('.view-details-btn-entraineur').on('click', function() {
            showEntraineurDetails($(this).data('nom'));
        });
        $('.view-details-btn-groupe').on('click', function() {
            showGroupeDetails($(this).data('nom'));
        });
        
        // Event listener pour les dates cliquables des groupes
        $('.attendance-day-clickable').on('click', function() {
            const groupe = $(this).data('groupe');
            const date = $(this).data('date');
            const heure = $(this).data('heure');
            showGroupeAdherentsModal(groupe, date, heure);
        });
    }

    function formatDateForDisplay(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR');
    }

    function showError(message) {
        $('#resultsContent').html(`
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Erreur:</strong> ${message}
            </div>
        `);
        $('#resultsCount').text('0 résultat(s)');
        $('#exportBtn').prop('disabled', true);
    }

    function exportGlobalData() {
        if (searchResults.length === 0) {
            alert('Aucune donnée à exporter');
            return;
        }

        const params = new URLSearchParams({
            type: currentSearchType,
            start_date: $('#startDate').val(),
            end_date: $('#endDate').val(),
            search_term: $('#searchToggle').is(':checked') ? $('#searchInput').val() : ''
        });

        window.open(`${API_BASE_URL}/presences/export?${params.toString()}`, '_blank');
    }

    function showAdherentDetails(matricule, nom, prenom) {
        currentName = `${nom} ${prenom}`;
        currentDetails = [];
        currentExpandedRows = new Set();
        
        $('#toggleAbsencesBtn').remove();
        $('#adherentName').text(`Chargement des détails de ${currentName}...`);
        $('#detailsTable tbody').html(`
            <tr><td colspan="6" class="text-center">
                <div class="spinner-border spinner-border-sm" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                Chargement des données...
            </td></tr>
        `);
        
        $('#detailsTable thead tr').html(`
            <th>Date</th><th>Groupe</th><th>Entraîneur</th>
            <th>Heure début</th><th>Durée</th><th>État</th>
        `);
        
        $('#detailsModal').modal('show');
        
        const params = new URLSearchParams({
            start_date: $('#startDate').val(),
            end_date: $('#endDate').val()
        });
        
        $.ajax({
            url: `/get_adherent_presences/${matricule}?${params.toString()}`,
            method: 'GET',
            success: function(response) {
                currentDetails = response.presences;
                displayDetailsWithDuration(response.presences, response.total_heures, response, 'adherent');
                $('#adherentName').text(`Détails des présences de ${response.nom}`);
            },
            error: function(xhr, status, error) {
                console.error('Erreur:', error);
                showModalError('Impossible de charger les détails. Veuillez réessayer.');
            }
        });
    }

    function showEntraineurDetails(nomEntraineur) {
        currentName = nomEntraineur;
        currentDetails = [];
        currentExpandedRows = new Set();
        
        $('#toggleAbsencesBtn').remove();
        $('#adherentName').text(`Chargement des détails de ${nomEntraineur}...`);
        $('#detailsTable tbody').html(`
            <tr><td colspan="6" class="text-center">
                <div class="spinner-border spinner-border-sm" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                Chargement des données...
            </td></tr>
        `);
        
        $('#detailsTable thead tr').html(`
            <th>Date</th><th>Groupe</th><th>Entraîneur</th>
            <th>Heure début</th><th>Durée</th><th>État</th>
        `);
        
        $('#detailsModal').modal('show');
        
        const params = new URLSearchParams({
            start_date: $('#startDate').val(),
            end_date: $('#endDate').val()
        });
        
        $.ajax({
            url: `/get_entraineur_presences/${encodeURIComponent(nomEntraineur)}?${params.toString()}`,
            method: 'GET',
            success: function(response) {
                currentDetails = response.presences;
                displayDetailsWithDuration(response.presences, response.total_heures, response, 'entraineur');
                $('#adherentName').text(`Détails des présences de ${response.nom}`);
            },
            error: function(xhr, status, error) {
                console.error('Erreur:', error);
                showModalError('Impossible de charger les détails. Veuillez réessayer.');
            }
        });
    }

    function showGroupeDetails(nomGroupe) {
        currentName = nomGroupe;
        currentDetails = [];
        currentExpandedRows = new Set();
        
        $('#toggleAbsencesBtn').remove();
        $('#adherentName').text(`Chargement des détails du groupe ${nomGroupe}...`);
        $('#detailsTable tbody').html(`
            <tr><td colspan="7" class="text-center">
                <div class="spinner-border spinner-border-sm" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                Chargement des données...
            </td></tr>
        `);
        
        // Header spécifique pour les groupes avec colonne Actions
        $('#detailsTable thead tr').html(`
            <th>Date</th><th>Groupe</th><th>Entraîneur</th>
            <th>Heure début</th><th>Durée</th><th>État</th><th>Actions</th>
        `);
        
        $('#detailsModal').modal('show');
        
        const params = new URLSearchParams({
            start_date: $('#startDate').val(),
            end_date: $('#endDate').val()
        });
        
        $.ajax({
            url: `/get_groupe_presences/${encodeURIComponent(nomGroupe)}?${params.toString()}`,
            method: 'GET',
            success: function(response) {
                currentDetails = response.presences;
                displayDetailsWithDuration(response.presences, response.total_heures_present, response, 'groupe');
                $('#adherentName').text(`Détails des séances du groupe ${response.nom}`);
            },
            error: function(xhr, status, error) {
                console.error('Erreur:', error);
                showModalError('Impossible de charger les détails. Veuillez réessayer.');
            }
        });
    }

    // FONCTION CLÉ - AFFICHAGE AVEC BOUTON FILTRE ET EXPANDABLE ROWS POUR GROUPES
    function displayDetailsWithDuration(details, totalHeures, response, type) {
        const tbody = $('#detailsTable tbody');
        tbody.empty();
        
        if (!details || details.length === 0) {
            tbody.append(`
                <tr><td colspan="${type === 'groupe' ? '7' : '6'}" class="text-center text-muted">
                    <i class="fas fa-info-circle me-2"></i>
                    Aucune donnée de présence trouvée pour cette période
                </td></tr>
            `);
            $('#exportDetailsBtn').prop('disabled', true);
            return;
        }
        
        $('#exportDetailsBtn').prop('disabled', false);
        
        // Ajouter le bouton de filtre
        const filterButtonHtml = `
            <div class="d-flex justify-content-end mb-3" id="filterAbsenceContainer">
                <button class="btn btn-sm btn-outline-secondary" id="toggleAbsencesBtn" data-show="true">
                    <i class="fas fa-eye-slash"></i> Masquer les absences
                </button>
            </div>
        `;
        
        $('#filterAbsenceContainer').remove();
        $('.modal-body .d-flex:first').after(filterButtonHtml);
        
        $('#toggleAbsencesBtn').off('click').on('click', function() {
            const showAbsences = $(this).data('show');
            
            if (showAbsences) {
                $('.row-absent').hide();
                $(this).html('<i class="fas fa-eye"></i> Afficher les absences');
                $(this).data('show', false);
            } else {
                $('.row-absent').show();
                $(this).html('<i class="fas fa-eye-slash"></i> Masquer les absences');
                $(this).data('show', true);
            }
        });
        
        // Générer les lignes
        details.forEach((detail, index) => {
            let badgeClass = 'bg-secondary';
            let etatText = detail.etat || 'Non marqué';
            let rowClass = index % 2 === 0 ? 'table-light' : '';
            
            if (detail.etat === 'Présent') {
                badgeClass = 'bg-success';
                rowClass += ' row-present';
            } else if (detail.etat === 'Absent') {
                badgeClass = 'bg-danger';
                rowClass += ' row-absent';
            } else if (detail.etat === 'Mixte') {
                badgeClass = 'bg-warning';
                rowClass += ' row-mixte';
            } else {
                rowClass += ' row-non-marque';
            }
            
            const rowId = `detail-row-${index}`;
            const expandRowId = `expand-row-${index}`;
            
            let row = `
                <tr class="${rowClass}" id="${rowId}">
                    <td>${detail.date || 'N/A'}</td>
                    <td>${detail.groupe || 'N/A'}</td>
                    <td>${detail.entraineur || 'N/A'}</td>
                    <td>${detail.heure_debut || 'N/A'}</td>
                    <td><strong>${detail.duree_heures}h</strong> (${detail.duree_minutes}min)</td>
                    <td><span class="badge ${badgeClass}">${etatText}</span>
                        ${detail.adherents_presents !== undefined ? `<br><small class="text-muted">${detail.adherents_presents} présent(s), ${detail.adherents_absents} absent(s)</small>` : ''}
                    </td>
            `;
            
            // Pour les groupes, ajouter le bouton "Voir adhérents"
            if (type === 'groupe') {
                row += `
                    <td>
                        <button class="btn btn-sm btn-outline-info toggle-adherents-btn" 
                                data-index="${index}"
                                data-groupe="${detail.groupe}"
                                data-date="${detail.date}"
                                data-heure="${detail.heure_debut}">
                            <i class="fas fa-users"></i> Voir adhérents
                        </button>
                    </td>
                `;
            }
            
            row += '</tr>';
            
            // Ajouter la ligne principale
            tbody.append(row);
            
            // Pour les groupes, préparer la ligne expandable (cachée par défaut)
            if (type === 'groupe') {
                const expandRow = `
                    <tr class="expand-row" id="${expandRowId}" style="display: none;">
                        <td colspan="7" style="background-color: #f8f9fa; padding: 0;">
                            <div class="adherents-list-container" style="padding: 15px;">
                                <div class="text-center">
                                    <div class="spinner-border spinner-border-sm" role="status">
                                        <span class="visually-hidden">Chargement...</span>
                                    </div>
                                    Chargement des adhérents...
                                </div>
                            </div>
                        </td>
                    </tr>
                `;
                tbody.append(expandRow);
            }
        });
        
        // Event listener pour les boutons "Voir adhérents" (pour les groupes)
        if (type === 'groupe') {
            $('.toggle-adherents-btn').off('click').on('click', function() {
                const index = $(this).data('index');
                const groupe = $(this).data('groupe');
                const date = $(this).data('date');
                const heure = $(this).data('heure');
                const expandRowId = `expand-row-${index}`;
                const $expandRow = $(`#${expandRowId}`);
                const $btn = $(this);
                
                if (currentExpandedRows.has(index)) {
                    // Fermer la ligne
                    $expandRow.slideUp(300);
                    currentExpandedRows.delete(index);
                    $btn.html('<i class="fas fa-users"></i> Voir adhérents');
                } else {
                    // Ouvrir la ligne et charger les données
                    loadAdherentsForSeance(groupe, date, heure, expandRowId);
                    $expandRow.slideDown(300);
                    currentExpandedRows.add(index);
                    $btn.html('<i class="fas fa-users"></i> Masquer adhérents');
                }
            });
        }
        
        // Totaux
        if (response && response.count_present !== undefined) {
            tbody.append(`
                <tr class="table-success">
                    <td colspan="${type === 'groupe' ? '5' : '4'}" class="text-end"><strong>Heures présent(e) :</strong></td>
                    <td colspan="2"><strong>${response.total_heures_present || 0}h</strong> (${response.count_present} séances)</td>
                </tr>
                <tr class="table-danger">
                    <td colspan="${type === 'groupe' ? '5' : '4'}" class="text-end"><strong>Heures absent(e) :</strong></td>
                    <td colspan="2"><strong>${response.total_heures_absent || 0}h</strong> (${response.count_absent} séances)</td>
                </tr>
            `);
            
            if (response.count_non_marque > 0) {
                tbody.append(`
                    <tr class="table-secondary">
                        <td colspan="${type === 'groupe' ? '5' : '4'}" class="text-end"><strong>Séances non marquées :</strong></td>
                        <td colspan="2"><strong>${response.count_non_marque} séances</strong></td>
                    </tr>
                `);
            }
        }
        
        const totalSeances = (response.count_present || 0) + (response.count_absent || 0) + (response.count_non_marque || 0);
        tbody.append(`
            <tr class="table-info">
                <td colspan="${type === 'groupe' ? '5' : '4'}" class="text-end"><strong>Total :</strong></td>
                <td colspan="2"><strong>${totalSeances} séances</strong> (Présent: ${response.total_heures_present || 0}h + Absent: ${response.total_heures_absent || 0}h)</td>
            </tr>
        `);
    }

function loadAdherentsForSeance(groupe, date, heure, expandRowId) {
    const $container = $(`#${expandRowId} .adherents-list-container`);
    
    // Chercher les détails dans les données déjà chargées
    const seance = currentDetails.find(s => 
        s.groupe === groupe && 
        s.date === date && 
        s.heure_debut === heure
    );
    
    if (seance && seance.adherents_details) {
        displayAdherentsInExpandRow({
            seance: {
                groupe: seance.groupe,
                date: seance.date,
                heure: seance.heure_debut,
                entraineur: seance.entraineur
            },
            adherents: seance.adherents_details,
            statistiques: {
                total: seance.total_adherents,
                presents: seance.adherents_presents,
                absents: seance.adherents_absents,
                non_marques: seance.total_adherents - (seance.adherents_presents + seance.adherents_absents)
            }
        }, $container);
    } else {
        // Fallback à l'appel API si les données ne sont pas déjà disponibles
        $.ajax({
            url: '/get_groupe_adherents_by_seance',
            method: 'GET',
            data: {
                groupe_nom: groupe,
                date_seance: date,
                heure_debut: heure
            },
            success: function(response) {
                if (response.success) {
                    displayAdherentsInExpandRow(response, $container);
                } else {
                    $container.html(`
                        <div class="alert alert-warning" role="alert">
                            <i class="fas fa-exclamation-triangle"></i>
                            ${response.error || 'Erreur lors du chargement des adhérents'}
                        </div>
                    `);
                }
            },
            error: function(xhr, status, error) {
                console.error('Erreur:', error);
                $container.html(`
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-circle"></i>
                        Impossible de charger les adhérents. Veuillez réessayer.
                    </div>
                `);
            }
        });
    }
}

    // Afficher les adhérents dans la ligne expandable
    function displayAdherentsInExpandRow(data, $container) {
        if (!data.adherents || data.adherents.length === 0) {
            $container.html(`
                <div class="alert alert-info" role="alert">
                    <i class="fas fa-info-circle"></i>
                    Aucun adhérent trouvé pour cette séance
                </div>
            `);
            return;
        }

        const presents = data.adherents.filter(a => a.est_present === 'O');
        const absents = data.adherents.filter(a => a.est_present === 'N');

        let html = `
            <div class="row">
                <div class="col-md-12 mb-3">
                    <h6><i class="fas fa-info-circle text-info"></i> Séance du ${data.seance.date} à ${data.seance.heure}</h6>
                    <p class="mb-2">
                        <span class="badge bg-success">${presents.length} Présent(s)</span>
                        <span class="badge bg-danger ms-2">${absents.length} Absent(s)</span>
                        <span class="badge bg-info ms-2">${data.statistiques.total} Total</span>
                    </p>
                </div>
            </div>
            <div class="row">
        `;

        // Colonne des présents
        if (presents.length > 0) {
            html += `
                <div class="col-md-6">
                    <h6 class="text-success"><i class="fas fa-check-circle"></i> Présents (${presents.length})</h6>
                    <div class="table-responsive">
                        <table class="table table-sm table-bordered">
                            <thead class="table-success">
                                <tr>
                                    <th>Matricule</th>
                                    <th>Nom</th>
                                    <th>Prénom</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            presents.forEach(adh => {
                html += `
                    <tr>
                        <td><strong>${adh.matricule}</strong></td>
                        <td>${adh.nom}</td>
                        <td>${adh.prenom}</td>
                    </tr>
                `;
            });
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        // Colonne des absents
        if (absents.length > 0) {
            html += `
                <div class="col-md-6">
                    <h6 class="text-danger"><i class="fas fa-times-circle"></i> Absents (${absents.length})</h6>
                    <div class="table-responsive">
                        <table class="table table-sm table-bordered">
                            <thead class="table-danger">
                                <tr>
                                    <th>Matricule</th>
                                    <th>Nom</th>
                                    <th>Prénom</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            absents.forEach(adh => {
                html += `
                    <tr>
                        <td><strong>${adh.matricule}</strong></td>
                        <td>${adh.nom}</td>
                        <td>${adh.prenom}</td>
                    </tr>
                `;
            });
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        html += `</div>`;
        $container.html(html);
    }

    // Modal popup pour voir les adhérents d'une date (quand on clique sur une date verte/rouge)
    function showGroupeAdherentsModal(groupe, date, heure) {
        // Créer le modal s'il n'existe pas
        if ($('#adherentsSeanceModal').length === 0) {
            const modalHtml = `
                <div class="modal fade" id="adherentsSeanceModal" tabindex="-1" aria-labelledby="adherentsSeanceModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="adherentsSeanceModalLabel">Adhérents de la séance</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body" id="adherentsSeanceModalBody">
                                <div class="text-center">
                                    <div class="spinner-border" role="status">
                                        <span class="visually-hidden">Chargement...</span>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            $('body').append(modalHtml);
        }

        // Afficher le modal avec spinner
        $('#adherentsSeanceModalBody').html(`
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                <p class="mt-2">Chargement des adhérents...</p>
            </div>
        `);
        $('#adherentsSeanceModal').modal('show');

        // Charger les données
        $.ajax({
            url: '/get_groupe_adherents_by_seance',
            method: 'GET',
            data: {
                groupe_nom: groupe,
                date_seance: date,
                heure_debut: heure
            },
            success: function(response) {
                if (response.success) {
                    displayAdherentsInModal(response);
                } else {
                    $('#adherentsSeanceModalBody').html(`
                        <div class="alert alert-warning" role="alert">
                            <i class="fas fa-exclamation-triangle"></i>
                            ${response.error || 'Erreur lors du chargement des adhérents'}
                        </div>
                    `);
                }
            },
            error: function(xhr, status, error) {
                console.error('Erreur:', error);
                $('#adherentsSeanceModalBody').html(`
                    <div class="alert alert-danger" role="alert">
                        <i class="fas fa-exclamation-circle"></i>
                        Impossible de charger les adhérents. Veuillez réessayer.
                    </div>
                `);
            }
        });
    }

    // Afficher les adhérents dans le modal popup
    function displayAdherentsInModal(data) {
        if (!data.adherents || data.adherents.length === 0) {
            $('#adherentsSeanceModalBody').html(`
                <div class="alert alert-info" role="alert">
                    <i class="fas fa-info-circle"></i>
                    Aucun adhérent trouvé pour cette séance
                </div>
            `);
            return;
        }

        const presents = data.adherents.filter(a => a.est_present === 'O');
        const absents = data.adherents.filter(a => a.est_present === 'N');

        let html = `
            <div class="mb-4">
                <h6><i class="fas fa-calendar-alt text-primary"></i> Informations de la séance</h6>
                <div class="card">
                    <div class="card-body">
                        <p class="mb-1"><strong>Groupe:</strong> ${data.seance.groupe}</p>
                        <p class="mb-1"><strong>Date:</strong> ${data.seance.date}</p>
                        <p class="mb-1"><strong>Heure:</strong> ${data.seance.heure}</p>
                        <p class="mb-1"><strong>Entraîneur:</strong> ${data.seance.entraineur}</p>
                        <hr>
                        <p class="mb-0">
                            <span class="badge bg-success">${presents.length} Présent(s)</span>
                            <span class="badge bg-danger ms-2">${absents.length} Absent(s)</span>
                            <span class="badge bg-info ms-2">${data.statistiques.total} Total</span>
                        </p>
                    </div>
                </div>
            </div>
            <div class="row">
        `;

        // Colonne des présents
        if (presents.length > 0) {
            html += `
                <div class="col-md-6">
                    <h6 class="text-success"><i class="fas fa-check-circle"></i> Présents (${presents.length})</h6>
                    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                        <table class="table table-sm table-bordered table-hover">
                            <thead class="table-success sticky-top">
                                <tr>
                                    <th>Matricule</th>
                                    <th>Nom</th>
                                    <th>Prénom</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            presents.forEach(adh => {
                html += `
                    <tr>
                        <td><strong>${adh.matricule}</strong></td>
                        <td>${adh.nom}</td>
                        <td>${adh.prenom}</td>
                    </tr>
                `;
            });
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        // Colonne des absents
        if (absents.length > 0) {
            html += `
                <div class="col-md-6">
                    <h6 class="text-danger"><i class="fas fa-times-circle"></i> Absents (${absents.length})</h6>
                    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                        <table class="table table-sm table-bordered table-hover">
                            <thead class="table-danger sticky-top">
                                <tr>
                                    <th>Matricule</th>
                                    <th>Nom</th>
                                    <th>Prénom</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            absents.forEach(adh => {
                html += `
                    <tr>
                        <td><strong>${adh.matricule}</strong></td>
                        <td>${adh.nom}</td>
                        <td>${adh.prenom}</td>
                    </tr>
                `;
            });
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        html += `</div>`;
        $('#adherentsSeanceModalBody').html(html);
    }

    function showModalError(message) {
        const tbody = $('#detailsTable tbody');
        tbody.html(`
            <tr><td colspan="7" class="text-center text-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>${message}
            </td></tr>
        `);
        $('#exportDetailsBtn').prop('disabled', true);
    }

    function exportDetailsData() {
        if (!currentDetails || currentDetails.length === 0) {
            alert('Aucune donnée à exporter');
            return;
        }
        
        try {
            const exportData = currentDetails.map(detail => ({
                'Date': detail.date,
                'Groupe': detail.groupe,
                'Entraîneur': detail.entraineur,
                'Heure début': detail.heure_debut,
                'Durée (heures)': detail.duree_heures,
                'Durée (minutes)': detail.duree_minutes,
                'État': detail.etat || 'Non marqué',
                'Adhérents présents': detail.adherents_presents || '',
                'Adhérents absents': detail.adherents_absents || ''
            }));
            
            const wb = XLSX.utils.book_new();
            const ws = XLSX.utils.json_to_sheet(exportData);
            
            const wscols = [
                { width: 15 }, { width: 20 }, { width: 25 },
                { width: 12 }, { width: 15 }, { width: 15 }, 
                { width: 15 }, { width: 15 }, { width: 15 }
            ];
            ws['!cols'] = wscols;
            
            XLSX.utils.book_append_sheet(wb, ws, 'Détails présences');
            
            const safeName = currentName.replace(/[^a-zA-Z0-9]/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '');
            const now = new Date();
            const dateStr = now.toISOString().split('T')[0];
            const fileName = `details_presences_${safeName}_${dateStr}.xlsx`;
            
            XLSX.writeFile(wb, fileName);
        } catch (error) {
            console.error('Erreur export:', error);
            alert('Erreur lors de l\'export des données. Veuillez réessayer.');
        }
    }

    function setDefaultDates() {
        const today = new Date();
        const oneMonthAgo = new Date(today);
        oneMonthAgo.setMonth(today.getMonth() - 1);

        $('#endDate').val(today.toISOString().split('T')[0]);
        $('#startDate').val(oneMonthAgo.toISOString().split('T')[0]);
    }

    return {
        init: init,
        search: performSearch,
        exportData: exportGlobalData
    };
})();

$(document).ready(function() {
    PresenceModule.init();
    
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});