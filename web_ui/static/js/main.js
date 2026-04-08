/**
 * Main JavaScript untuk Sistem Pakar Diagnosa Medis
 * Menghandle interactivity umum dan utilitas
 */

// Global configuration
const CONFIG = {
    API_BASE_URL: '',
    ANIMATION_DURATION: 300,
    CF_MIN: 0.1,
    CF_MAX: 1.0,
    CF_DEFAULT: 0.8
};

// Utility functions
const utils = {
    /**
     * Animasi fade in untuk elemen
     */
    fadeIn(element, duration = CONFIG.ANIMATION_DURATION) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let opacity = 0;
        const timer = setInterval(() => {
            opacity += 50 / duration;
            if (opacity >= 1) {
                clearInterval(timer);
                opacity = 1;
            }
            element.style.opacity = opacity;
        }, 50);
    },
    
    /**
     * Animasi fade out untuk elemen
     */
    fadeOut(element, duration = CONFIG.ANIMATION_DURATION) {
        let opacity = 1;
        const timer = setInterval(() => {
            opacity -= 50 / duration;
            if (opacity <= 0) {
                clearInterval(timer);
                opacity = 0;
                element.style.display = 'none';
            }
            element.style.opacity = opacity;
        }, 50);
    },
    
    /**
     * Format CF value dengan 3 decimal places
     */
    formatCF(cf) {
        return parseFloat(cf).toFixed(3);
    },
    
    /**
     * Convert CF to percentage
     */
    cfToPercentage(cf) {
        return Math.round(cf * 100);
    },
    
    /**
     * Get confidence level berdasarkan CF
     */
    getConfidenceLevel(cf) {
        if (cf >= 0.8) return { level: 'Sangat Tinggi', class: 'very-high', color: 'success' };
        if (cf >= 0.6) return { level: 'Tinggi', class: 'high', color: 'primary' };
        if (cf >= 0.4) return { level: 'Sedang', class: 'medium', color: 'warning' };
        return { level: 'Rendah', class: 'low', color: 'secondary' };
    },
    
    /**
     * Format display name dari symptom/conclusion
     */
    formatDisplayName(name) {
        return name.replace(/_/g, ' ')
                  .split(' ')
                  .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                  .join(' ');
    },
    
    /**
     * Show loading spinner
     */
    showLoading(container, message = 'Loading...') {
        container.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">${message}</p>
            </div>
        `;
    },
    
    /**
     * Show error message
     */
    showError(container, message) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Error:</strong> ${message}
            </div>
        `;
    },
    
    /**
     * Debounce function untuk search
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Validate CF value
     */
    validateCF(value) {
        const cf = parseFloat(value);
        return !isNaN(cf) && cf >= CONFIG.CF_MIN && cf <= CONFIG.CF_MAX;
    }
};

// Toast notification system
const toast = {
    show(message, type = 'info', duration = 3000) {
        const toastContainer = this.getContainer();
        const toastId = 'toast-' + Date.now();
        
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const bsToast = new bootstrap.Toast(toastElement, { delay: duration });
        bsToast.show();
        
        // Auto remove after hiding
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    },
    
    getContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    },
    
    success(message, duration = 3000) {
        this.show(message, 'success', duration);
    },
    
    error(message, duration = 5000) {
        this.show(message, 'danger', duration);
    },
    
    warning(message, duration = 4000) {
        this.show(message, 'warning', duration);
    },
    
    info(message, duration = 3000) {
        this.show(message, 'info', duration);
    }
};

// API helper functions
const api = {
    async get(endpoint) {
        try {
            const response = await fetch(CONFIG.API_BASE_URL + endpoint);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    },
    
    async post(endpoint, data) {
        try {
            const response = await fetch(CONFIG.API_BASE_URL + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    }
};

// Progress ring component
class ProgressRing {
    constructor(element, cf = 0) {
        this.element = element;
        this.radius = 25;
        this.circumference = 2 * Math.PI * this.radius;
        this.cf = cf;
        
        this.create();
        this.setValue(cf);
    }
    
    create() {
        this.element.innerHTML = `
            <svg width="60" height="60" class="progress-ring">
                <circle class="background" cx="30" cy="30" r="${this.radius}"/>
                <circle class="progress" cx="30" cy="30" r="${this.radius}"/>
            </svg>
            <div class="position-absolute top-50 start-50 translate-middle">
                <small class="fw-bold">${this.cf * 100}%</small>
            </div>
        `;
        
        const progressCircle = this.element.querySelector('.progress');
        progressCircle.style.strokeDasharray = `${this.circumference} ${this.circumference}`;
        progressCircle.style.strokeDashoffset = this.circumference;
    }
    
    setValue(cf) {
        this.cf = cf;
        const progressCircle = this.element.querySelector('.progress');
        const percentageText = this.element.querySelector('small');
        
        const offset = this.circumference - (cf * this.circumference);
        progressCircle.style.strokeDashoffset = offset;
        
        // Update color based on confidence level
        const confidence = utils.getConfidenceLevel(cf);
        progressCircle.style.stroke = getComputedStyle(document.documentElement)
            .getPropertyValue(`--${confidence.color}-color`) || '#007bff';
        
        if (percentageText) {
            percentageText.textContent = `${Math.round(cf * 100)}%`;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add smooth scroll behavior
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
    
    // Add loading animation to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled && !this.classList.contains('no-loading')) {
                const originalContent = this.innerHTML;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
                this.disabled = true;
                
                // Re-enable after a short delay (will be overridden by actual processing)
                setTimeout(() => {
                    this.innerHTML = originalContent;
                    this.disabled = false;
                }, 2000);
            }
        });
    });
    
    console.log('Sistema Pakar Web UI initialized successfully');
});

// Export untuk digunakan di file lain
window.utils = utils;
window.toast = toast;
window.api = api;
window.ProgressRing = ProgressRing;
window.CONFIG = CONFIG;