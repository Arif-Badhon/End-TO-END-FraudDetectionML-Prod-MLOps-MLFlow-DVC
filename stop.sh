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
readonly SHUTDOWN_TIMEOUT=10

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

# Stop service gracefully
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    log_info "Stopping $service_name..."
    
    if [ ! -f "$pid_file" ]; then
        log_warning "No PID file found for $service_name"
        return 1
    fi
    
    local pid=$(cat "$pid_file")
    
    # Check if process exists
    if ! kill -0 "$pid" 2>/dev/null; then
        log_warning "$service_name process (PID: $pid) not found"
        rm "$pid_file"
        return 1
    fi
    
    # Try graceful shutdown (SIGTERM)
    log_info "Sending SIGTERM to $service_name (PID: $pid)..."
    kill -TERM "$pid" 2>/dev/null || true
    
    # Wait for process to stop
    local elapsed=0
    while [ $elapsed -lt $SHUTDOWN_TIMEOUT ]; do
        if ! kill -0 "$pid" 2>/dev/null; then
            log_success "$service_name stopped gracefully"
            rm "$pid_file"
            return 0
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done
    
    # Force kill if still running
    log_warning "$service_name didn't stop gracefully, forcing shutdown..."
    kill -KILL "$pid" 2>/dev/null || true
    sleep 1
    
    if ! kill -0 "$pid" 2>/dev/null; then
        log_success "$service_name force stopped"
        rm "$pid_file"
        return 0
    else
        log_error "Failed to stop $service_name"
        return 1
    fi
}

# Stop FastAPI
stop_fastapi() {
    log_header "Stopping FastAPI"
    
    if stop_service "FastAPI" "$PID_DIR/api.pid"; then
        return 0
    fi
    
    # Fallback: kill by port
    log_info "Attempting to stop by port..."
    local pids=$(lsof -ti:8000 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -TERM 2>/dev/null || true
        sleep 2
        echo "$pids" | xargs kill -KILL 2>/dev/null || true
        log_success "FastAPI stopped by port"
    fi
}

# Stop MLflow
stop_mlflow() {
    log_header "Stopping MLflow"
    
    if stop_service "MLflow" "$PID_DIR/mlflow.pid"; then
        return 0
    fi
    
    # Fallback: kill by port
    log_info "Attempting to stop by port..."
    local pids=$(lsof -ti:5001 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -TERM 2>/dev/null || true
        sleep 2
        echo "$pids" | xargs kill -KILL 2>/dev/null || true
        log_success "MLflow stopped by port"
    fi
}

# Stop PostgreSQL
stop_postgresql() {
    log_header "Stopping PostgreSQL"
    
    if [ ! -d "docker" ]; then
        log_error "docker/ directory not found"
        return 1
    fi
    
    cd docker
    
    if docker-compose down 2>&1 | tee "../$LOG_DIR/postgres_stop.log"; then
        cd ..
        log_success "PostgreSQL stopped"
        return 0
    else
        cd ..
        log_error "Failed to stop PostgreSQL"
        log_info "Check logs: cat $LOG_DIR/postgres_stop.log"
        return 1
    fi
}

# Clean up stale files
cleanup() {
    log_header "Cleaning Up"
    
    # Remove stale PID files
    if [ -d "$PID_DIR" ]; then
        find "$PID_DIR" -name "*.pid" -type f -delete 2>/dev/null || true
        log_success "Removed stale PID files"
    fi
    
    # Optionally clean logs (commented out by default)
    # log_info "Clean logs? (y/N)"
    # read -r response
    # if [[ "$response" =~ ^[Yy]$ ]]; then
    #     rm -f "$LOG_DIR"/*.log
    #     log_success "Logs cleaned"
    # fi
}

# Main execution
main() {
    log_header "Fraud Detection ML - Stopping Services"
    
    # Create log directory if not exists
    mkdir -p "$LOG_DIR"
    
    # Stop services in reverse order
    stop_fastapi
    stop_mlflow
    stop_postgresql
    
    # Cleanup
    cleanup
    
    log_header "All Services Stopped! 👋"
}

# Run main function
main
