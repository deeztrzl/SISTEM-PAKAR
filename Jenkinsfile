import groovy.json.JsonOutput

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
        
        // Hostname menggunakan nama container n8n di docker network
        N8N_BURP_WEBHOOK    = 'http://n8n:5678/webhook/29618a6e-webhook-burpsuite'
        N8N_SONAR_WEBHOOK   = 'http://n8n:5678/webhook/sonarqube-trigger'
        // Tambahkan webhook khusus untuk error reporting
        N8N_FAILURE_WEBHOOK = 'http://n8n:5678/webhook/pipeline-failure' 
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
                withCredentials([string(credentialsId: 'sonarqube-token-id', variable: 'AUTH_TOKEN')]) {
                    wrap([$class: 'BuildUser']) {
                        script {
                            def scannerHome = tool 'SonarScanner'
                            def user = env.BUILD_USER_ID ?: "System/SCM"
        
                            withSonarQubeEnv('sonar-server') {
                                sh """
                                ${scannerHome}/bin/sonar-scanner \
                                -Dsonar.projectKey=jenkins-test \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=http://sonarqube:9000 \
                                -Dsonar.token=${AUTH_TOKEN} \
                                -Dsonar.analysis.buildUser=${user}
                                """
                            }
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

        stage('Trigger Downstream Webhooks') {
            steps {
                script {
                    echo "🚀 Firing downstream success webhooks to n8n..."
                    parallel(
                        "BurpSuite Trigger": {
                            sh """
                            curl -X POST -sS --fail --max-time 10 ${N8N_BURP_WEBHOOK} \
                                 -H "Content-Type: application/json" \
                                 -d '{"build_number": "${env.BUILD_NUMBER}", "project": "jenkins-test", "action": "trigger_dast"}'
                            """
                        },
                        "SonarQube Trigger": {
                            sh """
                            curl -X POST -sS --fail --max-time 10 ${N8N_SONAR_WEBHOOK} \
                                 -H "Content-Type: application/json" \
                                 -d '{"build_number": "${env.BUILD_NUMBER}", "project": "jenkins-test", "action": "process_sonar"}'
                            """
                        }
                    )
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
                echo "❌ Pipeline failed! Compiling logs and notifying n8n..."
                
                def jobName = env.JOB_NAME
                def buildId = env.BUILD_ID
                def buildUrl = env.BUILD_URL
                
                // Ambil 1500 baris terakhir, pastikan di Jenkins in-process script approval sudah di-allow
                def logLines = currentBuild.rawBuild.getLog(1500)
                def logCount = logLines.size()
                def start = logCount > 800 ? logCount - 800 : 0
                def combinedLog = logLines.subList(start, logCount).join('\n')
                
                def payloadData = [
                    "status": "failed",
                    "job_name": jobName,
                    "build_id": buildId,
                    "url": buildUrl,
                    "pipeline_log": combinedLog
                ]
                
                def jsonString = JsonOutput.toJson(payloadData)
                writeFile file: 'n8n_payload.json', text: jsonString

                // Kirim payload dengan argument -d @filename untuk membaca file JSON
                sh """
                curl -X POST -sS --max-time 15 ${N8N_FAILURE_WEBHOOK} \
                     -H "Content-Type: application/json" \
                     -d @n8n_payload.json
                """
            }
        }
        unstable {
            script {
                echo "⚠️ Pipeline is unstable. Check SonarQube or formatting logs."
                // Implementasi webhook unstable dapat ditambahkan di sini jika dibutuhkan
            }
        }
    }
}
