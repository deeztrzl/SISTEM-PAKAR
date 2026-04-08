#!/bin/bash
# Deploy to Staging Environment

set -e

echo "🚀 Starting deployment to staging..."

# Load environment variables
if [ -f .env.staging ]; then
    export $(cat .env.staging | xargs)
fi

# Variables
APP_NAME="medical-expert-system"
STAGING_SERVER="${STAGING_HOST:-staging.example.com}"
DEPLOY_PATH="/opt/apps/medical-expert-system"

echo "📦 Building application..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

echo "🧪 Running tests..."
pytest tests/ -v --tb=short || exit 1

echo "🐳 Building Docker image..."
docker build -t ${APP_NAME}:${CI_BUILD_NUMBER} .

if [ ! -z "$STAGING_SERVER" ]; then
    echo "📤 Pushing to staging server..."
    
    # Option 1: Using SSH and systemd
    ssh -i ~/.ssh/deploy_key ubuntu@${STAGING_SERVER} << EOF
        cd ${DEPLOY_PATH}
        git pull origin main
        docker-compose down || true
        docker-compose up -d
        sleep 5
        curl -f http://localhost:5000/api/status || exit 1
        echo "✅ Staging deployment successful"
EOF
    
    # Option 2: Using Docker registry
    # docker tag ${APP_NAME}:${CI_BUILD_NUMBER} ${DOCKER_REGISTRY}/${APP_NAME}:staging
    # docker push ${DOCKER_REGISTRY}/${APP_NAME}:staging
fi

echo "✅ Staging deployment completed!"
