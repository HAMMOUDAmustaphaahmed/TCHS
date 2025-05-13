document.addEventListener('DOMContentLoaded', function() {
    const searchTypeRadios = document.querySelectorAll('input[name="searchType"]');
    const searchContainers = document.querySelectorAll('.search-container');
    const adherentSearchInput = document.getElementById('adherentSearchInput');
    const adherentSearchResults = document.getElementById('adherentSearchResults');
    const entraineurSearchInput = document.getElementById('entraineurSearchInput');
    const entraineurSearchResults = document.getElementById('entraineurSearchResults');
    const searchButton = document.getElementById('searchButton');
    const exportButton = document.getElementById('exportExcel');
    const printButton = document.getElementById('printReport');
    const loader = document.getElementById('loader');
    setupEventListeners();

    function setupEventListeners() {
        searchTypeRadios.forEach(radio => {
            radio.addEventListener('change', handleSearchTypeChange);
        });

        adherentSearchInput.addEventListener('input', () => {
            searchEntities(adherentSearchInput.value, 'adherent', adherentSearchResults, selectAdherent);
        });

        entraineurSearchInput.addEventListener('input', () => {
            searchEntities(entraineurSearchInput.value, 'entraineur', entraineurSearchResults, selectEntraineur);
        });

        searchButton.addEventListener('click', performSearch);
        exportButton.addEventListener('click', exportToExcel);
        printButton.addEventListener('click', () => window.print());
    }

    function handleSearchTypeChange(event) {
        searchContainers.forEach(container => container.classList.remove('active'));
        document.getElementById(`${event.target.value}Search`).classList.add('active');
    }

    async function searchEntities(query, type, resultsContainer, selectCallback) {
        if (query.length < 2) {
            resultsContainer.style.display = 'none';
            return;
        }

        try {
            const response = await fetch(`/api/search_adherent_presence?type=${type}&query=${encodeURIComponent(query)}`);
            const results = await response.json();

            resultsContainer.innerHTML = '';
            results.forEach(entity => {
                const div = document.createElement('div');
                div.className = 'search-result-item';
                div.textContent = `${entity.matricule || ''} ${entity.nom} ${entity.prenom}`;
                div.addEventListener('click', () => selectCallback(entity));
                resultsContainer.appendChild(div);
            });

            resultsContainer.style.display = 'block';
        } catch (error) {
            console.error(`Error during ${type} search:`, error);
        }
    }

    function selectAdherent(adherent) {
        adherentSearchInput.value = `${adherent.matricule} - ${adherent.nom} ${adherent.prenom}`;
        adherentSearchInput.dataset.matricule = adherent.matricule;
        adherentSearchResults.style.display = 'none';
    }

    function selectEntraineur(entraineur) {
        entraineurSearchInput.value = `${entraineur.nom} ${entraineur.prenom}`;
        entraineurSearchInput.dataset.nom = `${entraineur.nom} ${entraineur.prenom}`;
        entraineurSearchResults.style.display = 'none';
    }

    async function performSearch() {
        showLoader();
        const searchType = document.querySelector('input[name="searchType"]:checked').value;
        const params = new URLSearchParams({
            date: document.getElementById('dateFilter').value,
            heure_debut: document.getElementById('timeStartFilter').value,
            heure_fin: document.getElementById('timeEndFilter').value,
            terrain: document.getElementById('terrainFilter').value
        });

        if (searchType === 'groupe') {
            params.append('groupe', document.getElementById('groupeSelect').value);
        } else if (searchType === 'adherent') {
            params.append('adherent', adherentSearchInput.dataset.matricule);
        } else if (searchType === 'entraineur') {
            params.append('entraineur', entraineurSearchInput.dataset.nom);
        }

        try {
            const response = await fetch(`/api/presences/search?${params}`);
            const results = await response.json();
            displayResults(results);
        } catch (error) {
            console.error('Error during the search:', error);
        } finally {
            hideLoader();
        }
    }

    function displayResults(results) {
        const tbody = document.getElementById('resultsBody');
        tbody.innerHTML = '';
        document.getElementById('totalResults').textContent = results.length;

        results.forEach(result => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${result.date}</td>
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

    async function exportToExcel() {
        showLoader();
        try {
            const response = await fetch('/export_presences' + window.location.search);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `presences_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } catch (error) {
            console.error('Error during export:', error);
        } finally {
            hideLoader();
        }
    }

    function showLoader() {
        loader.style.display = 'flex';
    }

    function hideLoader() {
        loader.style.display = 'none';
    }
});