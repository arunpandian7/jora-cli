#!/bin/bash
# Jira Manager Runner Script

echo "🎯 Starting Jira Manager..."

# Check if .env exists, if not copy from template
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from template..."
    cp .env.template .env
    echo "📝 Please edit .env file with your Jira credentials before running again."
    echo "   nano .env"
    exit 1
fi

# Run the Jira manager
uv run jira_manager.py