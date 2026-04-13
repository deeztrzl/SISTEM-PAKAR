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
                    checkout scm // Kalau ini gagal, langsung stop (pantas).
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    echo "🔧 Setting up Python environment..."
                    // Stage ini harus sukses (Blocking). Kalau gagal, library ga ada.
                    sh '''
                        python3 -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip setuptools wheel
                        pip install -r requirements.txt
                        pip install pytest pytest-cov pylint black flake8
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
                            def status = sh(script: ". ${VENV_DIR}/bin/activate && black --check .", returnStatus: true)
                            if (status != 0) {
                                echo "❌ Black: Kode lo berantakan, tolong dirapiin!"
                                currentBuild.result = 'FAILURE'
                            }
                        }
                    }
                }
                
                stage('Linting') {
                    steps {
                        script {
                            echo "🔍 Running linting (Flake8)..."
                            def status = sh(script: ". ${VENV_DIR}/bin/activate && flake8 . --format=json > reports/flake8-report.json", returnStatus: true)
                            if (status != 0) {
                                echo "❌ Flake8: Ada bau busuk di kode lo (Code Smell)!"
                                currentBuild.result = 'FAILURE'
                            }
                        }
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                script {
                    echo "🧪 Running unit tests..."
                    // Biarkan pytest jalan sampai habis buat dapet junit.xml
                    def status = sh(script: """
                        . ${VENV_DIR}/bin/activate
                        pytest tests/test_inference.py -v --tb=short \
                            --junitxml=reports/junit.xml \
                            --cov=inference_engine \
                            --cov-report=xml:reports/coverage.xml
                    """, returnStatus: true)
                    
                    if (status != 0) {
                        echo "❌ Unit Tests: Ada logic yang meledak!"
                        currentBuild.result = 'FAILURE'
                    }
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                script {
                    echo "🔗 Running integration tests..."
                    def status = sh(script: """
                        . ${VENV_DIR}/bin/activate
                        pytest tests/test_api.py -v --tb=short \
                            --junitxml=reports/integration-tests.xml
                    """, returnStatus: true)
                    
                    if (status != 0) {
                        echo "❌ Integration Tests: API atau koneksi bermasalah!"
                        currentBuild.result = 'FAILURE'
                    }
                }
            }
        }
    }
    
    post {
        always {
            // FAKTA: Arsipkan laporan supaya lo bisa liat di UI Jenkins
            junit 'reports/*.xml'
        }
        failure {
            script {
                echo "❌ Pipeline failed! Nembak n8n..."
                // notifyN8N() bakal dapet paket lengkap dari semua dosa di atas
                notifyN8N() 
            }
        }
    }
}