# Jenkins Pipeline Setup Guide
## Setup & Configuration untuk Jenkins CI/CD

### 📋 Prerequisites

1. **Jenkins Server**
   - Jenkins 2.89+
   - Plugins: Pipeline, Docker, Git, Email Extension

2. **Infrastructure**
   - Linux server atau Docker agent
   - Python 3.7+
   - Docker & Docker Compose
   - Git client

3. **Credentials di Jenkins**
   - Docker registry credentials
   - SSH key untuk deployment
   - GitHub/Git credentials (jika diperlukan)

### 🔧 Setup Jenkins

#### 1. Install Required Plugins

```bash
# Di Jenkins Dashboard:
# Manage Jenkins > Manage Plugins > Install

- Pipeline
- Docker Pipeline
- Git
- Email Extension
- Slack Notification (optional)
- Blue Ocean (optional, untuk better UI)
```

#### 2. Create Pipeline Job

```bash
# Di Jenkins:
1. New Item > Pipeline
2. Name: medical-expert-system
3. Pipeline > Definition: Pipeline script from SCM
4. SCM: Git
   Repository URL: https://your-repo/medical-expert-system.git
   Branch: */main
5. Script Path: Jenkinsfile
```

#### 3. Add Credentials

```bash
# Manage Jenkins > Manage Credentials > System > Global Credentials

# Docker Registry
Type: Username with password
Scope: Global
Username: your-docker-username
Password: your-docker-password
ID: docker-credentials

# SSH Key for Deployment
Type: SSH Username with private key
Username: deploy
Private Key: [Paste your private key]
ID: deploy-ssh-key

# GitHub Token (optional)
Type: Secret text
Secret: github_token
ID: github-token
```

#### 4. Configure System Settings

```bash
# Go to Manage Jenkins > Configure System

# Email Notification
SMTP Server: smtp.gmail.com
SMTP Port: 587
Use TLS: Yes
Advanced > Reply-To Address: jenkins@example.com

# Slack (optional)
Slack Workspace: your-workspace
Integration Token: your-token
```

### 📊 Pipeline Stages Explanation

#### **Stage 1: Checkout**
- Mengambil kode dari repository
- Branch: main (production) atau develop (development)

#### **Stage 2: Setup Environment**
- Membuat Python virtual environment
- Install dependencies dari requirements.txt
- Install testing & linting tools

#### **Stage 3: Code Quality**
- Pylint: Static code analysis
- Flake8: PEP8 compliance
- Black: Code formatting check

#### **Stage 4: Unit Tests**
- Menjalankan pytest untuk unit tests
- Generate coverage report
- Threshold: minimal 70% code coverage

#### **Stage 5: Integration Tests**
- Test API endpoints
- Test database integration (jika ada)
- Test third-party service integration

#### **Stage 6: API Smoke Test**
- Start Flask server
- Health check endpoint
- Basic functionality test

#### **Stage 7: Security Scanning**
- Bandit: Find common security issues
- Dependency check (OWASP)
- Report: bandit-report.json

#### **Stage 8: Build Docker Image**
- Only pada branch 'main'
- Tag dengan BUILD_NUMBER dan 'latest'
- Image name: medical-expert-system:BUILD_NUMBER

#### **Stage 9: Push Docker Image**
- Push ke Docker registry
- Credential: docker-credentials
- Tags: BUILD_NUMBER dan 'latest'

#### **Stage 10: Deploy Staging**
- Deploy ke staging environment
- Run sanity tests
- Automated rollback jika gagal

#### **Stage 11: Performance Test**
- Load testing
- Response time benchmarks
- Concurrent request testing

#### **Stage 12: Deploy Production**
- Only ketika tag v*.*.* dibuat
- Backup existing deployment
- Zero-downtime deployment
- Health check

### 🚀 Starting Pipeline

#### Manual Trigger

```bash
Jenkins Dashboard > medical-expert-system > Build Now
```

#### Git Push Trigger

```bash
# Di repository settings (GitHub/GitLab):
# Webhook URL: https://jenkins.example.com/github-webhook/
# Events: Push events
```

#### Scheduled Trigger

```bash
# Di Jenkins Pipeline > Build Triggers > Poll SCM:
H H * * *  # Daily at midnight
H */4 * * *  # Every 4 hours
```

### 📈 Monitoring & Reporting

#### Console Output

```bash
Jenkins Dashboard > Build # > Console Output
```

#### Test Reports

```bash
Jenkins Dashboard > Build # > Test Result
- Shows: Passed/Failed/Skipped tests
- Trend: Historical test results
```

#### Coverage Report

```bash
Jenkins Dashboard > Build # > Coverage Report
- Shows: Code coverage percentage
- Line coverage: % of lines covered
- Branch coverage: % of branches covered
```

#### Performance Report

```bash
Jenkins Dashboard > Build # > Performance Report
- Response times
- Throughput
- Error rates
```

### 🔐 Security Best Practices

1. **Credentials Management**
   ```bash
   # Gunakan Jenkins Credentials Store, bukan hardcoded
   # Rotate credentials regularly
   # Use least privilege principle
   ```

2. **Access Control**
   ```bash
   # Manage Jenkins > Manage Users & Security:
   - Enable LDAP/AD integration
   - Setup role-based access
   - Audit logging
   ```

3. **Network Security**
   ```bash
   # Firewall rules
   - Jenkins port (8080) hanya accessible dari CI/CD
   - API port (5000) hanya dari loadbalancer/proxy
   - SSH port (22) only from CI/CD server
   ```

4. **Pipeline Security**
   ```bash
   # Jenkinsfile approval untuk pull requests
   # Scan dependencies untuk vulnerabilities
   # SAST/DAST scanning
   ```

### 🐛 Troubleshooting

#### Build Fails di Stage Setup Environment

```bash
# Check: Python version compatibility
python3 --version  # Should be 3.7+

# Check: pip installation
pip install --upgrade pip

# Check: Virtual environment
ls -la .venv/
```

#### Tests Fail

```bash
# Run locally first:
source .venv/bin/activate
pytest tests/ -v

# Check: Dependencies
pip list

# Check: Test data availability
ls tests/test_data/
```

#### Docker Build Fails

```bash
# Check: Docker daemon running
docker ps

# Check: Dockerfile syntax
docker build --dry-run .

# Check: Resources available
df -h  # Disk space
free -h  # Memory
```

#### Deployment Fails

```bash
# Check: SSH connectivity
ssh -i ~/.ssh/deploy_key deploy@staging.example.com

# Check: Docker Compose
docker-compose config

# Check: Port availability
netstat -tulpn | grep 5000
```

### 📝 Maintenance

#### Regular Tasks

- **Weekly**: Review test results & coverage trends
- **Monthly**: Update dependencies & security patches
- **Quarterly**: Review & optimize pipeline performance

#### Backup & Recovery

```bash
# Backup Jenkins configuration
tar -czf jenkins-backup.tar.gz $JENKINS_HOME/

# Backup Docker images
docker save medical-expert-system:latest | gzip > backup.tar.gz

# Backup database (jika ada)
pg_dump medical_expert > backup.sql
```

### 📞 Support & Resources

- Jenkins Documentation: https://www.jenkins.io/doc/
- Docker Documentation: https://docs.docker.com/
- Python Testing: https://docs.pytest.org/
- CI/CD Best Practices: https://www.atlassian.com/continuous-delivery

