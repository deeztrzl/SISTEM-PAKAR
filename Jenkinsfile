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
                    checkout scm // Kalau ini gagal, langsung stop (pantas).
                }
            }
        }
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
                        
                        # FAKTA: Folder reports wajib dibuat di sini sebelum linting atau test berjalan
                        mkdir -p reports
                    '''
                }
                    steps {
                        script {
                            echo "✨ Checking code format (Black)..."
                            sh '''
                                . ${VENV_DIR}/bin/activate
                                black --check .
                            '''
                            def status = sh(script: ". ${VENV_DIR}/bin/activate && black --check .", returnStatus: true)
                            if (status != 0) {
                                echo "❌ Black: Kode lo berantakan, tolong dirapiin!"
                                currentBuild.result = 'FAILURE'
                            }
                        }
                    }
                }
                    steps {
                        script {
                            echo "🔍 Running linting (Flake8)..."
                            
                            // Simpan status exit code tanpa mematikan stage
                            def status = sh(
                                script: """
                                    . ${VENV_DIR}/bin/activate
                                    flake8 . --format=json > reports/flake8-report.json
                                """,
                                returnStatus: true
                            )

                            // Cek apakah ada error
                            def status = sh(script: ". ${VENV_DIR}/bin/activate && flake8 . --format=json > reports/flake8-report.json", returnStatus: true)
                            if (status != 0) {
                                echo "❌ Flake8 nemu dosa di kode lo!"
                                // Kita set hasil build jadi FAILURE tapi stage ini kelar dulu
                                echo "❌ Flake8: Ada bau busuk di kode lo (Code Smell)!"
                                currentBuild.result = 'FAILURE'
                            } else {
                                echo "✅ Kode bersih, mantap!"
                            }
                            
                            // Di sini lo bisa lanjutin bikin payload n8n pake file flake8-report.json
                        }
                    }
                }
            steps {
                script {
                    echo "🧪 Running unit tests..."
                    sh '''
                    // Biarkan pytest jalan sampai habis buat dapet junit.xml
                    def status = sh(script: """
                        . ${VENV_DIR}/bin/activate
                        pytest tests/test_inference.py -v --tb=short \
                            --junitxml=reports/junit.xml \
                            --cov=inference_engine \
                            --cov-report=html:coverage-report \
                            --cov-report=xml:reports/coverage.xml \
                            --cov-report=term-missing
                    '''
                            --cov-report=xml:reports/coverage.xml
                    """, returnStatus: true)
                    
                    if (status != 0) {
                        echo "❌ Unit Tests: Ada logic yang meledak!"
                        currentBuild.result = 'FAILURE'
                    }
                }
            }
        }
            steps {
                script {
                    echo "🔗 Running integration tests..."
                    sh '''
                    def status = sh(script: """
                        . ${VENV_DIR}/bin/activate
                        pytest tests/test_api.py -v --tb=short \
                            --junitxml=reports/integration-tests.xml
                    '''
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
        success {
            script {
                echo "✅ Pipeline completed successfully!"
            }
        always {
            // FAKTA: Arsipkan laporan supaya lo bisa liat di UI Jenkins
            junit 'reports/*.xml'
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
                echo "❌ Pipeline failed! Nembak n8n..."
                // notifyN8N() bakal dapet paket lengkap dari semua dosa di atas
                notifyN8N() 
            }
        }
    }
}
}
