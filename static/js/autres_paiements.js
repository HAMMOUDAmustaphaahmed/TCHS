class TransactionsManager {
    constructor() {
        this.transactions = [];
        this.modal = document.getElementById('transaction-modal');
        this.form = document.getElementById('transaction-form');
        this.fileDropArea = document.querySelector('.file-drop-area');
        this.fileInput = document.getElementById('documents');
        this.fileList = document.getElementById('file-list');
        
        this.initializeEventListeners();
        this.loadTransactions();
    }

    initializeEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        document.querySelector('.close-modal').addEventListener('click', () => {
            this.modal.style.display = 'none';
        });

        document.getElementById('category-filter').addEventListener('change', () => this.loadTransactions());
        document.getElementById('date-filter').addEventListener('change', () => this.loadTransactions());

        // File drop area handlers
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.fileDropArea.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.fileDropArea.addEventListener(eventName, () => {
                this.fileDropArea.classList.add('highlight');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.fileDropArea.addEventListener(eventName, () => {
                this.fileDropArea.classList.remove('highlight');
            });
        });

        this.fileDropArea.addEventListener('drop', (e) => this.handleDrop(e));
        this.fileInput.addEventListener('change', (e) => this.handleFiles(e.target.files));

        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.modal.style.display = 'none';
            }
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        this.handleFiles(files);
    }

    handleFiles(files) {
        this.fileList.innerHTML = '';
        Array.from(files).forEach(file => {
            const item = document.createElement('div');
            item.className = 'file-item';
            item.innerHTML = `
                <i class="fas fa-file"></i>
                <span>${file.name}</span>
            `;
            this.fileList.appendChild(item);
        });
    }

    async loadTransactions() {
        const categoryFilter = document.getElementById('category-filter').value;
        const dateFilter = document.getElementById('date-filter').value;

        const params = new URLSearchParams();
        if (categoryFilter !== 'all') params.append('category', categoryFilter);
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
    // Add these methods to your TransactionsManager class
async deleteTransaction(id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette transaction ?')) {
        return;
    }

    try {
        const response = await fetch(`/api/autres-paiements/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Erreur lors de la suppression');

        await this.loadTransactions();
    } catch (error) {
        console.error('Error:', error);
        alert('Erreur lors de la suppression de la transaction');
    }
}

async editTransaction(id) {
    try {
        const transaction = this.transactions.find(t => t.id === id);
        if (!transaction) throw new Error('Transaction non trouvée');

        // Populate the modal with transaction data
        document.getElementById('modal-title').textContent = 'Modifier la transaction';
        document.getElementById('transaction-amount').value = transaction.amount;
        document.getElementById('transaction-category').value = transaction.category;
        document.getElementById('transaction-date').value = transaction.date;
        document.getElementById('transaction-description').value = transaction.description;
        document.getElementById('company-name').value = transaction.company_name;
        document.getElementById('bank-name').value = transaction.bank_name;
        document.getElementById('rib').value = transaction.rib || '';
        document.getElementById('location').value = transaction.location || '';

        // Add a data attribute to the form to indicate we're editing
        const form = document.getElementById('transaction-form');
        form.dataset.editId = id;

        // Show the modal
        this.modal.style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        alert('Erreur lors du chargement de la transaction');
    }
}
    async handleFormSubmit(e) {
        e.preventDefault();
        
        try {
            const formData = new FormData();
            const form = e.target;
            const isEdit = form.dataset.editId;
            
            // Add form fields
            const fields = {
                'amount': 'transaction-amount',
                'category': 'transaction-category',
                'date': 'transaction-date',
                'description': 'transaction-description',
                'company_name': 'company-name',
                'bank_name': 'bank-name',
                'rib': 'rib',
                'location': 'location'
            };
    
            for (const [key, id] of Object.entries(fields)) {
                const value = document.getElementById(id).value;
                if (!value && key !== 'rib' && key !== 'location') {
                    throw new Error(`Le champ ${key} est requis`);
                }
                formData.append(key, value);
            }
    
            // Add files
            const fileInput = document.getElementById('documents');
            Array.from(fileInput.files).forEach(file => {
                formData.append('documents', file);
            });
    
            const url = isEdit 
                ? `/api/autres-paiements/${form.dataset.editId}`
                : '/api/autres-paiements';
            
            const method = isEdit ? 'PUT' : 'POST';
    
            const response = await fetch(url, {
                method: method,
                body: formData
            });
    
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erreur lors de l\'opération');
            }
    
            // Reset form and close modal
            this.modal.style.display = 'none';
            form.reset();
            delete form.dataset.editId;
            this.fileList.innerHTML = '';
            await this.loadTransactions();
    
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    }

    updateDashboard(summary) {
        document.getElementById('total-expenses').textContent = `${summary.expenses.toFixed(2)} €`;
    }

    renderTransactions() {
        const transactionsList = document.querySelector('.transactions-list');
        
        if (this.transactions.length === 0) {
            transactionsList.innerHTML = '<p class="text-center">Aucune transaction trouvée</p>';
            return;
        }
    
        transactionsList.innerHTML = this.transactions.map(transaction => `
            <div class="transaction-item" data-id="${transaction.id}">
                <div class="transaction-info">
                    <div class="transaction-header">
                        <span class="company-name">${transaction.company_name}</span>
                        <div class="transaction-actions">
                            <button class="btn-edit" onclick="transactionsManager.editTransaction(${transaction.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn-delete" onclick="transactionsManager.deleteTransaction(${transaction.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="transaction-details">
                        <span class="transaction-date">${new Date(transaction.date).toLocaleDateString()}</span>
                        <span class="category">${this.getCategoryLabel(transaction.category)}</span>
                        <span class="bank-info">Banque: ${transaction.bank_name}</span>
                        ${transaction.rib ? `<span class="rib">RIB: ${transaction.rib}</span>` : ''}
                        ${transaction.location ? `<span class="location">Location: ${transaction.location}</span>` : ''}
                    </div>
                    <div class="transaction-description">${transaction.description}</div>
                    ${transaction.documents && transaction.documents.length > 0 ? `
                        <div class="transaction-documents">
                            <h4>Documents:</h4>
                            <div class="document-list">
                                ${transaction.documents.map(doc => `
                                    <a href="/api/autres-paiements/${transaction.id}/documents/${doc}" 
                                       class="document-link" 
                                       download="${doc}">
                                        <i class="fas fa-file"></i> ${doc}
                                    </a>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                <div class="transaction-amount expense">
                    ${transaction.amount.toFixed(2)} €
                </div>
            </div>
        `).join('');
    }

    getCategoryLabel(category) {
        const categories = {
            utilities: 'Utilités',
            rent: 'Loyer',
            office: 'Fournitures de bureau',
            repairs: 'Réparations',
            other: 'Autres'
        };
        return categories[category] || category;
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.transactionsManager = new TransactionsManager();
});

function showTransactionModal() {
    document.getElementById('transaction-modal').style.display = 'block';
}