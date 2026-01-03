// situation-adherent.js
class SituationAdherent {
    constructor() {
        this.currentAdherent = null;
        this.initializeSearchBox();
        this.setupEventListeners();
    }

    initializeSearchBox() {
        $("#search-adherent").autocomplete({
            source: (request, response) => {
                $.getJSON("/api/search-adherent", { term: request.term }, (data) => {
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
        // Fermer le modal paiement
        $(".close-modal").click(() => $("#payment-modal").hide());

        // Fermer modal en cliquant à l’extérieur
        $(window).click((event) => {
            if ($(event.target).hasClass('modal')) $(event.target).hide();
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
            console.error('Erreur:', error);
            alert('Erreur lors du chargement des données.');
        }
    }

    updateUI(data) {
        const a = data.adherent;
        const p = data.paiements;
        const presences = data.presences;
        const prochaine = data.prochaine_seance;

        // --- Infos personnelles ---
        $("#matricule").text(a.matricule);
        $("#nom").text(a.nom);
        $("#prenom").text(a.prenom);
        $("#date-naissance").text(new Date(a.date_naissance).toLocaleDateString());
        $("#telephone").text(a.tel1 || "-");
        $("#email").text(a.email || "-");

        // --- Abonnement ---
        $("#type-abonnement").text(a.type_abonnement || "-");
        $("#groupe").text(a.groupe || "-");
        $("#entraineur").text(a.entraineur || "-");
        $("#status")
            .text(a.status)
            .removeClass()
            .addClass(a.status === 'Actif' ? 'text-success' : 'text-danger');

        // --- Paiement ---
        $("#total-a-payer").text(p.total_a_payer.toFixed(2) + " €");
        $("#total-paye").text(p.total_paye.toFixed(2) + " €");
        $("#total-remise").text(p.total_remise.toFixed(2) + " %");
        $("#reste-a-payer")
            .text(p.reste_a_payer.toFixed(2) + " €")
            .removeClass()
            .addClass(p.reste_a_payer > 0 ? 'text-danger' : 'text-success');

        // --- Présences ---
        $("#total-presences").text(presences.total);
        $("#presences").text(presences.present);
        $("#absences").text(presences.absent);

        // --- Prochaine séance ---
        $("#prochaine-date").text(prochaine?.date ? new Date(prochaine.date).toLocaleDateString() : "-");
        $("#prochaine-heure").text(prochaine?.heure || "-");
        $("#prochaine-groupe").text(prochaine?.groupe || "-");
    }

    showPaymentHistory() {
        if (!this.currentAdherent) return;
        const historique = this.currentAdherent.paiements.historique;
        const container = $(".payment-history-list");

        container.empty(); // Important pour ne pas dupliquer

        historique.forEach(p => {
            container.append(`
                <div class="payment-item">
                    <div class="payment-detail"><strong>Date:</strong> ${new Date(p.date).toLocaleDateString()}</div>
                    <div class="payment-detail"><strong>Montant:</strong> ${p.montant.toFixed(2)} €</div>
                    <div class="payment-detail"><strong>Payé:</strong> ${p.montant_paye.toFixed(2)} €</div>
                    <div class="payment-detail"><strong>Type:</strong> ${p.type_reglement || '-'}</div>
                    ${p.numero_cheque ? `<div class="payment-detail"><strong>N° Chèque:</strong> ${p.numero_cheque}</div>` : ''}
                    ${p.banque ? `<div class="payment-detail"><strong>Banque:</strong> ${p.banque}</div>` : ''}
                    <div class="payment-detail"><strong>N° Bon:</strong> ${p.numero_bon}</div>
                    <div class="payment-detail"><strong>N° Carnet:</strong> ${p.numero_carnet}</div>
                    ${p.remise > 0 ? `<div class="payment-detail"><strong>Remise:</strong> ${p.remise.toFixed(2)} €</div>` : ''}
                </div>
            `);
        });

        $("#payment-modal").fadeIn();
    }
}

// --- Initialisation ---
document.addEventListener('DOMContentLoaded', () => {
    window.situationAdherent = new SituationAdherent();
});

// Fonction globale pour modal historique
function showPaymentHistory() {
    window.situationAdherent.showPaymentHistory();
}
