// Gestion de l'interface utilisateur
document.addEventListener('DOMContentLoaded', function() {
    const formulaire = document.getElementById('formulaireUpload');
    const inputFichier = document.getElementById('inputFichier');
    const zoneStatut = document.getElementById('zoneStatut');
    const zoneResultat = document.getElementById('zoneResultat');
    const boutonTelechargement = document.getElementById('boutonTelechargement');

    // Gestion de la soumission du formulaire
    formulaire.addEventListener('submit', function(evenement) {
        evenement.preventDefault();
        
        const fichier = inputFichier.files[0];
        if (!fichier) {
            afficherStatut('Veuillez sélectionner un fichier CSV', 'erreur');
            return;
        }

        const donneesFormulaire = new FormData();
        donneesFormulaire.append('fichier', fichier);

        afficherStatut('Nettoyage en cours...', 'info');

        // Envoi au serveur
        fetch('/upload', {
            method: 'POST',
            body: donneesFormulaire
        })
        .then(reponse => {
            if (!reponse.ok) {
                return reponse.json().then(erreur => {
                    throw new Error(erreur.erreur || 'Erreur serveur');
                });
            }
            return reponse.json();
        })
        .then(donnees => {
            if (donnees.succes) {
                afficherResultat(donnees);
            } else {
                throw new Error(donnees.erreur || 'Échec du nettoyage');
            }
        })
        .catch(erreur => {
            afficherStatut(erreur.message, 'erreur');
            console.error("Erreur :", erreur);
        });
    });

    // Fonctions utilitaires
    function afficherStatut(message, type) {
        zoneStatut.textContent = message;
        zoneStatut.className = `statut ${type}`;
    }

    function afficherResultat(donnees) {
        afficherStatut(donnees.message, 'succes');
        
        // Création d'un aperçu du tableau
        let htmlApercu = `
        <h3>Aperçu complet des données nettoyées (${donnees.apercu.length} lignes) :</h3>
        <div style="max-height: 400px; overflow-y: auto;">
            <table class="table table-striped">
                <thead class="sticky-top bg-white">
                    <tr>
    `;        
        // En-têtes
        for (const colonne in donnees.apercu[0]) {
            htmlApercu += `<th>${colonne}</th>`;
        }
        htmlApercu += '</tr></thead><tbody>';
        
        // Données
        donnees.apercu.forEach(ligne => {
            htmlApercu += '<tr>';
            for (const valeur in ligne) {
                htmlApercu += `<td>${ligne[valeur]}</td>`;
            }
            htmlApercu += '</tr>';
        });
        
        htmlApercu += `</tbody></table></div>`;
        
        zoneResultat.innerHTML = htmlApercu;
        boutonTelechargement.href = `/telecharger/${donnees.fichier}`;
        boutonTelechargement.style.display = 'block';
    }
});