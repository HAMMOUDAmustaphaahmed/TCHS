class TransactionManager {
    constructor() {
        this.transactions = [];
        this.modal = document.getElementById('transaction-modal');
        this.form = document.getElementById('transaction-form');
        this.currentTransactionType = '';
        
        this.initializeEventListeners();
        this.loadTransactions();
    }

    initializeEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        document.querySelector('.close-modal').addEventListener('click', () => {
            this.modal.style.display = 'none';
        });

        document.getElementById('category-filter').addEventListener('change', () => this.loadTransactions());
        document.getElementById('type-filter').addEventListener('change', () => this.loadTransactions());
        document.getElementById('date-filter').addEventListener('change', () => this.loadTransactions());

        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.modal.style.display = 'none';
            }
        });
    }

    async loadTransactions() {
        const categoryFilter = document.getElementById('category-filter').value;
        const typeFilter = document.getElementById('type-filter').value;
        const dateFilter = document.getElementById('date-filter').value;

        const params = new URLSearchParams();
        if (categoryFilter !== 'all') params.append('category', categoryFilter);
        if (typeFilter !== 'all') params.append('type', typeFilter);
        if (dateFilter) params.append('date', dateFilter);

        try {
            const [transactionsResponse, summaryResponse] = await Promise.all([
                fetch(`/api/autres-paiements?${params}`),
                fetch('/api/autres-paiements/summary')
            ]);

            this.transactions = await transactionsResponse.json();
            const summary = await summaryResponse.json();

            this.updateDashboard(summary);
            this.renderTransactions();
        } catch (error) {
            console.error('Error loading data:', error);
            alert('Erreur lors du chargement des données');
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();

        const transactionData = {
            type: this.currentTransactionType,
            amount: parseFloat(document.getElementById('transaction-amount').value),
            category: document.getElementById('transaction-category').value,
            date: document.getElementById('transaction-date').value,
            description: document.getElementById('transaction-description').value
        };

        try {
            const response = await fetch('/api/autres-paiements', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(transactionData)
            });

            if (!response.ok) throw new Error('Erreur lors de l\'ajout de la transaction');

            this.modal.style.display = 'none';
            this.form.reset();
            await this.loadTransactions();
        } catch (error) {
            console.error('Error:', error);
            alert('Erreur lors de l\'ajout de la transaction');
        }
    }

    updateDashboard(summary) {
        document.getElementById('total-revenue').textContent = `${summary.revenue.toFixed(2)} €`;
        document.getElementById('total-expenses').textContent = `${summary.expenses.toFixed(2)} €`;
        document.getElementById('total-balance').textContent = `${summary.balance.toFixed(2)} €`;
    }

    renderTransactions() {
        const transactionsList = document.querySelector('.transactions-list');
        
        transactionsList.innerHTML = this.transactions.length === 0 
            ? '<p class="text-center">Aucune transaction trouvée</p>'
            : this.transactions.map(this.createTransactionHTML).join('');
    }

    createTransactionHTML(transaction) {
        const categories = {
            utilities: 'Utilités',
            rent: 'Loyer',
            office: 'Fournitures de bureau',
            repairs: 'Réparations',
            other: 'Autres'
        };

        return `
            <div class="transaction-item" data-id="${transaction.id}">
                <div class="transaction-info">
                    <div class="transaction-primary">
                        <span class="transaction-date">${new Date(transaction.date).toLocaleDateString()}</span>
                        <span class="transaction-category">${categories[transaction.category]}</span>
                    </div>
                    <div class="transaction-description">${transaction.description}</div>
                </div>
                <div class="transaction-amount ${transaction.type}">
                    ${transaction.type === 'revenue' ? '+' : '-'} ${transaction.amount.toFixed(2)} €
                </div>
            </div>
        `;
    }
}

function showTransactionModal(type) {
    const modal = document.getElementById('transaction-modal');
    const modalTitle = document.getElementById('modal-title');
    
    modalTitle.textContent = type === 'revenue' ? 'Ajouter un revenu' : 'Ajouter une dépense';
    window.transactionManager.currentTransactionType = type;
    
    modal.style.display = 'block';
}

window.addEventListener('DOMContentLoaded', () => {
    window.transactionManager = new TransactionManager();
});