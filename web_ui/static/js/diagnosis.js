/**
 * Diagnosis Page JavaScript
 * Menghandle interface untuk input gejala dan menampilkan hasil diagnosa
 */

class DiagnosisManager {
    constructor() {
        this.symptoms = [];
        this.selectedSymptoms = {};
        this.lastResults = null;
        
        this.init();
    }
    
    async init() {
        await this.loadSymptoms();
        this.setupEventListeners();
        this.setupSearch();
    }
    
    async loadSymptoms() {
        const container = document.getElementById('symptoms-container');
        utils.showLoading(container, 'Memuat daftar gejala...');
        
        try {
            const response = await api.get('/api/symptoms');
            if (response.success) {
                this.symptoms = response.symptoms;
                this.renderSymptoms();
                toast.success(`Berhasil memuat ${this.symptoms.length} gejala`);
            } else {
                throw new Error('Failed to load symptoms');
            }
        } catch (error) {
            console.error('Error loading symptoms:', error);
            utils.showError(container, 'Gagal memuat daftar gejala. Silakan refresh halaman.');
            toast.error('Gagal memuat daftar gejala');
        }
    }
    
    renderSymptoms(filteredSymptoms = null) {
        const container = document.getElementById('symptoms-container');
        const symptomsToRender = filteredSymptoms || this.symptoms;
        
        if (symptomsToRender.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-4">
                    <i class="fas fa-search text-muted" style="font-size: 3rem;"></i>
                    <p class="text-muted mt-2">Tidak ada gejala yang ditemukan</p>
                </div>
            `;
            return;
        }
        
        const symptomsHtml = symptomsToRender.map(symptom => `
            <div class="col-md-6 col-lg-4">
                <div class="symptom-card ${this.selectedSymptoms[symptom.id] ? 'selected' : ''}" 
                     data-symptom="${symptom.id}">
                    <div class="d-flex align-items-center mb-2">
                        <input type="checkbox" 
                               class="form-check-input symptom-checkbox me-3" 
                               id="symptom-${symptom.id}"
                               ${this.selectedSymptoms[symptom.id] ? 'checked' : ''}>
                        <label class="form-check-label fw-bold flex-grow-1" 
                               for="symptom-${symptom.id}">
                            ${symptom.name}
                        </label>
                    </div>
                    
                    <div class="cf-input-group">
                        <label class="form-label small text-muted">Tingkat Keyakinan (CF):</label>
                        <div class="input-group input-group-sm">
                            <input type="number" 
                                   class="form-control cf-input" 
                                   id="cf-${symptom.id}"
                                   min="${CONFIG.CF_MIN}" 
                                   max="${CONFIG.CF_MAX}" 
                                   step="0.1" 
                                   value="${this.selectedSymptoms[symptom.id] || CONFIG.CF_DEFAULT}"
                                   ${!this.selectedSymptoms[symptom.id] ? 'disabled' : ''}>
                            <span class="input-group-text">
                                <i class="fas fa-percent"></i>
                            </span>
                        </div>
                        <div class="form-text">
                            ${symptom.description}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = symptomsHtml;
        
        // Re-attach event listeners untuk symptom cards
        this.attachSymptomListeners();
        
        // Animate in
        container.querySelectorAll('.symptom-card').forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 50);
        });
    }
    
    attachSymptomListeners() {
        // Checkbox change listeners
        document.querySelectorAll('.symptom-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const symptomId = e.target.id.replace('symptom-', '');
                this.toggleSymptom(symptomId, e.target.checked);
            });
        });
        
        // CF input listeners
        document.querySelectorAll('.cf-input').forEach(input => {
            input.addEventListener('change', (e) => {
                const symptomId = e.target.id.replace('cf-', '');
                this.updateSymptomCF(symptomId, e.target.value);
            });
            
            input.addEventListener('blur', (e) => {
                this.validateCFInput(e.target);
            });
        });
        
        // Card click listeners
        document.querySelectorAll('.symptom-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (e.target.type !== 'checkbox' && e.target.type !== 'number') {
                    const checkbox = card.querySelector('.symptom-checkbox');
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change'));
                }
            });
        });
    }
    
    toggleSymptom(symptomId, selected) {
        const card = document.querySelector(`[data-symptom="${symptomId}"]`);
        const cfInput = document.getElementById(`cf-${symptomId}`);
        
        if (selected) {
            const cfValue = parseFloat(cfInput.value) || CONFIG.CF_DEFAULT;
            this.selectedSymptoms[symptomId] = cfValue;
            card.classList.add('selected');
            cfInput.disabled = false;
            cfInput.focus();
        } else {
            delete this.selectedSymptoms[symptomId];
            card.classList.remove('selected');
            cfInput.disabled = true;
            cfInput.value = CONFIG.CF_DEFAULT;
        }
        
        this.updateSelectedSummary();
    }
    
    updateSymptomCF(symptomId, cfValue) {
        const cf = parseFloat(cfValue);
        if (utils.validateCF(cf) && this.selectedSymptoms[symptomId] !== undefined) {
            this.selectedSymptoms[symptomId] = cf;
            this.updateSelectedSummary();
        }
    }
    
    validateCFInput(input) {
        const cf = parseFloat(input.value);
        if (!utils.validateCF(cf)) {
            input.classList.add('is-invalid');
            toast.warning(`CF harus antara ${CONFIG.CF_MIN} dan ${CONFIG.CF_MAX}`);
            input.value = CONFIG.CF_DEFAULT;
        } else {
            input.classList.remove('is-invalid');
        }
    }
    
    updateSelectedSummary() {
        const selectedContainer = document.getElementById('selected-symptoms');
        const selectedList = document.getElementById('selected-list');
        
        if (Object.keys(this.selectedSymptoms).length === 0) {
            selectedContainer.style.display = 'none';
            return;
        }
        
        selectedContainer.style.display = 'block';
        
        const badgesHtml = Object.entries(this.selectedSymptoms).map(([symptomId, cf]) => {
            const symptom = this.symptoms.find(s => s.id === symptomId);
            const confidence = utils.getConfidenceLevel(cf);
            
            return `
                <span class="badge bg-${confidence.color} me-1 mb-1">
                    ${symptom?.name || symptomId} 
                    <small>(${utils.formatCF(cf)})</small>
                    <button type="button" class="btn-close btn-close-white ms-1" 
                            onclick="diagnosisManager.removeSymptom('${symptomId}')" 
                            aria-label="Remove"></button>
                </span>
            `;
        }).join('');
        
        selectedList.innerHTML = badgesHtml;
    }
    
    removeSymptom(symptomId) {
        const checkbox = document.getElementById(`symptom-${symptomId}`);
        if (checkbox) {
            checkbox.checked = false;
            checkbox.dispatchEvent(new Event('change'));
        }
    }
    
    setupEventListeners() {
        // Form submission
        document.getElementById('diagnosis-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.runDiagnosis();
        });
        
        // Reset button
        document.getElementById('reset-btn').addEventListener('click', () => {
            this.resetForm();
        });
        
        // Trace button
        document.getElementById('show-trace-btn')?.addEventListener('click', () => {
            this.showInferenceTrace();
        });
        
        // Export button
        document.getElementById('export-btn')?.addEventListener('click', () => {
            this.exportResults();
        });
    }
    
    setupSearch() {
        const searchInput = document.getElementById('symptom-search');
        const debouncedSearch = utils.debounce((query) => {
            this.filterSymptoms(query);
        }, 300);
        
        searchInput.addEventListener('input', (e) => {
            debouncedSearch(e.target.value);
        });
    }
    
    filterSymptoms(query) {
        if (!query.trim()) {
            this.renderSymptoms();
            return;
        }
        
        const filtered = this.symptoms.filter(symptom => 
            symptom.name.toLowerCase().includes(query.toLowerCase()) ||
            symptom.description.toLowerCase().includes(query.toLowerCase())
        );
        
        this.renderSymptoms(filtered);
    }
    
    async runDiagnosis() {
        if (Object.keys(this.selectedSymptoms).length === 0) {
            toast.warning('Pilih minimal satu gejala untuk diagnosis');
            return;
        }
        
        // Show loading state
        this.showLoadingState();
        
        try {
            const response = await api.post('/api/diagnose', {
                symptoms: this.selectedSymptoms
            });
            
            if (response.success) {
                this.lastResults = response;
                this.displayResults(response);
                toast.success('Diagnosis berhasil dilakukan');
            } else {
                throw new Error(response.error || 'Diagnosis failed');
            }
        } catch (error) {
            console.error('Diagnosis error:', error);
            this.showErrorState(error.message);
            toast.error('Gagal melakukan diagnosis: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }
    
    showLoadingState() {
        document.getElementById('initial-state').style.display = 'none';
        document.getElementById('loading-state').style.display = 'block';
        document.getElementById('results-container').style.display = 'none';
        document.getElementById('error-state').style.display = 'none';
        
        // Disable diagnosis button
        const diagnoseBtn = document.getElementById('diagnose-btn');
        diagnoseBtn.disabled = true;
        diagnoseBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2"></span>
            Memproses...
        `;
    }
    
    hideLoadingState() {
        document.getElementById('loading-state').style.display = 'none';
        
        // Re-enable diagnosis button
        const diagnoseBtn = document.getElementById('diagnose-btn');
        diagnoseBtn.disabled = false;
        diagnoseBtn.innerHTML = `
            <i class="fas fa-user-md me-2"></i>
            Diagnosa
        `;
    }
    
    showErrorState(message) {
        document.getElementById('initial-state').style.display = 'none';
        document.getElementById('results-container').style.display = 'none';
        document.getElementById('error-state').style.display = 'block';
        document.getElementById('error-message').textContent = message;
    }
    
    displayResults(response) {
        document.getElementById('initial-state').style.display = 'none';
        document.getElementById('error-state').style.display = 'none';
        document.getElementById('results-container').style.display = 'block';
        
        // Input summary
        this.displayInputSummary(response.input_symptoms);
        
        // Main conclusion
        this.displayMainConclusion(response.most_likely_conclusion);
        
        // All results
        this.displayAllResults(response.results);
        
        // Processing info
        this.displayProcessingInfo(response.processing_info, response.fired_rules);
        
        // Animate results
        const resultsContainer = document.getElementById('results-container');
        resultsContainer.classList.add('fade-in-up');
    }
    
    displayInputSummary(inputSymptoms) {
        const container = document.getElementById('input-summary');
        
        const symptomsHtml = Object.entries(inputSymptoms).map(([symptomId, data]) => {
            const confidence = utils.getConfidenceLevel(data.cf);
            return `
                <span class="badge bg-${confidence.color} me-1 mb-1">
                    ${data.display_name} <small>(CF: ${utils.formatCF(data.cf)})</small>
                </span>
            `;
        }).join('');
        
        container.innerHTML = symptomsHtml;
    }
    
    displayMainConclusion(conclusion) {
        const container = document.getElementById('main-conclusion');
        
        if (!conclusion) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Tidak dapat menentukan diagnosis utama berdasarkan gejala yang diberikan.
                </div>
            `;
            return;
        }
        
        const confidence = utils.getConfidenceLevel(conclusion.cf);
        
        container.innerHTML = `
            <div class="result-card primary">
                <div class="d-flex align-items-center justify-content-between">
                    <div class="flex-grow-1">
                        <h5 class="mb-2">
                            <i class="fas fa-stethoscope me-2 text-success"></i>
                            Diagnosis Utama
                        </h5>
                        <h4 class="text-success fw-bold">${conclusion.display_name}</h4>
                        <div class="mt-2">
                            <span class="badge badge-cf ${confidence.class}">
                                CF: ${utils.formatCF(conclusion.cf)} (${confidence.level})
                            </span>
                            <span class="badge bg-light text-dark ms-2">
                                ${conclusion.percentage}% Keyakinan
                            </span>
                        </div>
                    </div>
                    <div class="text-end">
                        <div class="progress-ring-container position-relative">
                            <!-- Progress ring akan dibuat di sini -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add progress ring
        const progressContainer = container.querySelector('.progress-ring-container');
        new ProgressRing(progressContainer, conclusion.cf);
    }
    
    displayAllResults(results) {
        const container = document.getElementById('all-results');
        
        if (!results || results.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    Tidak ada diagnosis tambahan yang dapat ditentukan.
                </div>
            `;
            return;
        }
        
        const resultsHtml = results.map((result, index) => {
            const confidence = utils.getConfidenceLevel(result.cf);
            const isMainResult = index === 0;
            
            return `
                <div class="result-card ${isMainResult ? 'primary' : 'secondary'} ${result.cf < 0.3 ? 'low-confidence' : ''}">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <div class="d-flex align-items-center mb-2">
                                <span class="badge bg-light text-dark me-2">#${index + 1}</span>
                                <h6 class="mb-0">${result.display_name}</h6>
                            </div>
                            <div class="d-flex align-items-center gap-2">
                                <span class="badge badge-cf ${confidence.class}">
                                    CF: ${utils.formatCF(result.cf)}
                                </span>
                                <span class="badge bg-${confidence.color}">
                                    ${confidence.level}
                                </span>
                                <small class="text-muted">
                                    ${result.percentage}% Keyakinan
                                </small>
                            </div>
                        </div>
                        <div class="col-md-4 text-end">
                            <div class="progress-ring-container-${index} position-relative d-inline-block">
                                <!-- Progress ring akan dibuat di sini -->
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = resultsHtml;
        
        // Add progress rings untuk setiap result
        results.forEach((result, index) => {
            const progressContainer = container.querySelector(`.progress-ring-container-${index}`);
            if (progressContainer) {
                new ProgressRing(progressContainer, result.cf);
            }
        });
    }
    
    displayProcessingInfo(processingInfo, firedRules) {
        const container = document.getElementById('processing-info');
        
        container.innerHTML = `
            <div class="row g-3">
                <div class="col-md-3">
                    <div class="text-center p-2 bg-light rounded">
                        <div class="h5 text-primary mb-1">${processingInfo.total_rules_available}</div>
                        <small class="text-muted">Total Rules</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center p-2 bg-light rounded">
                        <div class="h5 text-success mb-1">${processingInfo.rules_fired}</div>
                        <small class="text-muted">Rules Digunakan</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center p-2 bg-light rounded">
                        <div class="h5 text-warning mb-1">${processingInfo.facts_derived}</div>
                        <small class="text-muted">Fakta Diturunkan</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center p-2 bg-light rounded">
                        <div class="h5 text-info mb-1">${Math.round((processingInfo.rules_fired / processingInfo.total_rules_available) * 100)}%</div>
                        <small class="text-muted">Efisiensi</small>
                    </div>
                </div>
            </div>
            
            ${firedRules.length > 0 ? `
                <div class="mt-3">
                    <h6 class="mb-2">Rules yang Digunakan:</h6>
                    <div class="d-flex flex-wrap gap-1">
                        ${firedRules.map(rule => `
                            <span class="badge bg-secondary">${rule}</span>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        `;
    }
    
    async showInferenceTrace() {
        if (!this.lastResults) {
            toast.warning('Lakukan diagnosis terlebih dahulu');
            return;
        }
        
        const modal = new bootstrap.Modal(document.getElementById('traceModal'));
        const content = document.getElementById('trace-content');
        
        const trace = this.lastResults.inference_trace || [];
        
        if (trace.length === 0) {
            content.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    Tidak ada jejak inferensi yang tersedia.
                </div>
            `;
        } else {
            const traceHtml = trace.map((step, index) => {
                const isIteration = step.includes('Iterasi') || step.includes('===');
                const isRule = step.includes('Rule');
                
                return `
                    <div class="trace-step ${isIteration ? 'trace-iteration' : isRule ? 'trace-rule' : ''}">
                        <div class="d-flex align-items-center">
                            <span class="badge bg-light text-dark me-3">${index + 1}</span>
                            <span class="flex-grow-1">${step}</span>
                        </div>
                    </div>
                `;
            }).join('');
            
            content.innerHTML = traceHtml;
        }
        
        modal.show();
    }
    
    exportResults() {
        if (!this.lastResults) {
            toast.warning('Tidak ada hasil untuk di-export');
            return;
        }
        
        // Simple implementation - could be enhanced with PDF generation
        const data = {
            timestamp: new Date().toISOString(),
            input_symptoms: this.lastResults.input_symptoms,
            results: this.lastResults.results,
            most_likely_conclusion: this.lastResults.most_likely_conclusion,
            processing_info: this.lastResults.processing_info
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `diagnosis-result-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        toast.success('Hasil diagnosis berhasil di-export');
    }
    
    resetForm() {
        // Clear selected symptoms
        this.selectedSymptoms = {};
        this.lastResults = null;
        
        // Reset checkboxes and inputs
        document.querySelectorAll('.symptom-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        document.querySelectorAll('.cf-input').forEach(input => {
            input.value = CONFIG.CF_DEFAULT;
            input.disabled = true;
            input.classList.remove('is-invalid');
        });
        
        document.querySelectorAll('.symptom-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Clear search
        document.getElementById('symptom-search').value = '';
        
        // Reset states
        document.getElementById('initial-state').style.display = 'block';
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('results-container').style.display = 'none';
        document.getElementById('error-state').style.display = 'none';
        document.getElementById('selected-symptoms').style.display = 'none';
        
        // Re-render symptoms
        this.renderSymptoms();
        
        toast.info('Form telah direset');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.diagnosisManager = new DiagnosisManager();
});