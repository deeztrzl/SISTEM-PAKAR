#!/bin/bash
# Deploy to Production Environment

set -e

echo "🎯 Starting production deployment..."

# Safety checks
if [ "$1" != "-y" ] && [ "$1" != "--yes" ]; then
    echo "⚠️  Are you sure you want to deploy to PRODUCTION?"
    read -p "Type 'yes' to confirm: " confirm
    if [ "$confirm" != "yes" ]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Load environment variables
if [ -f .env.prod ]; then
    export $(cat .env.prod | xargs)
fi

# Variables
APP_NAME="medical-expert-system"
PROD_SERVERS=("prod1.example.com" "prod2.example.com")
DEPLOY_PATH="/opt/apps/medical-expert-system"

echo "📊 Creating backup..."
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
# Backup rules.json
cp rules.json $BACKUP_DIR/rules.json.bak || true

echo "🧪 Final testing..."
pytest tests/ -v --tb=short
pytest tests/test_api.py -v --tb=short

echo "📦 Building release..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

echo "🐳 Building production Docker image..."
docker build -t ${APP_NAME}:${CI_BUILD_NUMBER} \
            -t ${APP_NAME}:${VERSION:-latest} .

echo "📤 Deploying to production servers..."
for server in "${PROD_SERVERS[@]}"; do
    echo "🚀 Deploying to ${server}..."
    
    ssh -i ~/.ssh/deploy_key ubuntu@${server} << EOF
        set -e
        cd ${DEPLOY_PATH}
        
        # Backup current state
        docker-compose exec -T app cp rules.json rules.json.bak || true
        
        # Pull latest
        git pull origin main
        
        # Update and restart
        docker-compose pull
        docker-compose down
        docker-compose up -d
        
        # Health check
        sleep 10
        curl -f http://localhost:5000/api/status || exit 1
        echo "✅ ${server} deployment successful"
EOF
done

echo "📊 Running post-deployment tests..."
# Test all production servers
for server in "${PROD_SERVERS[@]}"; do
    echo "Testing ${server}..."
    curl -f http://${server}:5000/api/status || exit 1
done

echo "✅ Production deployment completed successfully!"
echo "📝 Backup location: $BACKUP_DIR"
