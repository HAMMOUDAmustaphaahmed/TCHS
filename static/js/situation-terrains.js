class SituationTerrains {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.charts = {};
        
        this.initializeDatePickers();
        this.setupEventListeners();
        this.initializeCharts();
        this.initializeStatsPickers();
        this.loadStatistics(); // Chargement initial des statistiques
        this.initializeTerrainSelect();  
        this.addExportButtons();  // Déplacé à l'intérieur du constructeur

        // Chargement initial des données
        this.checkAvailability();
        this.loadStatistics();
        this.setupOccupationNavigation();
    }

    initializeTerrainSelect() {
        const select = document.getElementById('terrain-select');
        // Vider d'abord le select sauf la première option
        while (select.options.length > 1) {
            select.remove(1);
        }
        
        // Ajouter les options pour les 9 terrains
        for (let i = 1; i <= 9; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = `Terrain ${i}`;
            select.appendChild(option);
        }
    }

    initializeDatePickers() {
        // Configuration de base pour Flatpickr
        const defaultConfig = {
            locale: 'fr',
            dateFormat: 'Y-m-d',
            altFormat: 'd-m-Y',
            altInput: true,
            disableMobile: true,
            allowInput: true,
            enableTime: false,
            time_24hr: true,
            // Désactiver la conversion automatique des fuseaux horaires
            formatDate: (date) => {
                const d = new Date(date);
                const year = d.getFullYear();
                const month = String(d.getMonth() + 1).padStart(2, '0');
                const day = String(d.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`;
            }
        };
    
        // Date picker pour la vérification
        this.datePicker = flatpickr("#date-check", {
            ...defaultConfig,
            defaultDate: 'today',
            onChange: (selectedDates, dateStr, instance) => {
                if (selectedDates[0]) {
                    const d = selectedDates[0];
                    const formattedDisplay = `${String(d.getDate()).padStart(2, '0')}-${String(d.getMonth() + 1).padStart(2, '0')}-${d.getFullYear()}`;
                    instance.altInput.value = formattedDisplay;
                }
            }
        });
    
        // Time pickers
        this.heureDebutPicker = flatpickr("#heure-debut", {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true,
            minuteIncrement: 30,
            defaultHour: 8,
            defaultMinute: 0
        });
    
        this.heureFinPicker = flatpickr("#heure-fin", {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true,
            minuteIncrement: 30,
            defaultHour: 9,
            defaultMinute: 30
        });
    
        // Date range pour l'historique avec le même format
        this.historyDateStart = flatpickr("#history-date-start", {
            ...defaultConfig,
            defaultDate: new Date().setDate(new Date().getDate() - 30)
        });
    
        this.historyDateEnd = flatpickr("#history-date-end", {
            ...defaultConfig,
            defaultDate: 'today'
        });
    }
    
    async checkAvailability() {
        try {
            const selectedDate = this.datePicker.selectedDates[0];
            const heureDebut = this.heureDebutPicker.selectedDates[0];
            const heureFin = this.heureFinPicker.selectedDates[0];
    
            if (!selectedDate || !heureDebut) {
                this.showError("Veuillez sélectionner une date et une heure de début");
                return;
            }
    
            // Création d'une nouvelle date sans décalage horaire
            const year = selectedDate.getFullYear();
            const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
            const day = String(selectedDate.getDate()).padStart(2, '0');
            const formattedDate = `${year}-${month}-${day}`;
    
            console.log('Date sélectionnée:', formattedDate); // Pour debug
    
            const params = new URLSearchParams({
                date: formattedDate,
                heure_debut: heureDebut.toTimeString().slice(0, 5),
                heure_fin: heureFin ? heureFin.toTimeString().slice(0, 5) : ''
            });
    
            console.log('Paramètres envoyés:', {
                date: formattedDate,
                heure_debut: heureDebut.toTimeString().slice(0, 5),
                heure_fin: heureFin ? heureFin.toTimeString().slice(0, 5) : ''
            });
    
            const response = await fetch(`/api/terrains/disponibilite?${params}`);
            if (!response.ok) throw new Error('Erreur lors de la vérification');
    
            const data = await response.json();
            this.updateCourtsDisplay(data);
    
        } catch (error) {
            this.showError("Erreur lors de la vérification de la disponibilité");
            console.error(error);
        }
    }

    setupEventListeners() {
        // Vérification de disponibilité
        document.getElementById('check-availability')?.addEventListener('click', () => this.checkAvailability());
    
        // Historique
        document.getElementById('terrain-select')?.addEventListener('change', () => this.loadHistory());
        document.getElementById('history-date-start')?.addEventListener('change', () => this.loadHistory());
        document.getElementById('history-date-end')?.addEventListener('change', () => this.loadHistory());
    
        // Export des données actuelles
        document.getElementById('export-excel')?.addEventListener('click', () => this.exportCurrentToExcel());
        document.getElementById('print-page')?.addEventListener('click', () => this.printPage());
    }
    initializeCharts() {
        // Graphique d'utilisation
        const usageCtx = document.getElementById('usage-chart').getContext('2d');
        this.charts.usage = new Chart(usageCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Séances',
                    data: [],
                    backgroundColor: 'rgba(52, 152, 219, 0.5)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 1
                }, {
                    label: 'Locations',
                    data: [],
                    backgroundColor: 'rgba(46, 204, 113, 0.5)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Graphique des revenus
        const revenueCtx = document.getElementById('revenue-chart').getContext('2d');
        this.charts.revenue = new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Revenus des locations',
                    data: [],
                    borderColor: 'rgba(46, 204, 113, 1)',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(46, 204, 113, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: value => `${value} TND`
                        }
                    }
                }
            }
        });
    }

    
    updateCourtsDisplay(data) {
        const container = document.querySelector('.courts-grid');
        container.innerHTML = '';
        const template = document.getElementById('court-template');

        data.forEach(terrain => {
            const clone = template.content.cloneNode(true);
            const card = clone.querySelector('.court-card');

            // Mise à jour du numéro et du statut
            card.querySelector('.court-number').textContent = terrain.numero;
            const badge = card.querySelector('.status-badge');
            badge.textContent = terrain.disponible ? 'Disponible' : 'Occupé';
            badge.classList.add(terrain.disponible ? 'available' : 'occupied');

            // Information d'occupation
            const occupationInfo = card.querySelector('.occupation-info');
            if (terrain.occupation) {
                occupationInfo.innerHTML = this.formatOccupationInfo(terrain.occupation);
            } else {
                occupationInfo.innerHTML = '<p class="no-occupation">Aucune occupation</p>';
            }

            // Prochaine occupation
            const nextOccupation = card.querySelector('.next-occupation');
            if (terrain.prochaine_occupation) {
                nextOccupation.innerHTML = this.formatNextOccupation(terrain.prochaine_occupation);
            }

            container.appendChild(clone);
        });
        this.setupOccupationNavigation(); // Ajouter cette ligne à la fin
    }

    formatOccupationInfo(occupations) {
        if (!Array.isArray(occupations)) {
            occupations = [occupations];
        }
    
        let currentIndex = 0;
    
        const html = `
            <div class="occupation-container">
                <div class="occupation-navigation ${occupations.length > 1 ? 'show' : 'hide'}">
                    <button class="nav-btn prev" ${currentIndex === 0 ? 'disabled' : ''}>
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <span class="occupation-counter">${currentIndex + 1}/${occupations.length}</span>
                    <button class="nav-btn next" ${currentIndex === occupations.length - 1 ? 'disabled' : ''}>
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
                <div class="occupations-slider">
                    ${occupations.map((occupation, index) => `
                        <div class="occupation-slide ${index === currentIndex ? 'active' : ''}" data-index="${index}">
                            <div class="occupation-type ${occupation.type}">
                                <i class="fas ${occupation.type === 'location' ? 'fa-money-bill' : 'fa-users'}"></i>
                                <span>${occupation.type === 'location' ? 'Location' : 'Séance'}</span>
                            </div>
                            <div class="occupation-details">
                                <p><i class="fas fa-clock"></i> ${occupation.heure_debut} - ${occupation.heure_fin}</p>
                                ${occupation.type === 'location' 
                                    ? `<p><i class="fas fa-user"></i> ${occupation.locateur}</p>`
                                    : `<p><i class="fas fa-users"></i> ${occupation.groupe}</p>
                                       <p><i class="fas fa-user-tie"></i> ${occupation.entraineur}</p>`
                                }
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    
        return html;
    }
    
    setupOccupationNavigation() {
        document.querySelectorAll('.courts-grid').forEach(court => {
            const navigation = court.querySelector('.occupation-navigation');
            if (!navigation) return;
    
            const slides = court.querySelectorAll('.occupation-slide');
            const prevBtn = navigation.querySelector('.prev');
            const nextBtn = navigation.querySelector('.next');
            const counter = navigation.querySelector('.occupation-counter');
    
            let currentIndex = 0;
    
            const updateSlides = () => {
                slides.forEach((slide, index) => {
                    slide.classList.toggle('active', index === currentIndex);
                });
                counter.textContent = `${currentIndex + 1}/${slides.length}`;
                prevBtn.disabled = currentIndex === 0;
                nextBtn.disabled = currentIndex === slides.length - 1;
            };
    
            prevBtn?.addEventListener('click', () => {
                if (currentIndex > 0) {
                    currentIndex--;
                    updateSlides();
                }
            });
    
            nextBtn?.addEventListener('click', () => {
                if (currentIndex < slides.length - 1) {
                    currentIndex++;
                    updateSlides();
                }
            });
        });
    }

    formatNextOccupation(occupation) {
        return `
            <div class="next-occupation-header">
                <i class="fas fa-clock"></i>
                <span>Prochaine occupation</span>
            </div>
            <div class="next-occupation-details">
                <p>${occupation.type === 'location' ? 'Location' : 'Séance'}</p>
                <p>${occupation.heure_debut} - ${occupation.heure_fin}</p>
            </div>
        `;
    }

    
    initializeStatsPickers() {
        const defaultConfig = {
            locale: 'fr',
            dateFormat: 'Y-m-d',
            altFormat: 'd-m-Y',
            altInput: true,
            disableMobile: true,
            allowInput: true
        };

        // Date de début par défaut : 1er janvier 2025
        this.statsDateStart = flatpickr("#stats-date-start", {
            ...defaultConfig,
            defaultDate: "2025-01-01"
        });

        // Date de fin par défaut : aujourd'hui
        this.statsDateEnd = flatpickr("#stats-date-end", {
            ...defaultConfig,
            defaultDate: 'today'
        });

        // Ajouter l'événement pour le bouton d'actualisation
        document.getElementById('update-stats')?.addEventListener('click', () => this.loadStatistics());
    }

    async loadStatistics() {
        try {
            const dateStart = this.statsDateStart.selectedDates[0];
            const dateEnd = this.statsDateEnd.selectedDates[0];

            if (!dateStart || !dateEnd) {
                this.showError("Veuillez sélectionner une période pour les statistiques");
                return;
            }

            // Afficher un indicateur de chargement
            this.showLoadingStats();

            const params = new URLSearchParams({
                start_date: dateStart.toISOString().split('T')[0],
                end_date: dateEnd.toISOString().split('T')[0]
            });

            const response = await fetch(`/api/terrains/stats?${params}`);
            if (!response.ok) throw new Error('Erreur lors du chargement des statistiques');

            const data = await response.json();
            this.updateCharts(data);

            // Masquer l'indicateur de chargement
            this.hideLoadingStats();

        } catch (error) {
            this.hideLoadingStats();
            this.showError("Erreur lors du chargement des statistiques");
            console.error(error);
        }
    }

    showLoadingStats() {
        const chartsContainer = document.querySelector('.stats-charts');
        if (!chartsContainer) return;

        const loading = document.createElement('div');
        loading.className = 'stats-loading';
        loading.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i>
            </div>
            <p>Chargement des statistiques...</p>
        `;

        chartsContainer.style.opacity = '0.5';
        chartsContainer.parentElement.appendChild(loading);
    }

    hideLoadingStats() {
        const loading = document.querySelector('.stats-loading');
        if (loading) loading.remove();

        const chartsContainer = document.querySelector('.stats-charts');
        if (chartsContainer) chartsContainer.style.opacity = '1';
    }

    updateCharts(data) {
        // Mise à jour du graphique d'utilisation
        const terrainNumbers = Object.keys(data.statistics);
        const seances = terrainNumbers.map(num => data.statistics[num].seances);
        const locations = terrainNumbers.map(num => data.statistics[num].locations);

        this.charts.usage.data.labels = terrainNumbers.map(num => `Terrain ${num}`);
        this.charts.usage.data.datasets[0].data = seances;
        this.charts.usage.data.datasets[1].data = locations;
        this.charts.usage.update();

        // Mise à jour du graphique des revenus
        const revenus = terrainNumbers.map(num => data.statistics[num].montant_total);
        this.charts.revenue.data.labels = terrainNumbers.map(num => `Terrain ${num}`);
        this.charts.revenue.data.datasets[0].data = revenus;
        this.charts.revenue.update();

        // Ajouter un timestamp de mise à jour
        this.updateStatsTimestamp();
    }

    updateStatsTimestamp() {
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'stats-timestamp';
        timestampDiv.innerHTML = `
            <small>
                Dernière mise à jour : ${new Date().toLocaleString('fr-FR')}
            </small>
        `;

        const existingTimestamp = document.querySelector('.stats-timestamp');
        if (existingTimestamp) {
            existingTimestamp.remove();
        }

        document.querySelector('.stats-container')?.appendChild(timestampDiv);
    }


    async loadHistory() {
        try {
            const terrainNum = document.getElementById('terrain-select').value;
            console.log('Selected terrain:', terrainNum);
    
            if (!terrainNum) {
                console.log('No terrain selected');
                return;
            }
    
            const dateStart = this.historyDateStart.selectedDates[0];
            const dateEnd = this.historyDateEnd.selectedDates[0];
            
            console.log('Date range:', {
                start: dateStart,
                end: dateEnd
            });
    
            if (!dateStart || !dateEnd) {
                this.showError("Veuillez sélectionner une période");
                return;
            }
    
            const params = new URLSearchParams({
                terrain: terrainNum,
                start_date: dateStart.toISOString().split('T')[0],
                end_date: dateEnd.toISOString().split('T')[0],
                page: this.currentPage,
                per_page: this.itemsPerPage
            });
    
            console.log('Fetching history with params:', params.toString());
            
            const response = await fetch(`/api/terrains/historique?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Received history data:', data);
    
            if (data.error) {
                throw new Error(data.error);
            }
    
            this.updateHistoryTable(data);
            this.updatePagination(data);
    
        } catch (error) {
            console.error('Error in loadHistory:', error);
            this.showError(`Erreur lors du chargement de l'historique: ${error.message}`);
        }
    }

    updateHistoryTable(data) {
        const tbody = document.getElementById('history-body');
        tbody.innerHTML = data.historique.map(h => `
            <tr>
                <td>${h.date}</td>
                <td>${h.heure_debut} - ${h.heure_fin}</td>
                <td>${h.type === 'location' ? 'Location' : 'Séance'}</td>
                <td>${h.utilisateur}</td>
                <td>${h.montant ? h.montant.toFixed(2) + ' TND' : '-'}</td>
            </tr>
        `).join('');
    }

    updatePagination(data) {
        const pagination = document.getElementById('history-pagination');
        pagination.innerHTML = '';

        // Bouton précédent
        const prevButton = document.createElement('button');
        prevButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevButton.disabled = this.currentPage === 1;
        prevButton.addEventListener('click', () => this.changePage(this.currentPage - 1));
        pagination.appendChild(prevButton);

        // Pages
        for (let i = 1; i <= data.pages; i++) {
            if (
                i === 1 || 
                i === data.pages || 
                (i >= this.currentPage - 2 && i <= this.currentPage + 2)
            ) {
                const pageButton = document.createElement('button');
                pageButton.textContent = i;
                pageButton.classList.toggle('active', i === this.currentPage);
                pageButton.addEventListener('click', () => this.changePage(i));
                pagination.appendChild(pageButton);
            } else if (
                i === this.currentPage - 3 || 
                i === this.currentPage + 3
            ) {
                const ellipsis = document.createElement('span');
                ellipsis.textContent = '...';
                pagination.appendChild(ellipsis);
            }
        }

        // Bouton suivant
        const nextButton = document.createElement('button');
        nextButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextButton.disabled = this.currentPage === data.pages;
        nextButton.addEventListener('click', () => this.changePage(this.currentPage + 1));
        pagination.appendChild(nextButton);
    }

    changePage(page) {
        this.currentPage = page;
        this.loadHistory();
    }

    exportCurrentToExcel() {
        const wb = XLSX.utils.book_new();
        
        // Données des terrains
        const courtsData = Array.from(document.querySelectorAll('.court-card')).map(card => {
            const number = card.querySelector('.court-number').textContent;
            const status = card.querySelector('.status-badge').textContent;
            const occupation = card.querySelector('.occupation-info').textContent;
            return { 'Terrain': number, 'Statut': status, 'Occupation': occupation };
        });
        
        const wsTerrains = XLSX.utils.json_to_sheet(courtsData);
        XLSX.utils.book_append_sheet(wb, wsTerrains, "Situation Terrains");
    
        // Générer le fichier
        const date = new Date().toISOString().split('T')[0];
        XLSX.writeFile(wb, `situation_terrains_${date}.xlsx`);
    }
    exportHistoryToExcel() {
        try {
            const content = document.querySelector('.history-table');
            if (!content) {
                this.showError("Aucun contenu à exporter");
                return;
            }
    
            const terrain = document.querySelector('#terrain-select').value;
            const dateStart = this.historyDateStart.selectedDates[0];
            const dateEnd = this.historyDateEnd.selectedDates[0];
    
            // Créer un nouveau classeur
            const wb = XLSX.utils.book_new();
    
            // Récupérer les données de l'historique
            const historyData = Array.from(document.querySelectorAll('#history-body tr')).map(row => {
                const cells = row.querySelectorAll('td');
                return {
                    'Date': cells[0].textContent,
                    'Heures': cells[1].textContent,
                    'Type': cells[2].textContent,
                    'Utilisateur': cells[3].textContent,
                    'Montant': cells[4].textContent
                };
            });
    
            // Créer une feuille avec les données
            const ws = XLSX.utils.json_to_sheet(historyData);
    
            // Ajouter un en-tête
            const headerData = [
                [`Historique du Terrain ${terrain}`],
                [`Période : du ${dateStart.toLocaleDateString()} au ${dateEnd.toLocaleDateString()}`],
                [],
            ];
            XLSX.utils.sheet_add_aoa(ws, headerData, { origin: 'A1' });
    
            // Ajouter la feuille au classeur
            XLSX.utils.book_append_sheet(wb, ws, "Historique");
    
            // Générer le fichier
            const fileName = `historique_terrain_${terrain}_${dateStart.toLocaleDateString()}_${dateEnd.toLocaleDateString()}.xlsx`;
            XLSX.writeFile(wb, fileName);
    
            this.showMessage("Export Excel réussi!", "success");
        } catch (error) {
            console.error('Erreur lors de l\'export Excel:', error);
            this.showError("Erreur lors de l'export Excel");
        }
    }

    printPage() {
        // Imprimer uniquement la situation actuelle des terrains
        const courtsContent = document.querySelector('.courts-grid');
        if (!courtsContent) {
            this.showError("Aucun contenu à imprimer");
            return;
        }
    
        const printWindow = window.open('', '_blank');
        const date = new Date().toLocaleString('fr-FR');
        
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Situation des Terrains - ${date}</title>
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            padding: 20px;
                            color: #333;
                        }
                        .print-header {
                            text-align: center;
                            margin-bottom: 30px;
                            padding-bottom: 10px;
                            border-bottom: 2px solid #333;
                        }
                        .courts-grid {
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                            gap: 20px;
                        }
                        .court-card {
                            border: 1px solid #ddd;
                            padding: 15px;
                            border-radius: 8px;
                            break-inside: avoid;
                        }
                        .court-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: 15px;
                            padding-bottom: 10px;
                            border-bottom: 1px solid #eee;
                        }
                        .status-badge {
                            padding: 5px 10px;
                            border-radius: 15px;
                            font-size: 0.9em;
                        }
                        .status-badge.available {
                            background-color: #e8f5e9;
                            color: #2e7d32;
                        }
                        .status-badge.occupied {
                            background-color: #ffebee;
                            color: #c62828;
                        }
                        .occupation-info, .next-occupation {
                            margin-top: 10px;
                        }
                        .print-footer {
                            margin-top: 30px;
                            text-align: center;
                            font-size: 0.8em;
                            color: #666;
                        }
                        @media print {
                            body { margin: 0; padding: 15px; }
                            .court-card { break-inside: avoid; page-break-inside: avoid; }
                        }
                    </style>
                </head>
                <body>
                    <div class="print-header">
                        <h2>Situation des Terrains</h2>
                        <p>Date d'impression : ${date}</p>
                    </div>
                    ${courtsContent.outerHTML}
                    <div class="print-footer">
                        <p>Document généré le ${date}</p>
                    </div>
                </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
        setTimeout(() => printWindow.close(), 1000);
    }
    
    printHistory() {
        // Imprimer uniquement l'historique
        const historyTable = document.querySelector('.history-table');
        if (!historyTable) {
            this.showError("Aucun historique à imprimer");
            return;
        }
    
        const terrain = document.querySelector('#terrain-select').value;
        const dateStart = this.historyDateStart.selectedDates[0]?.toLocaleDateString('fr-FR');
        const dateEnd = this.historyDateEnd.selectedDates[0]?.toLocaleDateString('fr-FR');
        const currentDate = new Date().toLocaleString('fr-FR');
    
        const printWindow = window.open('', '_blank');
        
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Historique des Terrains - ${currentDate}</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            padding: 20px;
                            color: #333;
                        }
                        .print-header {
                            text-align: center;
                            margin-bottom: 30px;
                        }
                        .print-subheader {
                            text-align: center;
                            margin-bottom: 20px;
                            color: #666;
                        }
                        table {
                            width: 100%;
                            border-collapse: collapse;
                            margin-bottom: 20px;
                        }
                        th, td {
                            padding: 12px;
                            text-align: left;
                            border: 1px solid #ddd;
                        }
                        th {
                            background-color: #f5f5f5;
                            font-weight: bold;
                        }
                        tr:nth-child(even) {
                            background-color: #fafafa;
                        }
                        .print-footer {
                            margin-top: 30px;
                            text-align: center;
                            font-size: 0.8em;
                            color: #666;
                            padding-top: 10px;
                            border-top: 1px solid #ddd;
                        }
                        @media print {
                            thead {
                                display: table-header-group;
                            }
                            tr {
                                page-break-inside: avoid;
                            }
                            @page {
                                margin: 1cm;
                            }
                        }
                    </style>
                </head>
                <body>
                    <div class="print-header">
                        <h2>Historique des Réservations</h2>
                    </div>
                    <div class="print-subheader">
                        <p>Terrain ${terrain}</p>
                        <p>Période : du ${dateStart} au ${dateEnd}</p>
                    </div>
                    ${historyTable.outerHTML}
                    <div class="print-footer">
                        <p>Document généré le ${currentDate}</p>
                    </div>
                </body>
            </html>
        `);
    
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
        setTimeout(() => printWindow.close(), 1000);
    }

    addExportButtons() {
        const historyContainer = document.querySelector('.history-container');
        if (!historyContainer) return;
        
        const exportButtons = `
            <div class="export-buttons">
                <button class="btn btn-success" id="export-history-excel">
                    <i class="fas fa-file-excel"></i> Exporter Excel
                </button>
                <button class="btn btn-primary" id="print-history">
                    <i class="fas fa-print"></i> Imprimer
                </button>
            </div>
        `;
        historyContainer.insertAdjacentHTML('beforeend', exportButtons);
    
        // Ajouter les événements aux boutons
        document.getElementById('export-history-excel')?.addEventListener('click', () => this.exportHistoryToExcel());
        document.getElementById('print-history')?.addEventListener('click', () => this.printHistory());
    }
    async exportToPDF() {
        try {
            const content = document.querySelector('.history-table');
            if (!content) {
                this.showError("Aucun contenu à exporter");
                return;
            }
    
            const terrain = document.querySelector('#terrain-select').value;
            const dateStart = this.historyDateStart.selectedDates[0];
            const dateEnd = this.historyDateEnd.selectedDates[0];
    
            // Créer un conteneur temporaire avec le style
            const container = document.createElement('div');
            container.innerHTML = `
                <div style="padding: 20px; font-family: Arial, sans-serif;">
                    <h2 style="text-align: center; color: #333; margin-bottom: 20px;">
                        Historique du Terrain ${terrain}
                    </h2>
                    <p style="text-align: center; color: #666; margin-bottom: 30px;">
                        Période : du ${dateStart.toLocaleDateString()} au ${dateEnd.toLocaleDateString()}
                    </p>
                    <div style="max-width: 100%;">
                        ${content.outerHTML}
                    </div>
                </div>
            `;
    
            // Appliquer les styles à la table
            const tableStyles = `
                <style>
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 20px;
                        font-size: 12px;
                    }
                    th, td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }
                    th {
                        background-color: #f4f4f4;
                        color: #333;
                    }
                    tr:nth-child(even) {
                        background-color: #f9f9f9;
                    }
                </style>
            `;
            container.insertAdjacentHTML('afterbegin', tableStyles);
    
            // Options pour html2pdf
            const opt = {
                margin: [10, 10],
                filename: `historique_terrain_${terrain}_${dateStart.toLocaleDateString()}_${dateEnd.toLocaleDateString()}.pdf`,
                image: { type: 'jpeg', quality: 1 },
                html2canvas: { 
                    scale: 2,
                    useCORS: true,
                    logging: true
                },
                jsPDF: { 
                    unit: 'mm', 
                    format: 'a4', 
                    orientation: 'landscape',
                    compress: true
                }
            };
    
            // Afficher un message de chargement
            this.showMessage("Génération du PDF en cours...", "info");
    
            // Générer le PDF
            await html2pdf().from(container).set(opt).save();
    
            // Afficher un message de succès
            this.showMessage("PDF généré avec succès!", "success");
    
        } catch (error) {
            console.error('Erreur lors de la génération du PDF:', error);
            this.showError("Erreur lors de la génération du PDF");
        }
    }
    
    // Ajouter cette nouvelle méthode pour les messages
    showMessage(message, type = 'info') {
        let notification = document.getElementById('notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            document.body.appendChild(notification);
        }
    
        // Styles pour les différents types de messages
        const styles = {
            info: {
                backgroundColor: '#3498db',
                color: 'white'
            },
            success: {
                backgroundColor: '#2ecc71',
                color: 'white'
            },
            error: {
                backgroundColor: '#e74c3c',
                color: 'white'
            }
        };
    
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 5px;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            font-family: Arial, sans-serif;
            ${Object.entries(styles[type]).map(([key, value]) => `${key}: ${value}`).join(';')}
        `;
    
        notification.textContent = message;
        notification.style.opacity = '1';
    
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    

    showError(message) {
        let notification = document.getElementById('error-notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'error-notification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: #ff4444;
                color: white;
                padding: 15px;
                border-radius: 5px;
                z-index: 1000;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            document.body.appendChild(notification);
        }

        notification.textContent = message;
        notification.style.opacity = '1';

        setTimeout(() => {
            notification.style.opacity = '0';
        }, 3000);
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    window.situationTerrains = new SituationTerrains();
});