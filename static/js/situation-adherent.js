// situation-adherent.js
class SituationAdherent {
    constructor() {
        this.initializeSearchBox();
        this.currentAdherent = null;
        this.setupEventListeners();
    }

    initializeSearchBox() {
        $("#search-adherent").autocomplete({
            source: (request, response) => {
                $.getJSON("/api/search-adherent", {
                    term: request.term
                }, (data) => {
                    response(data.map(item => ({
                        label: item.label,
                        value: item.matricule
                    })));
                });
            },
            minLength: 2,
            select: (event, ui) => {
                event.preventDefault();
                $("#search-adherent").val(ui.item.label);
                this.loadAdherentSituation(ui.item.value);
            }
        });
    }

    setupEventListeners() {
        // Close modal handler
        $(".close-modal").click(() => {
            $("#payment-modal").hide();
        });

        // Close modal when clicking outside
        $(window).click((event) => {
            if ($(event.target).hasClass('modal')) {
                $(event.target).hide();
            }
        });
    }

    async loadAdherentSituation(matricule) {
        try {
            const response = await fetch(`/api/situation-adherent/${matricule}`);
            const data = await response.json();
            
            if (!response.ok) throw new Error(data.error || 'Erreur lors du chargement');
            
            this.currentAdherent = data;
            this.updateUI(data);
            $("#situation-content").fadeIn();
            
        } catch (error) {
            console.error('Error:', error);
            alert('Erreur lors du chargement des données');
        }
    }

    updateUI(data) {
        // Update personal information
        $("#matricule").text(data.adherent.matricule);
        $("#nom").text(data.adherent.nom);
        $("#prenom").text(data.adherent.prenom);
        $("#date-naissance").text(new Date(data.adherent.date_naissance).toLocaleDateString());
        $("#telephone").text(data.adherent.tel1 || '-');
        $("#email").text(data.adherent.email);

        // Update subscription information
        $("#type-abonnement").text(data.adherent.type_abonnement || '-');
        $("#groupe").text(data.adherent.groupe || '-');
        $("#entraineur").text(data.adherent.entraineur || '-');
        $("#status").text(data.adherent.status)
            .removeClass()
            .addClass(data.adherent.status === 'Actif' ? 'text-success' : 'text-danger');

        // Update payment information
        $("#total-a-payer").text(`${data.paiements.total_a_payer.toFixed(2)} €`);
        $("#total-paye").text(`${data.paiements.total_paye.toFixed(2)} €`);
        $("#total-remise").text(`${data.paiements.total_remise.toFixed(2)} €`);
        $("#reste-a-payer").text(`${data.paiements.reste_a_payer.toFixed(2)} €`)
            .removeClass()
            .addClass(data.paiements.reste_a_payer > 0 ? 'text-danger' : 'text-success');

        // Update presence information
        $("#total-presences").text(data.presences.total);
        $("#presences").text(data.presences.present);
        $("#absences").text(data.presences.absent);

        // Update next session information
        if (data.prochaine_seance) {
            $("#prochaine-date").text(new Date(data.prochaine_seance.date).toLocaleDateString());
            $("#prochaine-heure").text(data.prochaine_seance.heure);
            $("#prochaine-groupe").text(data.prochaine_seance.groupe);
        } else {
            $("#prochaine-date, #prochaine-heure, #prochaine-groupe").text('-');
        }
    }

    showPaymentHistory() {
        if (!this.currentAdherent) return;

        const historique = this.currentAdherent.paiements.historique;
        const container = $(".payment-history-list");
        
        container.empty();
        
        historique.forEach(payment => {
            container.append(`
                <div class="payment-item">
                    <div class="payment-detail">
                        <strong>Date:</strong> ${new Date(payment.date).toLocaleDateString()}
                    </div>
                    <div class="payment-detail">
                        <strong>Montant:</strong> ${payment.montant.toFixed(2)} €
                    </div>
                    <div class="payment-detail">
                        <strong>Payé:</strong> ${payment.montant_paye.toFixed(2)} €
                    </div>
                    <div class="payment-detail">
                        <strong>Type:</strong> ${payment.type_reglement || '-'}
                    </div>
                    ${payment.numero_cheque ? `
                        <div class="payment-detail">
                            <strong>N° Chèque:</strong> ${payment.numero_cheque}
                        </div>
                    ` : ''}
                    ${payment.banque ? `
                        <div class="payment-detail">
                            <strong>Banque:</strong> ${payment.banque}
                        </div>
                    ` : ''}
                    <div class="payment-detail">
                        <strong>N° Bon:</strong> ${payment.numero_bon}
                    </div>
                    <div class="payment-detail">
                        <strong>N° Carnet:</strong> ${payment.numero_carnet}
                    </div>
                    ${payment.remise > 0 ? `
                        <div class="payment-detail">
                            <strong>Remise:</strong> ${payment.remise.toFixed(2)} €
                        </div>
                    ` : ''}
                </div>
            `);
        });

        $("#payment-modal").show();
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.situationAdherent = new SituationAdherent();
});

// Global function for the payment history modal
function showPaymentHistory() {
    window.situationAdherent.showPaymentHistory();
}