#!/bin/bash

# Production Environment Setup Script
echo "🏭 Setting up PRODUCTION environment..."

# Set environment variables for production
export NODE_ENV=production
export VITE_API_URL=${PROD_API_URL:-https://your-api-domain.com}
export VITE_APP_ENV=production

# Copy production environment file if it exists
if [ -f ".env.production" ]; then
    cp .env.production .env
    echo "✅ Copied .env.production to .env"
else
    echo "⚠️  .env.production not found, using default .env"
fi

# Validate required production environment variables
echo "🔍 Validating production environment..."

if [ -z "$PROD_API_URL" ]; then
    echo "❌ ERROR: PROD_API_URL environment variable is required for production"
    echo "   Set it with: export PROD_API_URL=https://your-api-domain.com"
    exit 1
fi

# Build the application for production
echo "🔨 Building application for production..."
cd apps/frontend && npm run build

if [ $? -eq 0 ]; then
    echo "✅ Production build completed successfully!"
    echo "📦 Build files are in apps/frontend/dist/"
    echo "🚀 Deploy the dist/ folder to your hosting platform"
    echo "🌐 API configured for: $VITE_API_URL"
else
    echo "❌ Production build failed!"
    exit 1
fi