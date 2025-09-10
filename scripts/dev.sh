#!/bin/bash

# Development Environment Setup Script
echo "🚀 Setting up DEVELOPMENT environment..."

# Set environment variables for development
export NODE_ENV=development
export VITE_API_URL=http://localhost:8000
export VITE_APP_ENV=development

# Copy development environment file if it exists
if [ -f ".env.development" ]; then
    cp .env.development .env
    echo "✅ Copied .env.development to .env"
    echo "🎭 Mock data enabled for development"
else
    echo "⚠️  .env.development not found, using default .env"
fi

# Update vite config for development
echo "📝 Using development configuration..."

# Start the frontend development server
echo "🌟 Starting development server on http://localhost:3000"
echo "📡 API proxy configured for http://localhost:8000"

cd apps/frontend && npm run dev