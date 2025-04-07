// Gestion des raccourcis clavier
document.addEventListener('DOMContentLoaded', function() {
    setupKeyboardShortcuts();
});

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+O : Ouvrir le sélecteur de fichiers
        if (e.ctrlKey && e.key === 'o') {
            e.preventDefault();
            document.getElementById('file-input').click();
        }
        
        // Escape : Annuler l'opération en cours
        if (e.key === 'Escape') {
            if (uploadStatus === 'uploading' || uploadStatus === 'processing') {
                if (confirm('Voulez-vous vraiment annuler l\'opération en cours ?')) {
                    resetApplication();
                }
            }
        }
        
        // Ctrl+D : Télécharger DOCX (si disponible)
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            const docxLink = document.querySelector('a[href="/download/docx"]');
            if (docxLink && !docxLink.hasAttribute('disabled')) {
                docxLink.click();
            }
        }
        
        // Ctrl+P : Télécharger PDF (si disponible)
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            const pdfLink = document.querySelector('a[href="/download/pdf"]');
            if (pdfLink && !pdfLink.hasAttribute('disabled')) {
                pdfLink.click();
            } else {
                // Si l'impression native est activée, ne pas l'empêcher
                return true;
            }
        }
        
        // Ctrl+R : Réinitialiser l'application (seulement si terminé)
        if (e.ctrlKey && e.key === 'r') {
            if (uploadStatus === 'complete' || uploadStatus === 'error') {
                e.preventDefault(); // Empêcher le rechargement de la page
                resetApplication();
            }
        }
    });
}
