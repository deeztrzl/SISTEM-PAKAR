// GANTI 'nama-library-lu' dengan nama persis yang lu isi di kolom Name pada konfigurasi Shared Library Jenkins.
// CATATAN: Hapus baris ini JIKA lu sudah mencentang opsi "Load implicitly".
@Library('my-local-lib') _

pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    environment {
        PYTHON_VERSION = '3.9'
        VENV_DIR = '.venv'
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "📦 Checking out repository..."
                    checkout scm
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    echo "🔧 Setting up Python environment..."
                    sh '''
                        python3 -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip setuptools wheel
                        pip install -r requirements.txt
                        pip install pytest pytest-cov pylint black flake8
                        
                        # FAKTA: Folder reports wajib dibuat di sini sebelum linting atau test berjalan
                        mkdir -p reports
                    '''
                }
            }
        }
        
        stage('Code Quality') {
            parallel {
                stage('Code Format') {
                    steps {
                        script {
                            echo "✨ Checking code format (Black)..."
                            sh '''
                                . ${VENV_DIR}/bin/activate
                                black --check .
                            '''
                        }
                    }
                }
                
                stage('Linting') {
                    steps {
                        script {
                            echo "🔍 Running linting (Flake8)..."
                            sh '''
                                . ${VENV_DIR}/bin/activate
                                flake8 . --format=json > reports/flake8-report.json || true
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                script {
                    echo "🧪 Running unit tests..."
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        pytest tests/test_inference.py -v --tb=short \
                            --junitxml=reports/junit.xml \
                            --cov=inference_engine \
                            --cov-report=html:coverage-report \
                            --cov-report=xml:reports/coverage.xml \
                            --cov-report=term-missing
                    '''
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                script {
                    echo "🔗 Running integration tests..."
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        pytest tests/test_api.py -v --tb=short \
                            --junitxml=reports/integration-tests.xml
                    '''
                }
            }
        }
    }
    
    post {
        success {
            script {
                echo "✅ Pipeline completed successfully!"
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline failed!"
                notifyN8N()
            }
        }
        
        unstable {
            script {
                echo "⚠️ Pipeline is unstable (tests passed but other issues detected)"
            }
        }
    }
}
