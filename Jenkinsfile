pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    environment {
        APP_NAME = 'medical-expert-system'
        DOCKER_REGISTRY = 'docker.io'  // Ubah sesuai registry Anda
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
                    '''
                }
            }
        }
        
        stage('Code Quality') {
            parallel {
                stage('Linting') {
                    steps {
                        script {
                            echo "🔍 Running code style checks..."
                            sh '''
                                . ${VENV_DIR}/bin/activate
                                pylint **/*.py --disable=R,C --exit-zero > reports/lint-report.txt || true
                                flake8 --format=json > reports/flake8-report.json || true
                            '''
                        }
                    }
                }
                
                stage('Code Format') {
                    steps {
                        script {
                            echo "✨ Checking code format..."
                            sh '''
                                . ${VENV_DIR}/bin/activate
                                black --check . || true
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
                        mkdir -p reports
                        pytest tests/test_inference.py -v --tb=short \
                            --junitxml=reports/junit.xml \
                            --cov=inference_engine \
                            --cov-report=html:coverage-report \
                            --cov-report=xml:reports/coverage.xml \
                            --cov-report=term-missing || true
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
                            --junitxml=reports/integration-tests.xml || true
                    '''
                }
            }
        }
        
        stage('API Smoke Test') {
            steps {
                script {
                    echo "🚀 Starting API for smoke testing..."
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        timeout 30 python simple_server.py &
                        sleep 5
                        curl -f http://localhost:5000/api/status || exit 1
                    '''
                }
            }
        }
        
        stage('Security Scanning') {
            steps {
                script {
                    echo "🛡️ Running security checks..."
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        pip install bandit
                        bandit -r . -f json -o reports/bandit-report.json || true
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🐳 Building Docker image..."
                    sh '''
                        docker build -t ${APP_NAME}:${BUILD_NUMBER} \
                                   -t ${APP_NAME}:latest .
                        docker tag ${APP_NAME}:latest ${DOCKER_REGISTRY}/${APP_NAME}:${BUILD_NUMBER}
                    '''
                }
            }
        }
        
        stage('Push Docker Image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "📤 Pushing Docker image..."
                    sh '''
                        docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD} ${DOCKER_REGISTRY}
                        docker push ${DOCKER_REGISTRY}/${APP_NAME}:${BUILD_NUMBER}
                        docker push ${DOCKER_REGISTRY}/${APP_NAME}:latest
                    '''
                }
            }
        }
        
        stage('Deploy Staging') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🚀 Deploying to staging..."
                    sh './scripts/deploy-staging.sh'
                }
            }
        }
        
        stage('Performance Test') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "⚡ Running performance tests..."
                    sh '''
                        . ${VENV_DIR}/bin/activate
                        pytest tests/test_performance.py -v --tb=short || true
                    '''
                }
            }
        }
        
        stage('Deploy Production') {
            when {
                branch 'main'
                tag "v*.*.*"
            }
            steps {
                script {
                    echo "🎯 Deploying to production..."
                    sh './scripts/deploy-prod.sh'
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "📊 Publishing reports..."
                
                // Junit test reports
                junit testResults: 'reports/**/*.xml', allowEmptyResults: true
                
                // Coverage reports
                publishHTML([
                    reportDir: 'coverage-report',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true
                ])
                
                // Archive artifacts
                archiveArtifacts artifacts: 'reports/**/*,coverage-report/**/*', 
                                 allowEmptyArchive: true
                
                // Cleanup
                cleanWs(
                    deleteDirs: true,
                    patterns: [
                        [pattern: '.venv', type: 'INCLUDE'],
                        [pattern: '__pycache__', type: 'INCLUDE'],
                        [pattern: '.pytest_cache', type: 'INCLUDE']
                    ]
                )
            }
        }
        
        success {
            script {
                echo "✅ Pipeline completed successfully!"
                // Opsional: Kirim notifikasi
                // emailext(
                //     subject: "Build Success: ${APP_NAME}",
                //     body: "The build ${BUILD_NUMBER} was successful.",
                //     to: 'team@example.com'
                // )
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline failed!"
                // Opsional: Kirim notifikasi
                // emailext(
                //     subject: "Build Failed: ${APP_NAME}",
                //     body: "The build ${BUILD_NUMBER} failed. Check logs: ${BUILD_URL}",
                //     to: 'team@example.com'
                // )
            }
        }
        
        unstable {
            script {
                echo "⚠️ Pipeline is unstable (tests passed but other issues detected)"
            }
        }
    }
}
