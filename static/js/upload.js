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
            showAlert('Please select a ZIP file to upload.', 'danger');
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
        showAlert('Please upload a ZIP file.', 'danger');
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
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
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
        showAlert('A file is already being processed. Please wait.', 'warning');
        return;
    }
    
    // Update status
    uploadStatus = 'uploading';
    updateProgressUI(5, 'Uploading file...', 'upload');
    
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
                throw new Error(data.error || 'Upload failed');
            });
        }
        return response.json();
    })
    .then(data => {
        // Upload successful, start processing
        updateProgressUI(30, 'Upload complete. Starting processing...', 'process');
        
        // Start processing the file
        return startProcessing(data.zip_path, data.file_count);
    })
    .catch(error => {
        uploadStatus = 'error';
        updateProgressUI(0, '', 'error');
        showAlert(`Error: ${error.message}`, 'danger');
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
                throw new Error(data.error || 'Processing failed');
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
        showAlert(`Error: ${error.message}`, 'danger');
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
                    throw new Error(data.error || 'Status check failed');
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
                    updateProgressUI(30, 'Extracting files from ZIP...', 'process');
                    break;
                    
                case 'converting':
                    const convertProgress = data.progress_percent || 35;
                    updateProgressUI(convertProgress, `Converting files (${data.converted || 0}/${data.total_files || fileCount})...`, 'process');
                    break;
                    
                case 'processing':
                    const processedPercent = data.progress_percent || 
                                            (data.processed && data.total ? Math.round((data.processed / data.total) * 40) + 40 : 50);
                    updateProgressUI(processedPercent, `Merging documents (${data.processed || 0}/${data.total || fileCount})...`, 'process');
                    break;
                    
                case 'merging_complete':
                    updateProgressUI(80, 'File merging complete. Converting to PDF...', 'process');
                    break;
                    
                case 'converting_to_pdf':
                    updateProgressUI(85, 'Converting merged document to PDF...', 'process');
                    break;
                    
                case 'pdf_conversion_complete':
                    updateProgressUI(95, 'PDF conversion complete. Finalizing...', 'process');
                    break;
                    
                case 'complete':
                    uploadStatus = 'complete';
                    updateProgressUI(100, 'Processing complete!', 'complete');
                    clearInterval(statusCheckInterval);
                    showResults(data);
                    break;
                    
                case 'error':
                    uploadStatus = 'error';
                    updateProgressUI(0, '', 'error');
                    showAlert(`Error: ${data.error || 'An unknown error occurred'}`, 'danger');
                    clearInterval(statusCheckInterval);
                    break;
                    
                default:
                    // Unknown status
                    console.log('Unknown status:', data.status);
            }
        })
        .catch(error => {
            console.error('Error checking status:', error);
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
    showAlert('Files have been successfully processed!', 'success');
    
    // Create the result card
    resultContainer.innerHTML = `
        <div class="card success-card">
            <div class="card-header">
                <h5 class="card-title"><i class="fas fa-check-circle text-success me-2"></i>Processing Complete</h5>
            </div>
            <div class="card-body">
                <p>Your files have been successfully processed.</p>
                
                <div class="result-stats mb-3">
                    <div class="row">
                        <div class="col">
                            <div class="d-flex align-items-center">
                                <div class="me-3">
                                    <i class="fas fa-file-alt fa-2x text-success"></i>
                                </div>
                                <div>
                                    <div class="fw-bold">Processed Files</div>
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
                                    <div class="fw-bold">Failed Files</div>
                                    <div>${data.failed_files || 0}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                ${data.failed_files > 0 ? `
                <div class="alert alert-warning">
                    <strong>Note:</strong> Some files could not be processed. They have been skipped in the merged document.
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-warning" type="button" data-bs-toggle="collapse" data-bs-target="#failedFilesList">
                            Show Failed Files
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
                                <h5 class="card-title">Merged DOCX</h5>
                                <p class="card-text">Download the merged Word document</p>
                                <a href="/download/docx" class="btn btn-primary download-button">
                                    <i class="fas fa-download me-2"></i>Download DOCX
                                </a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body text-center">
                                <i class="fas fa-file-pdf fa-3x text-danger mb-3"></i>
                                <h5 class="card-title">Merged PDF</h5>
                                <p class="card-text">Download the converted PDF document</p>
                                <a href="/download/pdf" class="btn btn-danger download-button" ${!data.pdf_conversion_success ? 'disabled' : ''}>
                                    <i class="fas fa-download me-2"></i>Download PDF
                                </a>
                                ${!data.pdf_conversion_success ? '<p class="text-muted mt-2 small">PDF conversion was not available</p>' : ''}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <button id="reset-button" class="btn btn-secondary">
                        <i class="fas fa-redo me-2"></i>Process Another File
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
    
    // Reset UI elements
    document.getElementById('file-info').classList.add('d-none');
    document.getElementById('upload-button').disabled = true;
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', 0);
    progressStatus.textContent = '';
    
    // Reset step indicators
    uploadStep.classList.remove('step-active', 'step-complete');
    processStep.classList.remove('step-active', 'step-complete');
    completeStep.classList.remove('step-active', 'step-complete');
    
    // Clear results
    resultContainer.innerHTML = '';
    
    // Reset status
    uploadStatus = 'idle';
    
    // Clear any status check interval
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
    
    // Clear alerts
    alertContainer.innerHTML = '';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
