// situation-paiement.js
class SituationPaiement {
    constructor() {
        this.initializeDatePickers();
        this.setupEventListeners();
        this.currentPage = 1;
        this.itemsPerPage = 10;
        
        
        
    }

    

    initializeDatePickers() {
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);

        flatpickr("#date-start", {
            locale: "fr",
            dateFormat: "Y-m-d",
            defaultDate: firstDay,
            maxDate: today
        });

        flatpickr("#date-end", {
            locale: "fr",
            dateFormat: "Y-m-d",
            defaultDate: today,
            maxDate: today
        });
    }

    setupEventListeners() {
        document.getElementById('refresh-data')?.addEventListener('click', () => this.loadData());
        document.getElementById('search-transactions')?.addEventListener('input', debounce(() => this.loadTransactions(), 300));
        document.getElementById('per-page')?.addEventListener('change', (e) => {
            this.itemsPerPage = parseInt(e.target.value);
            this.currentPage = 1;
            this.loadTransactions();
        });
    }

    async loadData() {
        try {
            await Promise.all([
                this.loadSummary(),
                this.loadTransactions()
            ]);
        } catch (error) {
            console.error('Error loading data:', error);
        }
    }

    async loadSummary() {
        try {
            const startDate = document.getElementById('date-start')?.value || '';
            const endDate = document.getElementById('date-end')?.value || '';

            const response = await fetch(`/api/situation-paiement/summary?start_date=${startDate}&end_date=${endDate}`);
            const data = await response.json();

            if (!response.ok) throw new Error(data.error || 'Erreur lors du chargement');

            this.updateSummaryCards(data.summary);
            
            
        } catch (error) {
            console.error('Error loading summary:', error);
            alert('Erreur lors du chargement du résumé');
        }
    }

    

    updateSummaryCards(summary) {
        if (!summary) return;
        
        document.getElementById('total-a-payer').textContent = `${summary.total_a_payer.toLocaleString()} €`;
        document.getElementById('total-paye').textContent = `${summary.total_paye.toLocaleString()} €`;
        document.getElementById('total-remise').textContent = `${summary.total_remise.toLocaleString()} €`;
        document.getElementById('reste-a-payer').textContent = `${summary.reste_a_payer.toLocaleString()} €`;
    }

    exportToExcel() {
        try {
            const startDate = document.getElementById('date-start')?.value || '';
            const endDate = document.getElementById('date-end')?.value || '';
            
            const fileName = `situation_paiement_${startDate}_${endDate}.xlsx`;
            
            const rows = [
                [
                    'Date', 'Matricule', 'Montant', 'Payé', 'Reste',
                    'Type règlement', 'Banque', 'N° Chèque',
                     'N° Bon', 'N° Carnet'
                ]
            ];

            const transactions = document.querySelectorAll('#transactions-body tr');
            if (transactions.length === 0) {
                alert('Aucune donnée à exporter');
                return;
            }

            transactions.forEach(row => {
                const rowData = Array.from(row.cells).map(cell => cell.textContent.trim());
                rows.push(rowData);
            });

            const wb = XLSX.utils.book_new();
            const ws = XLSX.utils.aoa_to_sheet(rows);

            XLSX.utils.book_append_sheet(wb, ws, 'Transactions');
            XLSX.writeFile(wb, fileName);
        } catch (error) {
            console.error('Error exporting to Excel:', error);
            alert('Erreur lors de l\'exportation vers Excel');
        }
    }

    printTable() {
        try {
            const printContent = `
                <html>
                    <head>
                        <title>Situation Paiement</title>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                padding: 20px;
                            }
                            .print-header {
                                text-align: center;
                                margin-bottom: 20px;
                            }
                            .print-header h1 {
                                margin: 0;
                                color: #2c3e50;
                            }
                            .print-header p {
                                margin: 5px 0;
                                color: #666;
                            }
                            table {
                                width: 100%;
                                border-collapse: collapse;
                                margin-top: 20px;
                            }
                            th, td {
                                padding: 8px;
                                border: 1px solid #ddd;
                                font-size: 12px;
                            }
                            th {
                                background: #f8f9fa;
                                font-weight: bold;
                            }
                            .summary {
                                margin-top: 20px;
                                padding: 10px;
                                background: #f8f9fa;
                            }
                            .summary p {
                                margin: 5px 0;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="print-header">
                            <h1>Situation Paiement</h1>
                            <p>Période: ${document.getElementById('date-start')?.value || ''} - ${document.getElementById('date-end')?.value || ''}</p>
                            <p>Date d'impression: ${new Date().toLocaleString()}</p>
                        </div>
                        <div class="summary">
                            <p>Total à payer: ${document.getElementById('total-a-payer')?.textContent || ''}</p>
                            <p>Total payé: ${document.getElementById('total-paye')?.textContent || ''}</p>
                            <p>Total remises: ${document.getElementById('total-remise')?.textContent || ''}</p>
                            <p>Reste à payer: ${document.getElementById('reste-a-payer')?.textContent || ''}</p>
                        </div>
                        ${document.querySelector('.transactions-table')?.outerHTML || ''}
                    </body>
                </html>
            `;

            const printWindow = window.open('', '_blank');
            if (!printWindow) {
                alert('Veuillez autoriser les popups pour l\'impression');
                return;
            }
            
            printWindow.document.write(printContent);
            printWindow.document.close();

            printWindow.onload = function() {
                printWindow.print();
                printWindow.close();
            };
        } catch (error) {
            console.error('Error printing:', error);
            alert('Erreur lors de l\'impression');
        }
    }

    async loadTransactions() {
        try {
            const startDate = document.getElementById('date-start')?.value || '';
            const endDate = document.getElementById('date-end')?.value || '';
            const searchTerm = document.getElementById('search-transactions')?.value || '';

            const response = await fetch(
                `/api/situation-paiement/transactions?` +
                `page=${this.currentPage}&` +
                `per_page=${this.itemsPerPage}&` +
                `start_date=${startDate}&` +
                `end_date=${endDate}&` +
                `search=${searchTerm}`
            );

            const data = await response.json();

            if (!response.ok) throw new Error(data.error || 'Erreur lors du chargement');

            this.updateTransactionsTable(data.transactions);
            this.updatePagination(data.current_page, data.pages);
        } catch (error) {
            console.error('Error loading transactions:', error);
            alert('Erreur lors du chargement des transactions');
        }
    }

    updateTransactionsTable(transactions) {
        const tbody = document.getElementById('transactions-body');
        if (!tbody || !transactions) return;

        tbody.innerHTML = transactions.map(t => {
            const remiseDisplay = t.is_first_payment ? 
                `${t.remise}% (${t.montant_remise.toLocaleString()} €)` : 
                '-';
            
            return `
                <tr class="${t.is_first_payment ? 'first-payment' : ''}">
                    <td>${new Date(t.date).toLocaleString()}</td>
                    <td>${t.matricule}</td>
                    <td>${t.montant.toLocaleString()} €</td>
                    <td>${t.montant_paye.toLocaleString()} €</td>
                    <td>${t.montant_reste.toLocaleString()} €</td>
                    <td>${t.type_reglement || '-'}</td>
                    <td>${t.banque || '-'}</td>
                    <td>${t.numero_cheque || '-'}</td>
                    
                    <td>${t.numero_bon}</td>
                    <td>${t.numero_carnet}</td>
                </tr>
            `;
        }).join('');
    }

    updatePagination(currentPage, totalPages) {
        const pagination = document.getElementById('pagination');
        if (!pagination) return;

        let buttons = '';

        buttons += `
            <button ${currentPage === 1 ? 'disabled' : ''} 
                    onclick="window.situationPaiement.changePage(${currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;

        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                buttons += `
                    <button class="${i === currentPage ? 'active' : ''}"
                            onclick="window.situationPaiement.changePage(${i})">
                        ${i}
                    </button>
                `;
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                buttons += '<button disabled>...</button>';
            }
        }

        buttons += `
            <button ${currentPage === totalPages ? 'disabled' : ''} 
                    onclick="window.situationPaiement.changePage(${currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;

        pagination.innerHTML = buttons;
    }

    changePage(page) {
        this.currentPage = page;
        this.loadTransactions();
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

document.addEventListener('DOMContentLoaded', () => {
    window.situationPaiement = new SituationPaiement();
});