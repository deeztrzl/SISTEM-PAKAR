import groovy.json.JsonOutput

@Library('my-local-lib') _

pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds() // Praktik enterprise untuk menghindari bentrok state
    }

    environment {
        PYTHON_VERSION = '3.9'
        VENV_DIR = '.venv'
        
        // Praktik terbaik: Pindahkan URL ini ke Global/Folder properties jika memungkinkan
        N8N_BURP_WEBHOOK    = 'http://n8n_app:5678/webhook/29618a6e-webhook-burpsuite'
        N8N_SONAR_WEBHOOK   = 'http://n8n_app:5678/webhook/sonarqube-trigger'
        N8N_FAILURE_WEBHOOK = 'http://n8n:5678/webhook/pipeline-failure' 
    }

    stages {
        stage('Checkout') {
            steps {
                echo "📦 Checking out repository..."
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                // Eksekusi shell statis dengan single quotes
                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip setuptools wheel
                    .venv/bin/pip install -r requirements.txt
                    .venv/bin/pip install pytest pytest-cov pylint black flake8
                    mkdir -p reports
                '''
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                wrap([$class: 'BuildUser']) {
                    script {
                        def scannerHome = tool 'SonarScanner'
                        def user = env.BUILD_USER_ID ?: "System"
                        
                        // Injeksi scannerHome ke PATH environment agar tidak perlu interpolasi Groovy di dalam sh
                        withEnv(["PATH+SONAR=${scannerHome}/bin"]) {
                            withSonarQubeEnv('sonar-server') {
                                // Eksekusi 100% aman: menggunakan single quotes ('), tidak ada variabel Groovy yang terekspos.
                                // URL dan Token diurus sepenuhnya oleh plugin withSonarQubeEnv.
                                sh '''
                                    sonar-scanner \
                                    -Dsonar.projectKey=jenkins-test \
                                    -Dsonar.sources=.
                                '''
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
                        echo "✨ Checking code format (Black)..."
                        script {
                            // Pemanggilan langsung ke binary venv tanpa activate
                            def status = sh(script: ".venv/bin/black --check .", returnStatus: true)
                            if (status != 0) {
                                currentBuild.result = 'UNSTABLE'
                            }
                        }
                    }
                }
                stage('Flake8 Lint') {
                    steps {
                        echo "🔍 Running linting (Flake8)..."
                        script {
                            def status = sh(
                                script: ".venv/bin/flake8 . --format=default > reports/flake8-report.txt || true",
                                returnStatus: true
                            )
                            if (status != 0) {
                                currentBuild.result = 'UNSTABLE'
                            }
                        }
                    }
                }
            }
        }

        stage('Unit Tests') {
            steps {
                echo "🧪 Running unit tests..."
                sh '''
                    .venv/bin/pytest tests/test_inference.py -v --tb=short \
                        --junitxml=reports/junit.xml \
                        --cov=inference_engine \
                        --cov-report=xml:reports/coverage.xml \
                        --cov-report=term-missing
                '''
            }
        }

        stage('Integration Tests') {
            steps {
                echo "🔗 Running integration tests..."
                sh '''
                    .venv/bin/pytest tests/test_api.py -v --tb=short \
                        --junitxml=reports/integration-tests.xml
                '''
            }
        }

        stage('Trigger Downstream Webhooks') {
            steps {
                echo "🚀 Firing downstream success webhooks to n8n..."
                parallel(
                    "BurpSuite Trigger": {
                        // Interpolasi shell standar
                        sh """
                            curl -X POST -sS --fail --max-time 10 ${N8N_BURP_WEBHOOK} \
                                 -H "Content-Type: application/json" \
                                 -d '{"build_number": "${BUILD_NUMBER}", "project": "jenkins-test", "action": "trigger_dast"}'
                        """
                    },
                    "SonarQube Trigger": {
                        sh """
                            curl -X POST -sS --fail --max-time 10 ${N8N_SONAR_WEBHOOK} \
                                 -H "Content-Type: application/json" \
                                 -d '{"build_number": "${BUILD_NUMBER}", "project": "jenkins-test", "action": "process_sonar"}'
                        """
                    }
                )
            }
        }
    }

    post {
        always {
            junit testResults: 'reports/*.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        failure {
            script {
                echo "❌ Pipeline failed! Notifying n8n to fetch logs..."
                
                // Arsitektur yang benar: Kirim metadata, biarkan n8n memanggil Jenkins REST API
                // n8n harus melakukan GET ke ${BUILD_URL}/consoleText menggunakan Jenkins API Token
                def payloadData = [
                    "status": "failed",
                    "job_name": env.JOB_NAME,
                    "build_id": env.BUILD_ID,
                    "url": env.BUILD_URL,
                    "log_api_url": "${env.BUILD_URL}consoleText"
                ]
                
                writeFile file: 'n8n_payload.json', text: JsonOutput.toJson(payloadData)

                sh """
                    curl -X POST -sS --max-time 15 ${N8N_FAILURE_WEBHOOK} \
                         -H "Content-Type: application/json" \
                         -d @n8n_payload.json
                """
            }
        }
        unstable {
            echo "⚠️ Pipeline is unstable. Check SonarQube or formatting logs."
        }
    }
}
