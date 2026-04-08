/**
 * Rules Page JavaScript
 * Menghandle display dan filtering untuk basis pengetahuan (rules)
 */

class RulesManager {
    constructor() {
        this.rules = [];
        this.filteredRules = [];
        
        this.init();
    }
    
    async init() {
        await this.loadRules();
        this.setupEventListeners();
        this.calculateStatistics();
    }
    
    async loadRules() {
        const container = document.getElementById('rules-container');
        const loading = document.getElementById('rules-loading');
        
        try {
            const response = await api.get('/api/rules');
            if (response.success) {
                this.rules = response.rules;
                this.filteredRules = [...this.rules];
                this.renderRules();
                toast.success(`Berhasil memuat ${this.rules.length} aturan`);
            } else {
                throw new Error('Failed to load rules');
            }
        } catch (error) {
            console.error('Error loading rules:', error);
            utils.showError(container, 'Gagal memuat basis pengetahuan. Silakan refresh halaman.');
            toast.error('Gagal memuat basis pengetahuan');
        } finally {
            if (loading) loading.style.display = 'none';
        }
    }
    
    renderRules() {
        const container = document.getElementById('rules-container');
        
        if (this.filteredRules.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-search text-muted" style="font-size: 4rem;"></i>
                    <h4 class="text-muted mt-3">Tidak ada aturan yang ditemukan</h4>
                    <p class="text-muted">Coba ubah filter atau kata kunci pencarian</p>
                </div>
            `;
            return;
        }
        
        const rulesHtml = this.filteredRules.map((rule, index) => {
            const confidence = utils.getConfidenceLevel(rule.cf);
            const ruleType = this.determineRuleType(rule);
            
            return `
                <div class="card mb-3 rule-card" data-rule-id="${rule.id}" style="animation-delay: ${index * 100}ms">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                            <h5 class="mb-0">
                                <span class="badge bg-primary me-2">${rule.id}</span>
                                ${this.getRuleTypeIcon(ruleType)}
                                <span class="rule-type-badge badge bg-${this.getRuleTypeColor(ruleType)} ms-2">
                                    ${ruleType}
                                </span>
                            </h5>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <span class="badge badge-cf ${confidence.class}">
                                CF: ${utils.formatCF(rule.cf)}
                            </span>
                            <button class="btn btn-outline-info btn-sm" onclick="rulesManager.showRuleDetail('${rule.id}')">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                    </div>
                    
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-5">
                                <h6 class="text-muted mb-2">
                                    <i class="fas fa-list-ul me-1"></i>
                                    Premis (IF):
                                </h6>
                                <div class="premises">
                                    ${rule.premises.map((premise, i) => `
                                        <span class="badge bg-light text-dark me-1 mb-1">
                                            ${premise}
                                        </span>
                                        ${i < rule.premises.length - 1 ? '<small class="text-muted">AND</small>' : ''}
                                    `).join('')}
                                </div>
                            </div>
                            
                            <div class="col-md-1 text-center">
                                <div class="arrow-separator">
                                    <i class="fas fa-arrow-right text-primary" style="font-size: 1.5rem;"></i>
                                </div>
                            </div>
                            
                            <div class="col-md-6">
                                <h6 class="text-muted mb-2">
                                    <i class="fas fa-bullseye me-1"></i>
                                    Kesimpulan (THEN):
                                </h6>
                                <div class="conclusion">
                                    <span class="badge bg-success text-white fs-6 p-2">
                                        ${rule.conclusion}
                                    </span>
                                </div>
                                
                                <div class="mt-3">
                                    <small class="text-muted">
                                        <i class="fas fa-info-circle me-1"></i>
                                        ${rule.description}
                                    </small>
                                </div>
                            </div>
                        </div>
                        
                        <!-- CF Visualization -->
                        <div class="mt-3">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <label class="form-label small text-muted mb-1">Tingkat Keyakinan:</label>
                                    <div class="progress" style="height: 8px;">
                                        <div class="progress-bar bg-${confidence.color}" 
                                             role="progressbar" 
                                             style="width: ${rule.cf * 100}%">
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4 text-end">
                                    <span class="badge bg-${confidence.color} fs-6">
                                        ${confidence.level} (${Math.round(rule.cf * 100)}%)
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = rulesHtml;
        
        // Animate cards
        setTimeout(() => {
            document.querySelectorAll('.rule-card').forEach(card => {
                card.classList.add('fade-in-up');
            });
        }, 100);
    }
    
    determineRuleType(rule) {
        // Check if any premise is a conclusion from other rules
        const allConclusions = this.rules.map(r => r.conclusion);
        const hasSequentialPremise = rule.premises.some(premise => 
            allConclusions.includes(premise.replace(/\s/g, '_').toLowerCase())
        );
        
        if (hasSequentialPremise) {
            return 'Sekuensial';
        }
        
        // Check if this conclusion appears in other rules (parallel)
        const sameConclusions = this.rules.filter(r => r.conclusion === rule.conclusion);
        if (sameConclusions.length > 1) {
            return 'Paralel';
        }
        
        return 'Dasar';
    }
    
    getRuleTypeIcon(ruleType) {
        switch (ruleType) {
            case 'Sekuensial':
                return '<i class="fas fa-arrows-alt-h text-success me-1"></i>';
            case 'Paralel':
                return '<i class="fas fa-code-branch text-warning me-1"></i>';
            default:
                return '<i class="fas fa-circle text-info me-1"></i>';
        }
    }
    
    getRuleTypeColor(ruleType) {
        switch (ruleType) {
            case 'Sekuensial':
                return 'success';
            case 'Paralel':
                return 'warning';
            default:
                return 'info';
        }
    }
    
    calculateStatistics() {
        const totalRules = this.rules.length;
        const sequentialRules = this.rules.filter(rule => this.determineRuleType(rule) === 'Sekuensial').length;
        const parallelRules = this.rules.filter(rule => this.determineRuleType(rule) === 'Paralel').length;
        const avgCF = this.rules.reduce((sum, rule) => sum + rule.cf, 0) / totalRules;
        
        // Update statistics cards
        document.getElementById('total-rules').textContent = totalRules;
        document.getElementById('sequential-rules').textContent = sequentialRules;
        document.getElementById('parallel-rules').textContent = parallelRules;
        document.getElementById('avg-cf').textContent = avgCF.toFixed(2);
    }
    
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('rules-search');
        const debouncedSearch = utils.debounce((query) => {
            this.filterRules();
        }, 300);
        
        searchInput.addEventListener('input', debouncedSearch);
        
        // CF filter
        document.getElementById('cf-filter').addEventListener('change', () => {
            this.filterRules();
        });
        
        // Type filter
        document.getElementById('type-filter').addEventListener('change', () => {
            this.filterRules();
        });
    }
    
