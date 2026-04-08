#!/bin/bash
# Local setup script untuk development & testing

set -e

echo "🔧 Setting up development environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
pip install pytest pytest-cov pylint flake8 black bandit

# Create necessary directories
mkdir -p logs reports coverage-report

# Run initial tests
echo "🧪 Running tests..."
pytest tests/ -v --tb=short --cov=inference_engine --cov-report=html || true

echo "✅ Development environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Run tests: pytest tests/ -v"
echo "  3. Start server: python simple_server.py"
echo "  4. Start GUI: python main.py"
