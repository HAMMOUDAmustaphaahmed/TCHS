document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM
    const searchTypeRadios = document.querySelectorAll('input[name="searchType"]');
    const searchContainers = document.querySelectorAll('.search-container');
    const adherentSearchInput = document.getElementById('adherentSearchInput');
    const adherentSearchResults = document.getElementById('adherentSearchResults');
    const searchButton = document.getElementById('searchButton');
    const exportButton = document.getElementById('exportExcel');
    const printButton = document.getElementById('printReport');
    const loader = document.getElementById('loader');

    // Initialisation des composants
    initializeDatePicker();
    setupEventListeners();
    setDefaultDate();

    // Initialisation du date picker
    function initializeDatePicker() {
        flatpickr("#dateFilter", {
            dateFormat: "Y-m-d",
            locale: "fr",
            defaultDate: new Date(),
            maxDate: new Date()
        });
    }

    // Définir la date du jour par défaut
    function setDefaultDate() {
        const today = new Date();
        document.getElementById('dateFilter').value = today.toISOString().split('T')[0];
    }

    // Configuration des écouteurs d'événements
    function setupEventListeners() {
        // Gestion du changement de type de recherche
        searchTypeRadios.forEach(radio => {
            radio.addEventListener('change', handleSearchTypeChange);
        });

        // Recherche d'adhérent en temps réel
        let searchTimeout;
        adherentSearchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const searchType = document.querySelector('input[name="adherentSearchType"]:checked').value;
                searchAdherents(this.value, searchType);
            }, 300);
        });

        // Bouton de recherche
        searchButton.addEventListener('click', performSearch);

        // Bouton d'export Excel
        exportButton.addEventListener('click', exportToExcel);

        // Bouton d'impression
        printButton.addEventListener('click', printResults);
    }

    // Gestion du changement de type de recherche
    function handleSearchTypeChange(event) {
        searchContainers.forEach(container => {
            container.classList.remove('active');
        });

        const selectedType = event.target.value;
        document.getElementById(`${selectedType}Search`).classList.add('active');
    }

    // Recherche d'adhérents
    async function searchAdherents(query, type) {
        if (query.length < 2) {
            adherentSearchResults.style.display = 'none';
            return;
        }
    
        try {
            const response = await fetch(`/api/search_adherent_presence?type=${type}&query=${encodeURIComponent(query)}`);
            const adherents = await response.json();
    
            displayAdherentResults(adherents);
        } catch (error) {
            console.error('Erreur lors de la recherche d\'adhérents:', error);
        }
    }

    // Affichage des résultats de recherche d'adhérents
    function displayAdherentResults(adherents) {
        adherentSearchResults.innerHTML = '';
        
        if (adherents.length === 0) {
            adherentSearchResults.style.display = 'none';
            return;
        }

        adherents.forEach(adherent => {
            const div = document.createElement('div');
            div.className = 'search-result-item';
            div.innerHTML = `${adherent.matricule} - ${adherent.nom} ${adherent.prenom}`;
            div.addEventListener('click', () => selectAdherent(adherent));
            adherentSearchResults.appendChild(div);
        });

        adherentSearchResults.style.display = 'block';
    }

    // Sélection d'un adhérent
    function selectAdherent(adherent) {
        adherentSearchInput.value = `${adherent.matricule} - ${adherent.nom} ${adherent.prenom}`;
        adherentSearchInput.dataset.matricule = adherent.matricule;
        adherentSearchResults.style.display = 'none';
    }

    // Effectuer la recherche
    async function performSearch() {
        showLoader();

        // Récupération des valeurs des filtres
        const searchType = document.querySelector('input[name="searchType"]:checked').value;
        const date = document.getElementById('dateFilter').value;
        const timeStart = document.getElementById('timeStartFilter').value;
        const timeEnd = document.getElementById('timeEndFilter').value;
        const terrain = document.getElementById('terrainFilter').value;

        // Construction des paramètres de recherche
        let params = new URLSearchParams({
            date: date,
            heure_debut: timeStart,
            heure_fin: timeEnd,
            terrain: terrain
        });

        // Ajout du critère de recherche principal
        switch (searchType) {
            case 'groupe':
                params.append('groupe', document.getElementById('groupeSelect').value);
                break;
            case 'entraineur':
                params.append('entraineur', document.getElementById('entraineurSelect').value);
                break;
            case 'adherent':
                params.append('adherent', adherentSearchInput.dataset.matricule);
                break;
        }

        try {
            const response = await fetch(`/api/presences/search?${params}`);
            const results = await response.json();
            displayResults(results);
        } catch (error) {
            console.error('Erreur lors de la recherche:', error);
            showError('Une erreur est survenue lors de la recherche');
        } finally {
            hideLoader();
        }
    }

    // Affichage des résultats
    function displayResults(results) {
        const tbody = document.getElementById('resultsBody');
        tbody.innerHTML = '';
        document.getElementById('totalResults').textContent = results.length;

        results.forEach(result => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${formatDate(result.date)}</td>
                <td>${result.heure}</td>
                <td>${result.groupe}</td>
                <td>${result.matricule}</td>
                <td>${result.adherent}</td>
                <td>${result.entraineur}</td>
                <td><span class="status-badge ${result.classe_statut}">${result.statut}</span></td>
            `;
            tbody.appendChild(row);
        });
    }

    // Export Excel
    async function exportToExcel() {
        showLoader();
        try {
            const response = await fetch('/export_presences' + window.location.search);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `presences_${formatDateFileName(new Date())}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } catch (error) {
            console.error('Erreur lors de l\'export:', error);
            showError('Une erreur est survenue lors de l\'export');
        } finally {
            hideLoader();
        }
    }

    // Impression des résultats
    function printResults() {
        window.print();
    }

    // Fonctions utilitaires
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR');
    }

    function formatDateFileName(date) {
        return date.toISOString().split('T')[0].replace(/-/g, '');
    }

    function showLoader() {
        loader.style.display = 'flex';
    }

    function hideLoader() {
        loader.style.display = 'none';
    }

    function showError(message) {
        // Création d'une notification d'erreur
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.textContent = message;
        document.body.appendChild(notification);

        // Auto-suppression après 3 secondes
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
});