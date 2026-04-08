# Quick Reference untuk Jenkins Integration

## File Structure

```
medical_expert_system/
├── Jenkinsfile                 # Pipeline definition
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose config
├── pytest.ini                  # Pytest configuration
├── .gitignore                  # Git ignore rules
├── .dockerignore               # Docker build ignore
├── .env.example                # Example environment variables
├── .env.staging                # Staging environment
├── .env.prod                   # Production environment
│
├── scripts/                    # Deployment & build scripts
│   ├── setup-dev.sh            # Development setup
│   ├── build.sh                # Build & packaging
│   ├── deploy-staging.sh       # Staging deployment
│   └── deploy-prod.sh          # Production deployment
│
├── tests/                      # Automated tests
│   ├── __init__.py
│   ├── conftest.py             # Pytest configuration
│   ├── test_inference.py       # Unit tests
│   ├── test_api.py             # Integration tests
│   └── test_performance.py     # Performance tests
│
└── ... (original files)        # Application files
```

## Quick Start

### 1. Setup Jenkins Server

```bash
# Install Jenkins
sudo apt-get install jenkins

# Install required plugins
# Dashboard > Manage Jenkins > Manage Plugins:
# - Pipeline
# - Docker Pipeline
# - Git
# - Email Extension
```

### 2. Create Pipeline Job

```bash
# Dashboard > New Item > Pipeline
# Name: medical-expert-system
# Pipeline > Definition: Pipeline script from SCM
# SCM: Git
# Repository: https://your-repo.git
# Script Path: Jenkinsfile
```

### 3. Add Credentials

```bash
# Docker Registry
Manage Jenkins > Manage Credentials > Add Credentials:
- Username: your-docker-username
- Password: your-docker-token
- ID: docker-credentials

# SSH Key
- Private Key from: ~/.ssh/deploy_key
- ID: deploy-ssh-key
```

### 4. Build

```bash
# Trigger build
Dashboard > medical-expert-system > Build Now

# Monitor progress
Dashboard > medical-expert-system > Build History > Console Output
```

## Local Testing

### Run Tests Locally

```bash
# Setup
bash scripts/setup-dev.sh

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_inference.py -v

# Run with coverage
pytest tests/ --cov=inference_engine --cov-report=html
```

### Start Development Server

```bash
source venv/bin/activate
python simple_server.py
# Open: http://localhost:5000
```

### Build Docker Image Locally

```bash
docker build -t medical-expert-system:test .
docker run -p 5000:5000 medical-expert-system:test
```

## Common Commands

### Jenkins

```bash
# Trigger build from command line
curl -X POST http://jenkins.example.com:8080/job/medical-expert-system/build

# Get build status
curl http://jenkins.example.com:8080/api/json?tree=jobs[name,lastBuild[result]]

# View console output
curl http://jenkins.example.com:8080/job/medical-expert-system/lastBuild/consoleText
```

### Docker

```bash
# Build
docker build -t medical-expert-system:1.0 .

# Run
docker run -p 5000:5000 medical-expert-system:1.0

# Push
docker push registry.example.com/medical-expert-system:1.0

# Compose
docker-compose up -d
docker-compose down
```

### Testing

```bash
# All tests
pytest tests/ -v

# Specific marker
pytest tests/ -m integration -v

# With coverage
pytest tests/ --cov --cov-report=html

# Performance tests
pytest tests/test_performance.py -v
```

## Environment Setup

### Staging (.env.staging)

```bash
FLASK_ENV=staging
DEPLOY_HOST=staging.example.com
LOG_LEVEL=INFO
```

### Production (.env.prod)

```bash
FLASK_ENV=production
LOG_LEVEL=WARNING
API_WORKERS=4
```

## Pipeline Stages

| Stage | Command | Output |
|-------|---------|--------|
| Setup | pip install -r requirements.txt | logs |
| Linting | pylint **/*.py | reports/lint-report.txt |
| Tests | pytest tests/ -v | junit.xml, coverage.xml |
| API Test | curl http://localhost:5000/api/status | success/fail |
| Docker Build | docker build | image:tag |
| Push | docker push image:tag | registry confirmation |

## Troubleshooting

### Build Failures

```bash
# Check logs
tail -f /var/lib/jenkins/logs/jenkins.log

# Manually run failing stage
source .venv/bin/activate
pytest tests/ -v  # If tests fail

# Check Docker
docker ps -a
docker logs container-name
```

### Deployment Issues

```bash
# Check SSH connectivity
ssh -i ~/.ssh/deploy_key deploy@staging.example.com

# Check Docker daemon
sudo systemctl status docker

# Verify disk space
df -h  # At least 10GB free recommended
```

## Useful Links

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Python Testing](https://docs.pytest.org/)
- [CI/CD Patterns](https://www.atlassian.com/continuous-delivery)

