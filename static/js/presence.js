// Module pattern pour éviter les conflits de variables
const PresenceModule = (function() {
    // Variables privées
    let currentSearchType = null;
    let searchResults = [];
    let currentAdherentDetails = null;
    let currentAdherentName = '';
    
    const API_BASE_URL = '/api'; // Ajustez selon la config Flask

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
            alert('Veuillez sélectionner un type de recherche');
            return;
        }

        const startDate = $('#startDate').val();
        const endDate = $('#endDate').val();
        const searchTerm = $('#searchToggle').is(':checked') ? $('#searchInput').val() : '';

        if (!startDate || !endDate) {
            alert('Veuillez sélectionner les dates de début et fin');
            return;
        }

        performSearch(startDate, endDate, searchTerm);
    }

    // Exécution de la recherche
    function performSearch(startDate, endDate, searchTerm) {
        $('#loadingSpinner').show();
        $('#resultsContent').empty();
        $('#resultsSection').addClass('visible');

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
                displayResults(response.data || []);
                $('#loadingSpinner').hide();
                $('#exportBtn').prop('disabled', false);
            },
            error: function(xhr, status, error) {
                console.error('Erreur lors de la recherche:', error);
                showError('Erreur serveur. Veuillez réessayer plus tard.');
                $('#loadingSpinner').hide();
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
                    <thead>
                        <tr>
        `;

        if (currentSearchType === 'adherent') {
            tableHtml += `
                <th>Matricule</th>
                <th>Nom</th>
                <th>Prénom</th>
                <th>Présences</th>
                <th>Actions</th>
            `;
        } else if (currentSearchType === 'entraineur') {
            tableHtml += `
                <th>Nom</th>
                <th>Présences</th>
            `;
        } else if (currentSearchType === 'groupe') {
            tableHtml += `
                <th>Nom du Groupe</th>
                <th>Présences</th>
            `;
        }

        tableHtml += `
                        </tr>
                    </thead>
                    <tbody>
        `;

        data.forEach(item => {
            let presentCount = 0;
            let absentCount = 0;
            let attendanceHtml = '';

            if (item.sessions && item.sessions.length > 0) {
                item.sessions.forEach(session => {
                    const isPresent = (session.est_present && session.est_present === 'O');
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
                             title="${session.date_seance} - ${isPresent ? 'Présent' : 'Absent'}">
                            ${day}/${month}
                        </div>
                    `;
                });
            }

            tableHtml += '<tr>';

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

            tableHtml += `
                <td>
  <div class="stats-summary">
    <div class="stat-card present">
      <div class="stat-number">${presentCount}</div>
      <div class="stat-label">Présent(e)</div>
    </div>
    <div class="stat-card absent">
      <div class="stat-number">${absentCount}</div>
      <div class="stat-label">Absent(e)</div>
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

            // Ajouter le bouton "Voir détails" seulement pour les adhérents
            if (currentSearchType === 'adherent') {
                tableHtml += `
                    <td>
                        <button class="btn btn-sm btn-outline-primary view-details-btn" 
                                data-matricule="${item.matricule}" 
                                data-nom="${item.nom}" 
                                data-prenom="${item.prenom}">
                            <i class="fas fa-eye"></i> Voir détails
                        </button>
                    </td>
                `;
            } else {
                tableHtml += '<td></td>';
            }

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
    }

    // Affichage des erreurs
    function showError(message) {
        $('#resultsContent').html(`
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                ${message}
            </div>
        `);
    }

    // Export des données globales
    function exportGlobalData() {
        if (searchResults.length === 0) return;

        const params = new URLSearchParams({
            type: currentSearchType,
            start_date: $('#startDate').val(),
            end_date: $('#endDate').val(),
            search_term: $('#searchToggle').is(':checked') ? $('#searchInput').val() : ''
        });

        window.open(`${API_BASE_URL}/presences/export?${params.toString()}`, '_blank');
    }

    // Affichage des détails d'un adhérent
    function showAdherentDetails(matricule, nom, prenom) {
        $('#loadingSpinner').show();
        currentAdherentName = `${nom} ${prenom}`;
        currentAdherentDetails = [];
        
        $.ajax({
            url: `/api/presences/adherent/${matricule}/details`,
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    currentAdherentDetails = response.details;
                    displayAdherentDetails(response.details);
                    $('#adherentName').text(`Détails des présences de ${currentAdherentName}`);
                    $('#detailsModal').modal('show');
                } else {
                    alert('Erreur lors du chargement des détails: ' + response.error);
                }
                $('#loadingSpinner').hide();
            },
            error: function() {
                alert('Erreur lors du chargement des détails');
                $('#loadingSpinner').hide();
            }
        });
    }

    // Affichage des détails dans le modal
    function displayAdherentDetails(details) {
        const tbody = $('#detailsTable tbody');
        tbody.empty();
        
        if (details.length === 0) {
            tbody.append('<tr><td colspan="5" class="text-center">Aucune donnée de présence trouvée</td></tr>');
            return;
        }
        
        details.forEach(detail => {
            const row = `
                <tr>
                    <td>${detail.date}</td>
                    <td>${detail.groupe || 'N/A'}</td>
                    <td>${detail.entraineur || 'N/A'}</td>
                    <td>${detail.heure_debut}</td>
                    <td><span class="badge ${detail.etat === 'Présent(e)' ? 'bg-success' : 'bg-danger'}">${detail.etat}</span></td>
                </tr>
            `;
            tbody.append(row);
        });
    }

    // Export des données détaillées
    function exportDetailsData() {
        if (!currentAdherentDetails || currentAdherentDetails.length === 0) {
            alert('Aucune donnée à exporter');
            return;
        }
        
        // Créer un workbook et une worksheet
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.json_to_sheet(currentAdherentDetails);
        
        // Ajouter la worksheet au workbook
        XLSX.utils.book_append_sheet(wb, ws, 'Détails présences');
        
        // Générer le fichier XLSX et le télécharger
        const fileName = `details_presences_${currentAdherentName.replace(/\s+/g, '_')}.xlsx`;
        XLSX.writeFile(wb, fileName);
    }

    // Définition des dates par défaut
    function setDefaultDates() {
        const today = new Date();
        const oneMonthAgo = new Date(today);
        oneMonthAgo.setMonth(today.getMonth() - 1);

        $('#endDate').val(today.toISOString().split('T')[0]);
        $('#startDate').val(oneMonthAgo.toISOString().split('T')[0]);
    }

    // Retourner les méthodes publiques
    return {
        init: init
    };
})();

// Initialisation du module lorsque le document est prêt
$(document).ready(function() {
    PresenceModule.init();
});