    filterRules() {
        const searchQuery = document.getElementById('rules-search').value.toLowerCase();
        const cfFilter = document.getElementById('cf-filter').value;
        const typeFilter = document.getElementById('type-filter').value;
        
        this.filteredRules = this.rules.filter(rule => {
            // Search filter
            const matchesSearch = !searchQuery || 
                rule.id.toLowerCase().includes(searchQuery) ||
                rule.premises.some(p => p.toLowerCase().includes(searchQuery)) ||
                rule.conclusion.toLowerCase().includes(searchQuery) ||
                rule.description.toLowerCase().includes(searchQuery);
            
            // CF filter
            let matchesCF = true;
            if (cfFilter === 'high') {
                matchesCF = rule.cf >= 0.8;
            } else if (cfFilter === 'medium') {
                matchesCF = rule.cf >= 0.6 && rule.cf < 0.8;
            } else if (cfFilter === 'low') {
                matchesCF = rule.cf < 0.6;
            }
            
            // Type filter
            let matchesType = true;
            if (typeFilter) {
                const ruleType = this.determineRuleType(rule);
                if (typeFilter === 'sequential') {
                    matchesType = ruleType === 'Sekuensial';
                } else if (typeFilter === 'parallel') {
                    matchesType = ruleType === 'Paralel';
                } else if (typeFilter === 'basic') {
                    matchesType = ruleType === 'Dasar';
                }
            }
            
            return matchesSearch && matchesCF && matchesType;
        });
        
        this.renderRules();
        
        // Update filtered count
        const totalFiltered = this.filteredRules.length;
        const totalAll = this.rules.length;
        
        if (totalFiltered !== totalAll) {
            toast.info(`Menampilkan ${totalFiltered} dari ${totalAll} aturan`);
        }
    }
    
