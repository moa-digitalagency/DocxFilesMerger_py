/**
 * DocxFilesMerger - Application de traitement et fusion de documents.
 * Développé par MOA Digital Agency LLC (https://myoneart.com)
 * Email: moa@myoneart.com
 * Copyright © 2025 MOA Digital Agency LLC. Tous droits réservés.
 */
// Global variables
let uploadStatus = 'idle'; // idle, uploading, processing, complete, error
let statusCheckInterval = null;

// DOM elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadForm = document.getElementById('upload-form');
const progressBar = document.getElementById('progress-bar');
const progressStatus = document.getElementById('progress-status');
const uploadStep = document.getElementById('upload-step');
const processStep = document.getElementById('process-step');
const completeStep = document.getElementById('complete-step');
const alertContainer = document.getElementById('alert-container');
const resultContainer = document.getElementById('result-container');

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Set up the file drop zone
    setupDropZone();
    
    // Set up the form submission
    setupForm();
});

// Set up the drag and drop functionality
function setupDropZone() {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    
    // Handle click to select file
    dropZone.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Handle file selection
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });
}

// Set up the form submission
function setupForm() {
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (fileInput.files.length > 0) {
            uploadFile(fileInput.files[0]);
        } else {
            showAlert('Veuillez sélectionner un fichier ZIP à téléverser.', 'danger');
        }
    });
}

// Utility functions
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    dropZone.classList.add('drag-over');
}

function unhighlight() {
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    handleFiles(files);
}

function handleFiles(files) {
    if (files.length === 0) return;
    
    const file = files[0];
    
    // Check if it's a ZIP file
    if (file.type !== 'application/zip' && !file.name.toLowerCase().endsWith('.zip')) {
        showAlert('Veuillez téléverser un fichier ZIP.', 'danger');
        return;
    }
    
    // Update the file info in the UI
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatFileSize(file.size);
    document.getElementById('file-info').classList.remove('d-none');
    
    // Enable the upload button
    document.getElementById('upload-button').disabled = false;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Octets';
    
    const k = 1024;
    const sizes = ['Octets', 'Ko', 'Mo', 'Go'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showAlert(message, type = 'info') {
    // Clear previous alerts
    alertContainer.innerHTML = '';
    
    // Create the alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to the container
    alertContainer.appendChild(alert);
    alertContainer.scrollIntoView({ behavior: 'smooth' });
}

function uploadFile(file) {
    if (uploadStatus === 'uploading' || uploadStatus === 'processing') {
        showAlert('Un fichier est déjà en cours de traitement. Veuillez patienter.', 'warning');
        return;
    }
    
    // Update status
    uploadStatus = 'uploading';
    updateProgressUI(5, 'Téléversement du fichier...', 'upload');
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    // Send the file to the server
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Échec du téléversement');
            });
        }
        return response.json();
    })
    .then(data => {
        // Upload successful, start processing
        updateProgressUI(30, 'Téléversement terminé. Démarrage du traitement...', 'process');
        
        // Start processing the file
        return startProcessing(data.zip_path, data.file_count);
    })
    .catch(error => {
        uploadStatus = 'error';
        updateProgressUI(0, '', 'error');
        showAlert(`Erreur : ${error.message}`, 'danger');
    });
}

function startProcessing(zipPath, fileCount) {
    // Update status
    uploadStatus = 'processing';
    
    // Request the server to process the file
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ zip_path: zipPath })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Échec du traitement');
            });
        }
        return response.json();
    })
    .then(data => {
        // Start checking status
        startStatusCheck(fileCount);
    })
    .catch(error => {
        uploadStatus = 'error';
        updateProgressUI(0, '', 'error');
        showAlert(`Erreur : ${error.message}`, 'danger');
        clearInterval(statusCheckInterval);
    });
}

function startStatusCheck(fileCount) {
    // Clear any existing interval
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    // Set up status checking
    statusCheckInterval = setInterval(() => {
        checkProcessingStatus(fileCount);
    }, 2000); // Check every 2 seconds
}

function checkProcessingStatus(fileCount) {
    fetch('/status')
        .then(response => {
            if (!response.ok) {
                if (response.status === 404) {
                    // Status file not found, keep waiting
                    return null;
                }
                return response.json().then(data => {
                    throw new Error(data.error || 'Échec de la vérification du statut');
                });
            }
            return response.json();
        })
        .then(data => {
            if (!data) return; // Status file not ready yet
            
            // Update the UI based on status
            switch (data.status) {
                case 'starting':
                case 'extracting':
                    updateProgressUI(30, 'Extraction des fichiers de l\'archive ZIP...', 'process');
                    break;
                    
                case 'converting':
                    const convertProgress = data.progress_percent || 35;
                    updateProgressUI(convertProgress, `Conversion des fichiers (${data.converted || 0}/${data.total_files || fileCount})...`, 'process');
                    break;
                    
                case 'processing':
                    const processedPercent = data.progress_percent || 
                                            (data.processed && data.total ? Math.round((data.processed / data.total) * 40) + 40 : 50);
                    updateProgressUI(processedPercent, `Fusion des documents (${data.processed || 0}/${data.total || fileCount})...`, 'process');
                    break;
                    
                case 'merging_complete':
                    updateProgressUI(80, 'Fusion des fichiers terminée. Conversion en PDF...', 'process');
                    break;
                    
                case 'converting_to_pdf':
                    updateProgressUI(85, 'Conversion du document fusionné en PDF...', 'process');
                    break;
                    
                case 'pdf_conversion_complete':
                    updateProgressUI(95, 'Conversion PDF terminée. Finalisation...', 'process');
                    break;
                    
                case 'complete':
                    uploadStatus = 'complete';
                    updateProgressUI(100, 'Traitement terminé !', 'complete');
                    clearInterval(statusCheckInterval);
                    showResults(data);
                    break;
                    
                case 'error':
                    uploadStatus = 'error';
                    updateProgressUI(0, '', 'error');
                    showAlert(`Erreur : ${data.error || 'Une erreur inconnue est survenue'}`, 'danger');
                    clearInterval(statusCheckInterval);
                    break;
                    
                default:
                    // Unknown status
                    console.log('Statut inconnu :', data.status);
            }
        })
        .catch(error => {
            console.error('Erreur lors de la vérification du statut :', error);
            // Don't stop checking on a temporary error
        });
}

