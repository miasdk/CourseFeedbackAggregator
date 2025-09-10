#!/bin/bash

# Environment Switching Utility
# Usage: ./scripts/switch-env.sh [dev|prod|status]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

show_status() {
    echo "📊 Current Environment Status:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -f "$PROJECT_ROOT/.env" ]; then
        echo "📄 Active .env file found"
        if grep -q "NODE_ENV=development" "$PROJECT_ROOT/.env" 2>/dev/null; then
            echo "🟢 Environment: DEVELOPMENT"
        elif grep -q "NODE_ENV=production" "$PROJECT_ROOT/.env" 2>/dev/null; then
            echo "🔴 Environment: PRODUCTION"
        else
            echo "🟡 Environment: UNKNOWN"
        fi
    else
        echo "⚠️  No .env file found"
    fi
    
    echo ""
    echo "Available environment files:"
    [ -f "$PROJECT_ROOT/.env.development" ] && echo "  ✅ .env.development" || echo "  ❌ .env.development"
    [ -f "$PROJECT_ROOT/.env.production" ] && echo "  ✅ .env.production" || echo "  ❌ .env.production"
    echo ""
}

show_help() {
    echo "🔧 Environment Switching Utility"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Usage: ./scripts/switch-env.sh [command]"
    echo ""
    echo "Commands:"
    echo "  dev      Switch to development environment and start dev server"
    echo "  prod     Switch to production environment and build"
    echo "  status   Show current environment status"
    echo "  help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./scripts/switch-env.sh dev     # Start development"
    echo "  ./scripts/switch-env.sh prod    # Build for production"
    echo "  ./scripts/switch-env.sh status  # Check current environment"
    echo ""
}

case "$1" in
    "dev")
        echo "🚀 Switching to DEVELOPMENT environment..."
        cd "$PROJECT_ROOT"
        ./scripts/dev.sh
        ;;
    "prod")
        echo "🏭 Switching to PRODUCTION environment..."
        cd "$PROJECT_ROOT"
        ./scripts/prod.sh
        ;;
    "status")
        show_status
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        echo "❌ No command specified"
        echo ""
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac