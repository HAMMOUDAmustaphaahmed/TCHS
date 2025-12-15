// Module pattern pour éviter les conflits de variables - VERSION AVEC DURÉE
const PresenceModule = (function() {
    // Variables privées
    let currentSearchType = null;
    let searchResults = [];
    let currentAdherentDetails = null;
    let currentAdherentName = '';
    
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

        // Validation des dates
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

    // Affichage des résultats - VERSION CORRIGÉE
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
                    <thead>
                        <tr>
        `;

        // En-têtes selon le type
        if (currentSearchType === 'adherent') {
            tableHtml += `
                <th>Matricule</th>
                <th>Nom</th>
                <th>Prénom</th>
                <th>Statistiques & Présences</th>
                <th>Actions</th>
            `;
        } else if (currentSearchType === 'entraineur') {
            tableHtml += `
                <th>Nom Entraîneur</th>
                <th>Statistiques & Présences</th>
                <th>Actions</th>
            `;
        } else if (currentSearchType === 'groupe') {
            tableHtml += `
                <th>Nom du Groupe</th>
                <th>Statistiques & Présences</th>
                <th>Actions</th>
            `;
        }

        tableHtml += `
                        </tr>
                    </thead>
                    <tbody>
        `;

        // Génération des lignes
        data.forEach(item => {
            let presentCount = 0;
            let absentCount = 0;
            let attendanceHtml = '';

            if (item.sessions && item.sessions.length > 0) {
                item.sessions.forEach(session => {
                    const isPresent = (session.est_present === 'O');
                    if (isPresent) {
                        presentCount++;
                    } else {
                        absentCount++;
                    }

                    const date = new Date(session.date_seance);
                    const day = date.getDate();
                    const month = date.getMonth() + 1;

                    attendanceHtml += `
                        <div class="attendance-day ${isPresent ? 'present' : 'absent'}" 
                             title="${formatDateForDisplay(session.date_seance)} - ${session.heure_debut} - ${isPresent ? 'Présent' : 'Absent'}
${session.groupe_nom ? 'Groupe: ' + session.groupe_nom : ''}
${session.entraineur_nom ? 'Entraîneur: ' + session.entraineur_nom : ''}">
                            ${day}/${month}
                        </div>
                    `;
                });
            }

            tableHtml += '<tr>';

            // Colonnes spécifiques selon le type
            if (currentSearchType === 'adherent') {
                tableHtml += `
                    <td><strong>${item.matricule || 'N/A'}</strong></td>
                    <td><strong>${item.nom || 'N/A'}</strong></td>
                    <td>${item.prenom || 'N/A'}</td>
                `;
            } else if (currentSearchType === 'entraineur') {
                tableHtml += `
                    <td><strong>${item.nom || 'N/A'}</strong></td>
                `;
            } else if (currentSearchType === 'groupe') {
                tableHtml += `
                    <td><strong>${item.nom || 'N/A'}</strong></td>
                `;
            }

            // Colonne des statistiques et présences
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
                    </div>
                    <div class="attendance-grid">
                        ${attendanceHtml}
                    </div>
                </td>
            `;

            // Colonne actions
            tableHtml += '<td>';
            if (currentSearchType === 'adherent') {
                tableHtml += `
                    <button class="btn btn-sm btn-outline-primary view-details-btn" 
                            data-matricule="${item.matricule}" 
                            data-nom="${item.nom}" 
                            data-prenom="${item.prenom}">
                        <i class="fas fa-eye"></i> Voir détails
                    </button>
                `;
            } else if (currentSearchType === 'entraineur') {
                tableHtml += `
                    <button class="btn btn-sm btn-outline-primary view-details-btn-entraineur" 
                            data-nom="${item.nom}">
                        <i class="fas fa-eye"></i> Voir détails
                    </button>
                `;
            }
            tableHtml += '</td>';

            tableHtml += '</tr>';
        });

        tableHtml += `
                    </tbody>
                </table>
            </div>
        `;

        $('#resultsContent').html(tableHtml);
        
        // Ajouter les gestionnaires d'événements pour les boutons "Voir détails"
        $('.view-details-btn').on('click', function() {
            const matricule = $(this).data('matricule');
            const nom = $(this).data('nom');
            const prenom = $(this).data('prenom');
            showAdherentDetails(matricule, nom, prenom);
        });

        $('.view-details-btn-entraineur').on('click', function() {
            const nom = $(this).data('nom');
            showEntraineurDetails(nom);
        });
    }

    // Fonction utilitaire pour formater les dates
    function formatDateForDisplay(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR');
    }

    // Affichage des erreurs amélioré
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

    // Export des données globales
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

        // Créer un lien temporaire pour le téléchargement
        const downloadUrl = `${API_BASE_URL}/presences/export?${params.toString()}`;
        window.open(downloadUrl, '_blank');
    }

    // Affichage des détails d'un adhérent - AVEC DURÉE
    function showAdherentDetails(matricule, nom, prenom) {
        currentAdherentName = `${nom} ${prenom}`;
        currentAdherentDetails = [];
        
        // Afficher le modal avec un spinner de chargement
        $('#adherentName').text(`Chargement des détails de ${currentAdherentName}...`);
        $('#detailsTable tbody').html(`
            <tr>
                <td colspan="6" class="text-center">
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="visually-hidden">Chargement...</span>
                    </div>
                    Chargement des données...
                </td>
            </tr>
        `);
        
        // Mettre à jour l'en-tête du tableau avec la colonne Durée
        $('#detailsTable thead tr').html(`
            <th>Date</th>
            <th>Groupe</th>
            <th>Entraîneur</th>
            <th>Heure début</th>
            <th>Durée</th>
            <th>État</th>
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
                currentAdherentDetails = response.presences;
                displayDetailsWithDuration(response.presences, response.total_heures);
                $('#adherentName').text(`Détails des présences de ${response.nom}`);
            },
            error: function(xhr, status, error) {
                console.error('Erreur lors du chargement des détails:', error);
                showModalError('Impossible de charger les détails. Veuillez réessayer.');
            }
        });
    }

    // Affichage des détails d'un entraîneur - NOUVEAU AVEC DURÉE
    function showEntraineurDetails(nomEntraineur) {
        currentAdherentName = nomEntraineur;
        currentAdherentDetails = [];
        
        // Afficher le modal avec un spinner de chargement
        $('#adherentName').text(`Chargement des détails de ${nomEntraineur}...`);
        $('#detailsTable tbody').html(`
            <tr>
                <td colspan="6" class="text-center">
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="visually-hidden">Chargement...</span>
                    </div>
                    Chargement des données...
                </td>
            </tr>
        `);
        
        // Mettre à jour l'en-tête du tableau avec la colonne Durée
        $('#detailsTable thead tr').html(`
            <th>Date</th>
            <th>Groupe</th>
            <th>Entraîneur</th>
            <th>Heure début</th>
            <th>Durée</th>
            <th>État</th>
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
                currentAdherentDetails = response.presences;
                displayDetailsWithDuration(response.presences, response.total_heures);
                $('#adherentName').text(`Détails des présences de ${response.nom}`);
            },
            error: function(xhr, status, error) {
                console.error('Erreur lors du chargement des détails:', error);
                showModalError('Impossible de charger les détails. Veuillez réessayer.');
            }
        });
    }

    // Affichage des détails avec durée - NOUVELLE FONCTION
    function displayDetailsWithDuration(details, totalHeures) {
        const tbody = $('#detailsTable tbody');
        tbody.empty();
        
        if (!details || details.length === 0) {
            tbody.append(`
                <tr>
                    <td colspan="6" class="text-center text-muted">
                        <i class="fas fa-info-circle me-2"></i>
                        Aucune donnée de présence trouvée pour cette période
                    </td>
                </tr>
            `);
            $('#exportDetailsBtn').prop('disabled', true);
            return;
        }
        
        $('#exportDetailsBtn').prop('disabled', false);
        
        details.forEach((detail, index) => {
            const row = `
                <tr class="${index % 2 === 0 ? 'table-light' : ''}">
                    <td>${detail.date || 'N/A'}</td>
                    <td>${detail.groupe || 'N/A'}</td>
                    <td>${detail.entraineur || 'N/A'}</td>
                    <td>${detail.heure_debut || 'N/A'}</td>
                    <td><strong>${detail.duree_heures}h</strong> (${detail.duree_minutes}min)</td>
                    <td>
                        <span class="badge ${detail.etat === 'Présent' ? 'bg-success' : 'bg-danger'}">
                            ${detail.etat || 'N/A'}
                        </span>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
        
        // Ajouter la ligne de total
        tbody.append(`
            <tr class="table-info">
                <td colspan="4" class="text-end"><strong>Durée totale :</strong></td>
                <td colspan="2"><strong>${totalHeures} heures</strong></td>
            </tr>
        `);
    }

    // Affichage des erreurs dans le modal
    function showModalError(message) {
        const tbody = $('#detailsTable tbody');
        tbody.html(`
            <tr>
                <td colspan="6" class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${message}
                </td>
            </tr>
        `);
        $('#exportDetailsBtn').prop('disabled', true);
    }

    // Export des données détaillées - VERSION AVEC DURÉE
    function exportDetailsData() {
        if (!currentAdherentDetails || currentAdherentDetails.length === 0) {
            alert('Aucune donnée à exporter');
            return;
        }
        
        try {
            // Préparer les données pour l'export
            const exportData = currentAdherentDetails.map(detail => ({
                'Date': detail.date,
                'Groupe': detail.groupe,
                'Entraîneur': detail.entraineur,
                'Heure début': detail.heure_debut,
                'Durée (heures)': detail.duree_heures,
                'Durée (minutes)': detail.duree_minutes,
                'État': detail.etat
            }));
            
            // Créer un workbook et une worksheet
            const wb = XLSX.utils.book_new();
            const ws = XLSX.utils.json_to_sheet(exportData);
            
            // Ajuster la largeur des colonnes
            const wscols = [
                { width: 15 }, // Date
                { width: 20 }, // Groupe
                { width: 25 }, // Entraîneur
                { width: 12 }, // Heure début
                { width: 15 }, // Durée (heures)
                { width: 15 }, // Durée (minutes)
                { width: 15 }  // État
            ];
            ws['!cols'] = wscols;
            
            // Ajouter la worksheet au workbook
            XLSX.utils.book_append_sheet(wb, ws, 'Détails présences');
            
            // Générer le nom de fichier
            const safeAdherentName = currentAdherentName
                .replace(/[^a-zA-Z0-9]/g, '_')
                .replace(/_+/g, '_')
                .replace(/^_|_$/g, '');
            
            const now = new Date();
            const dateStr = now.toISOString().split('T')[0];
            const fileName = `details_presences_${safeAdherentName}_${dateStr}.xlsx`;
            
            // Télécharger le fichier
            XLSX.writeFile(wb, fileName);
            
        } catch (error) {
            console.error('Erreur lors de l\'export:', error);
            alert('Erreur lors de l\'export des données. Veuillez réessayer.');
        }
    }

    // Définition des dates par défaut
    function setDefaultDates() {
        const today = new Date();
        const oneMonthAgo = new Date(today);
        oneMonthAgo.setMonth(today.getMonth() - 1);

        $('#endDate').val(today.toISOString().split('T')[0]);
        $('#startDate').val(oneMonthAgo.toISOString().split('T')[0]);
    }

    // Fonction utilitaire pour valider les dates
    function validateDates(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const today = new Date();
        
        if (start > end) {
            return 'La date de début doit être antérieure à la date de fin';
        }
        
        if (start > today) {
            return 'La date de début ne peut pas être dans le futur';
        }
        
        // Vérifier que la période ne dépasse pas 1 an
        const oneYearAgo = new Date(today);
        oneYearAgo.setFullYear(today.getFullYear() - 1);
        
        if (start < oneYearAgo) {
            return 'La période de recherche ne peut pas dépasser 1 an';
        }
        
        return null; // Pas d'erreur
    }

    // Fonctions utilitaires pour améliorer l'UX
    function showLoading(show = true) {
        if (show) {
            $('#loadingSpinner').show();
            $('#searchBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Recherche...');
        } else {
            $('#loadingSpinner').hide();
            $('#searchBtn').prop('disabled', false).html('<i class="fas fa-search"></i> Rechercher');
        }
    }

    // Retourner les méthodes publiques
    return {
        init: init,
        // Exposer certaines fonctions pour les tests ou usage externe
        search: performSearch,
        exportData: exportGlobalData,
        validateDates: validateDates
    };
})();

// Initialisation du module lorsque le document est prêt
$(document).ready(function() {
    PresenceModule.init();
    
    // Ajouter des tooltips Bootstrap si disponible
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});