function updateProgressUI(percent, statusText, step) {
    // Update progress bar
    progressBar.style.width = `${percent}%`;
    progressBar.setAttribute('aria-valuenow', percent);
    progressStatus.textContent = statusText;
    
    // Update step indicators
    uploadStep.classList.remove('step-active', 'step-complete');
    processStep.classList.remove('step-active', 'step-complete');
    completeStep.classList.remove('step-active', 'step-complete');
    
    switch (step) {
        case 'upload':
            uploadStep.classList.add('step-active');
            break;
            
        case 'process':
            uploadStep.classList.add('step-complete');
            processStep.classList.add('step-active');
            break;
            
        case 'complete':
            uploadStep.classList.add('step-complete');
            processStep.classList.add('step-complete');
            completeStep.classList.add('step-active', 'step-complete');
            break;
            
        case 'error':
            // Leave steps as is, just show error
            break;
    }
}

function showResults(data) {
    // Show success message
    showAlert('Les fichiers ont été traités avec succès !', 'success');
    
    // Create the result card
    resultContainer.innerHTML = `
        <div class="card success-card">
            <div class="card-header">
                <h5 class="card-title"><i class="fas fa-check-circle text-success me-2"></i>Traitement Terminé</h5>
            </div>
            <div class="card-body">
                <p>Vos fichiers ont été traités avec succès.</p>
                
                <div class="result-stats mb-3">
                    <div class="row">
                        <div class="col">
                            <div class="d-flex align-items-center">
                                <div class="me-3">
                                    <i class="fas fa-file-alt fa-2x text-success"></i>
                                </div>
                                <div>
                                    <div class="fw-bold">Fichiers Traités</div>
                                    <div>${data.processed_files || 0}</div>
                                </div>
                            </div>
                        </div>
                        <div class="col">
                            <div class="d-flex align-items-center">
                                <div class="me-3">
                                    <i class="fas fa-exclamation-triangle fa-2x ${data.failed_files > 0 ? 'text-warning' : 'text-secondary'}"></i>
                                </div>
                                <div>
                                    <div class="fw-bold">Fichiers Échoués</div>
                                    <div>${data.failed_files || 0}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                ${data.failed_files > 0 ? `
                <div class="alert alert-warning">
                    <strong>Remarque :</strong> Certains fichiers n'ont pas pu être traités. Ils ont été ignorés dans le document fusionné.
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-warning" type="button" data-bs-toggle="collapse" data-bs-target="#failedFilesList">
                            Afficher les fichiers échoués
                        </button>
                    </div>
                    <div class="collapse mt-2" id="failedFilesList">
                        <div class="card card-body failed-files-container">
                            <ul class="list-group list-group-flush">
                                ${data.failed_file_names?.map(file => `<li class="list-group-item">${file}</li>`).join('') || ''}
                            </ul>
                        </div>
                    </div>
                </div>
                ` : ''}
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <i class="fas fa-file-word fa-3x text-primary mb-3"></i>
                                <h5 class="card-title">DOCX Fusionné</h5>
                                <p class="card-text">Téléchargez le document Word fusionné</p>
                                <a href="/download/docx" class="btn btn-primary download-button">
                                    <i class="fas fa-download me-2"></i>Télécharger DOCX
                                </a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <i class="fas fa-file-pdf fa-3x text-danger mb-3"></i>
                                <h5 class="card-title">PDF Fusionné</h5>
                                <p class="card-text">Téléchargez le document PDF converti</p>
                                <a href="/download/pdf" class="btn btn-danger download-button" ${!data.pdf_conversion_success ? 'disabled' : ''}>
                                    <i class="fas fa-download me-2"></i>Télécharger PDF
                                </a>
                                ${!data.pdf_conversion_success ? '<p class="text-muted mt-2 small">La conversion PDF n\'était pas disponible</p>' : ''}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <button id="reset-button" class="btn btn-secondary">
                        <i class="fas fa-redo me-2"></i>Traiter un autre fichier
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Scroll to the results
    resultContainer.scrollIntoView({ behavior: 'smooth' });
    
    // Add event listener for the reset button
    document.getElementById('reset-button').addEventListener('click', resetApplication);
}

function resetApplication() {
    // Reset the form
    uploadForm.reset();
    
    // Clear file info
    document.getElementById('file-info').classList.add('d-none');
    
    // Reset progress
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', 0);
    progressStatus.textContent = '';
    
    // Reset steps
    uploadStep.classList.remove('step-active', 'step-complete');
    processStep.classList.remove('step-active', 'step-complete');
    completeStep.classList.remove('step-active', 'step-complete');
    
    // Clear results
    resultContainer.innerHTML = '';
    
    // Reset status
    uploadStatus = 'idle';
    
    // Clear any intervals
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
    
    // Disable upload button
    document.getElementById('upload-button').disabled = true;
    
    // Show message
    showAlert('Prêt pour un nouveau traitement.', 'info');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
