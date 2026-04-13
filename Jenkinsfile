@Library('my-local-lib') _

pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'registry.internal.company/bpjs-flask-web'
        DOCKER_CREDENTIALS_ID = 'dockerhub-credentials'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Knowledge Base Integrity Check') {
            steps {
                // Fakta: Satu tanda kutip yang hilang pada JSON akan merusak aplikasi Flask. 
                // Tahap ini memvalidasi seluruh berkas JSON sebelum diproses lebih lanjut.
                # Validasi spesifik pada file yang relevan saja
                echo "Memvalidasi sintaks JSON..."
                python3 -m json.tool "./rules.json" > /dev/null || exit 1
                echo "Integritas JSON Knowledge Base terverifikasi."
            }
        }

        stage('Backend: Flask Testing & Linting') {
            steps {
                // Menyiapkan environment Python dan menjalankan pengujian
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                
                # Memeriksa standar kode Python (mencegah syntax error fatal)
                pip install flake8 pytest
                flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                
                # Menjalankan unit test aplikasi Flask
                pytest tests/
                '''
            }
        }

        stage('Build Flask Docker Image') {
            steps {
                script {
                    // Dockerfile harus sudah dikonfigurasi untuk menjalankan Gunicorn/Waitress, bukan Flask Development Server
                    appImage = docker.build("${DOCKER_IMAGE}:${env.BUILD_NUMBER}", "-f Dockerfile .")
                }
            }
        }

        stage('Security Vulnerability Scan (Trivy)') {
            steps {
                // Memindai base image Python dari celah keamanan
                sh "trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE}:${env.BUILD_NUMBER}"
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
