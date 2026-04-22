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
        
        stage('SonarQube analysis') {
            steps {
                // Pastikan 'sonar-token-id' adalah ID yang Anda buat di Manage Jenkins > Credentials
                withCredentials([string(credentialsId: 'sonarqube-token-id', variable: 'AUTH_TOKEN')]) {
                    script {
                // Sekarang BUILD_USER_ID sudah tersedia di dalam blok ini
                def user = env.BUILD_USER_ID ?: "System/SCM"
                def scannerHome = tool 'SonarScanner'
                
                withSonarQubeEnv('SonarQube') {
                    sh """
                    sonar-scanner \
                    -Dsonar.projectKey=jenkins-test \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=http://sonarqube:9000 \
                    -Dsonar.token=${AUTH_TOKEN} \
                    - Dsonar.login=${AUTH_TOKEN} \
                    -Dsonar.analysis.buildUser=${user}
                    """
                }
            }
        }
            }
        }

        stage('Code Quality') {
            parallel {
                stage('Black Format') {
                    steps {
                        script {
                            echo "✨ Checking code format (Black)..."
                            def status = sh(script: ". ${VENV_DIR}/bin/activate && black --check .", returnStatus: true)
                            if (status != 0) {
                                echo "❌ Black: Formatting issues detected."
                                currentBuild.result = 'UNSTABLE'
                            }
                        }
                    }
                }
                stage('Flake8 Lint') {
                    steps {
                        script {
                            echo "🔍 Running linting (Flake8)..."
                            def status = sh(
                                script: ". ${VENV_DIR}/bin/activate && flake8 . --format=default > reports/flake8-report.txt || true",
                                returnStatus: true
                            )
                            if (status != 0) {
                                echo "❌ Flake8: Code smells detected."
                                currentBuild.result = 'UNSTABLE'
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
                    def status = sh(script: """
                        . ${VENV_DIR}/bin/activate
                        pytest tests/test_inference.py -v --tb=short \
                            --junitxml=reports/junit.xml \
                            --cov=inference_engine \
                            --cov-report=xml:reports/coverage.xml \
                            --cov-report=term-missing
                    """, returnStatus: true)
                    
                    if (status != 0) {
                        echo "❌ Unit Tests: Logic failure detected."
                        error("Unit tests failed")
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
                        echo "❌ Integration Tests: API/Connectivity failure."
                        error("Integration tests failed")
                    }
                }
            }
        }
    }

    post {
        always {
            junit 'reports/*.xml'
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        failure {
            script {
                echo "❌ Pipeline failed! Notifying n8n..."
                notifyN8N()
            }
        }
        unstable {
            script {
                echo "⚠️ Pipeline is unstable. Notifying n8n..."
                notifyN8N()
            }
        }
    }
}
