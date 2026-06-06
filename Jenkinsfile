import groovy.json.JsonOutput

@Library('my-local-lib') _

pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        PYTHON_VERSION = '3.9'
        VENV_DIR = '.venv'
        
        N8N_BURP_WEBHOOK    = 'http://n8n_app:5678/webhook/29618a6e-webhook-burpsuite'
        N8N_SONAR_WEBHOOK   = 'http://n8n_app:5678/webhook/sonarqube-trigger'
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
                        
                        withEnv(["PATH+SONAR=${scannerHome}/bin"]) {
                            withSonarQubeEnv('sonar-server') {
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
            parallel {
                stage('BurpSuite Trigger') {
                    steps {
                        echo "🚀 Firing BurpSuite webhook to n8n..."
                        sh """
                            curl -X POST -sS --fail --max-time 10 ${N8N_BURP_WEBHOOK} \
                                 -H "Content-Type: application/json" \
                                 -d '{"build_number": "${BUILD_NUMBER}", "project": "jenkins-test", "action": "trigger_dast"}'
                        """
                    }
                }
                stage('SonarQube Trigger') {
                    steps {
                        echo "🚀 Firing SonarQube webhook to n8n..."
                        sh """
                            curl -X POST -sS --fail --max-time 10 ${N8N_SONAR_WEBHOOK} \
                                 -H "Content-Type: application/json" \
                                 -d '{"build_number": "${BUILD_NUMBER}", "project": "jenkins-test", "action": "process_sonar"}'
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            junit testResults: 'reports/*.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        unstable {
            echo "⚠️ Pipeline is unstable. Check SonarQube or formatting logs."
        }
    }
}
