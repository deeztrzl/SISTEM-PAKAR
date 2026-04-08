#!/bin/bash
# Build & Package script

set -e

VERSION=${1:-"1.0.0"}
APP_NAME="medical-expert-system"
BUILD_DIR="build"

echo "🏗️  Building ${APP_NAME} v${VERSION}..."

# Clean previous builds
rm -rf $BUILD_DIR dist
mkdir -p $BUILD_DIR

# Copy source files
cp -r inference_engine $BUILD_DIR/
cp -r ui $BUILD_DIR/
cp -r web_ui $BUILD_DIR/
cp rules.json $BUILD_DIR/
cp requirements.txt $BUILD_DIR/
cp {cli,main,simple_server}.py $BUILD_DIR/ 2>/dev/null || true

# Create version file
cat > $BUILD_DIR/VERSION << EOF
version=${VERSION}
build_date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
git_commit=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
EOF

# Create tarball
ARCHIVE="${APP_NAME}-${VERSION}.tar.gz"
tar -czf ${ARCHIVE} -C $BUILD_DIR .

# Create checksums
sha256sum ${ARCHIVE} > ${ARCHIVE}.sha256

echo "✅ Build complete!"
echo "📦 Package: ${ARCHIVE}"
echo "📊 Checksum: $(cat ${ARCHIVE}.sha256)"
echo ""
echo "📝 Files created:"
ls -lh ${ARCHIVE}* 
