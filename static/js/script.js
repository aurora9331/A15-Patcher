// JavaScript for A15 Framework Patcher

document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('jar_file');
    const uploadContent = uploadArea?.querySelector('.upload-content');
    const selectedFile = document.getElementById('selectedFile');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFileBtn = document.getElementById('removeFile');
    const submitBtn = document.getElementById('submitBtn');
    const uploadForm = document.getElementById('uploadForm');

    // File input functionality
    if (uploadArea && fileInput) {
        // Click to select file
        uploadArea.addEventListener('click', function(e) {
            if (e.target !== removeFileBtn && !removeFileBtn?.contains(e.target)) {
                fileInput.click();
            }
        });

        // Drag and drop functionality
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            if (!uploadArea.contains(e.relatedTarget)) {
                uploadArea.classList.remove('dragover');
            }
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (isValidFile(file)) {
                    fileInput.files = files;
                    displaySelectedFile(file);
                } else {
                    showAlert('Sadece .jar dosyaları kabul edilir!', 'error');
                }
            }
        });

        // File input change
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                if (isValidFile(file)) {
                    displaySelectedFile(file);
                } else {
                    showAlert('Sadece .jar dosyaları kabul edilir!', 'error');
                    this.value = '';
                }
            }
        });

        // Remove file button
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                clearSelectedFile();
            });
        }
    }

    // Form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const nameInput = document.getElementById('name');
            const fileInput = document.getElementById('jar_file');
            
            if (!nameInput.value.trim()) {
                e.preventDefault();
                showAlert('Proje adı gereklidir!', 'error');
                nameInput.focus();
                return;
            }
            
            if (!fileInput.files.length) {
                e.preventDefault();
                showAlert('Lütfen bir JAR dosyası seçin!', 'error');
                return;
            }

            // Show loading state
            showLoadingState();
        });
    }

    // Helper functions
    function isValidFile(file) {
        const allowedTypes = ['.jar'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        const maxSize = 500 * 1024 * 1024; // 500MB
        
        if (!allowedTypes.includes(fileExtension)) {
            return false;
        }
        
        if (file.size > maxSize) {
            showAlert('Dosya boyutu 500MB\'dan büyük olamaz!', 'error');
            return false;
        }
        
        return true;
    }

    function displaySelectedFile(file) {
        if (fileName && fileSize && selectedFile && uploadContent) {
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            
            uploadContent.style.display = 'none';
            selectedFile.style.display = 'block';
            
            uploadArea.style.borderColor = '#198754';
            uploadArea.style.backgroundColor = 'rgba(25, 135, 84, 0.05)';
        }
    }

    function clearSelectedFile() {
        if (fileInput && selectedFile && uploadContent) {
            fileInput.value = '';
            selectedFile.style.display = 'none';
            uploadContent.style.display = 'block';
            
            uploadArea.style.borderColor = '#dee2e6';
            uploadArea.style.backgroundColor = '#fafafa';
        }
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'check-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at top of main container
        const main = document.querySelector('main.container');
        if (main) {
            main.insertBefore(alertDiv, main.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }

    function showLoadingState() {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                Dosya yükleniyor...
            `;
        }

        // Add loading class to form
        if (uploadForm) {
            uploadForm.classList.add('loading');
        }
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Form validation enhancements
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateInput(this);
        });
        
        input.addEventListener('input', function() {
            clearValidationState(this);
        });
    });

    function validateInput(input) {
        const value = input.value.trim();
        
        if (input.hasAttribute('required') && !value) {
            input.classList.add('is-invalid');
            return false;
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            return true;
        }
    }

    function clearValidationState(input) {
        input.classList.remove('is-invalid', 'is-valid');
    }

    // Check API status on page load
    checkApiStatus();

    function checkApiStatus() {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                console.log('API Status:', data);
            })
            .catch(error => {
                console.warn('API status check failed:', error);
            });
    }
});

// Global utility functions
window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Metin panoya kopyalandı!', 'success');
    }).catch(() => {
        showAlert('Kopyalama işlemi başarısız!', 'error');
    });
};

window.downloadFile = function(filename) {
    window.location.href = `/download/${filename}`;
};