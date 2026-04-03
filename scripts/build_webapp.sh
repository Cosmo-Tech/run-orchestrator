#!/bin/bash
# Build the Visual Orchestrator web app into static files for packaging.
# The built files are output to cosmotech/csm_orc_api/static/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WEBAPP_DIR="$PROJECT_ROOT/cosmotech/visual_orchestrator"

if [ ! -f "$WEBAPP_DIR/package.json" ]; then
    echo "ERROR: visual_orchestrator source not found at $WEBAPP_DIR"
    exit 1
fi

echo "Installing npm dependencies..."
cd "$WEBAPP_DIR"
npm install

echo "Building web app..."
npm run build

echo "Build complete. Static files are in cosmotech/csm_orc_api/static/"
