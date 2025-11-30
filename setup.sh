#!/bin/bash

# Setup script for AI-Ops Insights Generator

echo "Setting up AI-Ops Insights Generator..."

# Make the main script executable
chmod +x insight_generator.py

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "Usage examples:"
echo "  python insight_generator.py config.json"
echo "  python insight_generator.py config.json --endpoint http://localhost:4047/api/platform/ai-ops-insights/v1/insights"
echo "  python insight_generator.py config.json --dry-run"
echo ""
echo "See README.md for detailed documentation."