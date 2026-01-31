#!/bin/bash

set -euo pipefail

# Colors
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

log_header() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

main() {
    log_header "Fraud Detection ML - Restarting Services"
    
    # Stop services
    if ./stop.sh; then
        echo ""
        echo "⏳ Waiting 3 seconds before restart..."
        sleep 3
        echo ""
        
        # Start services
        ./start.sh
    else
        echo "❌ Failed to stop services. Fix errors before restarting."
        exit 1
    fi
}

main
