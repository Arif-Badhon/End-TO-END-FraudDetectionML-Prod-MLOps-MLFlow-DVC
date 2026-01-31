#!/bin/bash

set -euo pipefail

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Configuration
readonly LOG_DIR="logs"
readonly PID_DIR="$LOG_DIR"

# Logging functions
log_header() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

# Check service status
check_service_status() {
    local service_name=$1
    local port=$2
    local pid_file=$3
    local health_url=$4
    
    echo -e "${BLUE}$service_name:${NC}"
    
    local status_ok=true
    
    # Check PID file
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "   Process: ${GREEN}✅ Running${NC} (PID: $pid)"
        else
            echo -e "   Process: ${RED}❌ Dead${NC} (stale PID: $pid)"
            status_ok=false
        fi
    else
        # Check by port
        if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
            local pid=$(lsof -ti:"$port" 2>/dev/null | head -1)
            echo -e "   Process: ${YELLOW}⚠️  Running${NC} (PID: $pid, no PID file)"
        else
            echo -e "   Process: ${RED}❌ Not running${NC}"
            status_ok=false
        fi
    fi
    
    # Check port
    if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "   Port $port: ${GREEN}✅ Listening${NC}"
    else
        echo -e "   Port $port: ${RED}❌ Not listening${NC}"
        status_ok=false
    fi
    
    # Check health endpoint (if provided)
    if [ -n "$health_url" ]; then
        if curl -sf "$health_url" > /dev/null 2>&1; then
            echo -e "   Health: ${GREEN}✅ Healthy${NC}"
        else
            echo -e "   Health: ${RED}❌ Unhealthy${NC}"
            status_ok=false
        fi
    fi
    
    # Overall status
    if $status_ok; then
        echo -e "   Status: ${GREEN}✅ OK${NC}"
    else
        echo -e "   Status: ${RED}❌ Issues detected${NC}"
    fi
    
    echo ""
}

# Check Docker container
check_docker_container() {
    local container_name=$1
    local service_name=$2
    
    echo -e "${BLUE}$service_name:${NC}"
    
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null || echo "unknown")
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "none")
        
        echo -e "   Container: ${GREEN}✅ Running${NC}"
        echo -e "   Status: ${GREEN}$status${NC}"
        
        if [ "$health" != "none" ]; then
            if [ "$health" = "healthy" ]; then
                echo -e "   Health: ${GREEN}✅ $health${NC}"
            else
                echo -e "   Health: ${YELLOW}⚠️  $health${NC}"
            fi
        fi
    else
        echo -e "   Container: ${RED}❌ Not running${NC}"
    fi
    
    echo ""
}

# Display service URLs
display_urls() {
    echo -e "${CYAN}📊 Service URLs:${NC}"
    echo -e "   🌐 API:        http://127.0.0.1:8000"
    echo -e "   📚 API Docs:   http://127.0.0.1:8000/docs"
    echo -e "   📊 MLflow:     http://127.0.0.1:5001"
    echo -e "   🗄️  PgAdmin:    http://127.0.0.1:5050"
    echo ""
}

# Display log tails
display_recent_logs() {
    echo -e "${CYAN}📝 Recent Log Entries:${NC}"
    
    if [ -f "$LOG_DIR/api.log" ]; then
        echo -e "${BLUE}FastAPI (last 3 lines):${NC}"
        tail -n 3 "$LOG_DIR/api.log" 2>/dev/null | sed 's/^/   /'
        echo ""
    fi
    
    if [ -f "$LOG_DIR/mlflow.log" ]; then
        echo -e "${BLUE}MLflow (last 3 lines):${NC}"
        tail -n 3 "$LOG_DIR/mlflow.log" 2>/dev/null | sed 's/^/   /'
        echo ""
    fi
}

# Main execution
main() {
    log_header "Fraud Detection ML - Service Status"
    
    # Check application services
    check_service_status "FastAPI" "8000" "$PID_DIR/api.pid" "http://127.0.0.1:8000/health"
    check_service_status "MLflow" "5001" "$PID_DIR/mlflow.pid" "http://127.0.0.1:5001"
    
    # Check Docker containers
    check_docker_container "fraud_detection_db" "PostgreSQL"
    check_docker_container "fraud_detection_pgadmin" "PgAdmin"
    
    # Display URLs
    display_urls
    
    # Display recent logs
    display_recent_logs
    
    echo -e "${CYAN}💡 Commands:${NC}"
    echo -e "   Start:   ./start.sh"
    echo -e "   Stop:    ./stop.sh"
    echo -e "   Restart: ./restart.sh"
    echo -e "   Logs:    tail -f logs/api.log"
    echo ""
}

# Run main function
main