    showRuleDetail(ruleId) {
        const rule = this.rules.find(r => r.id === ruleId);
        if (!rule) return;
        
        const modal = new bootstrap.Modal(document.getElementById('ruleDetailModal'));
        const content = document.getElementById('rule-detail-content');
        
        const confidence = utils.getConfidenceLevel(rule.cf);
        const ruleType = this.determineRuleType(rule);
        
        // Find related rules
        const relatedRules = this.findRelatedRules(rule);
        
        content.innerHTML = `
            <div class="rule-detail">
                <div class="row mb-4">
                    <div class="col-md-8">
                        <h4>
                            <span class="badge bg-primary me-2">${rule.id}</span>
                            ${rule.conclusion}
                        </h4>
                        <div class="mt-2">
                            <span class="badge bg-${this.getRuleTypeColor(ruleType)}">
                                ${this.getRuleTypeIcon(ruleType)} ${ruleType}
                            </span>
                            <span class="badge badge-cf ${confidence.class} ms-2">
                                CF: ${utils.formatCF(rule.cf)} (${confidence.level})
                            </span>
                        </div>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="progress-ring-detail position-relative d-inline-block">
                            <!-- Progress ring akan dibuat di sini -->
                        </div>
                    </div>
                </div>
                
                <div class="rule-structure mb-4">
                    <h6 class="border-bottom pb-2">Struktur Aturan</h6>
                    <div class="bg-light p-3 rounded">
                        <div class="mb-2">
                            <strong>IF:</strong> ${rule.premises.join(' AND ')}
                        </div>
                        <div>
                            <strong>THEN:</strong> ${rule.conclusion} 
                            <small class="text-muted">(CF: ${utils.formatCF(rule.cf)})</small>
                        </div>
                    </div>
                </div>
                
                <div class="rule-description mb-4">
                    <h6 class="border-bottom pb-2">Deskripsi</h6>
                    <p>${rule.description}</p>
                </div>
                
                ${relatedRules.length > 0 ? `
                    <div class="related-rules mb-4">
                        <h6 class="border-bottom pb-2">Aturan Terkait</h6>
                        <div class="row g-2">
                            ${relatedRules.map(relatedRule => `
                                <div class="col-md-6">
                                    <div class="card border-secondary">
                                        <div class="card-body p-2">
                                            <div class="d-flex justify-content-between align-items-center">
                                                <span class="badge bg-secondary">${relatedRule.id}</span>
                                                <small class="text-muted">CF: ${utils.formatCF(relatedRule.cf)}</small>
                                            </div>
                                            <small class="d-block mt-1">${relatedRule.conclusion}</small>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div class="cf-analysis">
                    <h6 class="border-bottom pb-2">Analisis Certainty Factor</h6>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body text-center">
                                    <h5 class="text-${confidence.color}">${Math.round(rule.cf * 100)}%</h5>
                                    <small class="text-muted">Tingkat Keyakinan</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body text-center">
                                    <h5 class="text-info">${confidence.level}</h5>
                                    <small class="text-muted">Kategori Keyakinan</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-${confidence.color}" 
                                 style="width: ${rule.cf * 100}%">
                                <small class="fw-bold">${Math.round(rule.cf * 100)}%</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add progress ring
        const progressContainer = content.querySelector('.progress-ring-detail');
        new ProgressRing(progressContainer, rule.cf);
        
        modal.show();
    }
    
    findRelatedRules(rule) {
        return this.rules.filter(r => {
            if (r.id === rule.id) return false;
            
            // Rules that share premises or conclusions
            const sharesPremise = r.premises.some(p => rule.premises.includes(p));
            const sharesConclusion = r.conclusion === rule.conclusion;
            const premiseIsConclusion = rule.premises.includes(r.conclusion);
            const conclusionIsPremise = r.premises.includes(rule.conclusion);
            
            return sharesPremise || sharesConclusion || premiseIsConclusion || conclusionIsPremise;
        }).slice(0, 6); // Limit to 6 related rules
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.rulesManager = new RulesManager();
});