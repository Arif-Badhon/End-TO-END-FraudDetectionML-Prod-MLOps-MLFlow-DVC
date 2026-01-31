#!/bin/bash

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Configuration
readonly MAX_RETRIES=3
readonly RETRY_DELAY=2
readonly POSTGRES_READY_TIMEOUT=30
readonly SERVICE_START_DELAY=2
readonly LOG_DIR="logs"
readonly PID_DIR="logs"

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

# Error handler
error_exit() {
    log_error "$1"
    log_info "Run './stop.sh' to clean up any started services"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if UV is installed
    if ! command -v uv &> /dev/null; then
        error_exit "UV not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error_exit "Docker not found. Install Docker Desktop: https://www.docker.com/products/docker-desktop"
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        error_exit "Docker is not running. Please start Docker Desktop"
    fi
    
    # Check if docker-compose exists
    if [ ! -f "docker/docker-compose.yml" ]; then
        error_exit "docker/docker-compose.yml not found"
    fi
    
    # Check if .env exists
    if [ ! -f .env ]; then
        error_exit ".env file not found. Copy .env.example and configure it"
    fi
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    log_success "All prerequisites met"
}

# Wait for service to be ready
wait_for_service() {
    local service_name=$1
    local host=$2
    local port=$3
    local max_wait=$4
    
    log_info "Waiting for $service_name to be ready..."
    
    local elapsed=0
    while [ $elapsed -lt $max_wait ]; do
        if nc -z "$host" "$port" 2> /dev/null; then
            log_success "$service_name is ready"
            return 0
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done
    
    log_error "$service_name failed to start within ${max_wait}s"
    return 1
}

# Start PostgreSQL with retry
start_postgresql() {
    log_header "Starting PostgreSQL"
    
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        log_info "Attempt $((retry_count + 1))/$MAX_RETRIES"
        
        cd docker
        if docker-compose up -d >> "../$LOG_DIR/postgres.log" 2>&1; then
            cd ..
            
            # Wait for PostgreSQL to be ready
            if wait_for_service "PostgreSQL" "127.0.0.1" "5433" "$POSTGRES_READY_TIMEOUT"; then
                
                # Test database connection
                log_info "Testing database connection..."
                if uv run python -m backend.app.database >> "$LOG_DIR/postgres.log" 2>&1; then
                    log_success "PostgreSQL started and database connection verified"
                    return 0
                else
                    log_warning "Database connection test failed"
                fi
            fi
        else
            cd ..
            log_warning "Failed to start PostgreSQL containers"
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            log_info "Retrying in ${RETRY_DELAY}s..."
            sleep $RETRY_DELAY
        fi
    done
    
    error_exit "Failed to start PostgreSQL after $MAX_RETRIES attempts"
}

# Start MLflow with retry
start_mlflow() {
    log_header "Starting MLflow"
    
    # Check if port is already in use
    if lsof -Pi :5001 -sTCP:LISTEN -t > /dev/null 2>&1; then
        log_warning "Port 5001 is already in use"
        log_info "Attempting to stop existing process..."
        lsof -ti:5001 | xargs kill -9 2> /dev/null || true
        sleep 2
    fi
    
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        log_info "Attempt $((retry_count + 1))/$MAX_RETRIES"
        
        # Start MLflow in background
        nohup uv run mlflow ui --host 127.0.0.1 --port 5001 > "$LOG_DIR/mlflow.log" 2>&1 &
        
        local mlflow_pid=$!
        echo $mlflow_pid > "$PID_DIR/mlflow.pid"
        
        sleep $SERVICE_START_DELAY
        
        # Check if process is still running
        if kill -0 $mlflow_pid 2> /dev/null; then
            # Wait for service to be ready
            if wait_for_service "MLflow" "127.0.0.1" "5001" 10; then
                log_success "MLflow started (PID: $mlflow_pid)"
                return 0
            else
                log_warning "MLflow process started but service not responding"
                kill $mlflow_pid 2> /dev/null || true
            fi
        else
            log_warning "MLflow process died immediately"
            log_info "Last 10 lines of mlflow.log:"
            tail -n 10 "$LOG_DIR/mlflow.log"
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            log_info "Retrying in ${RETRY_DELAY}s..."
            sleep $RETRY_DELAY
        fi
    done
    
    error_exit "Failed to start MLflow after $MAX_RETRIES attempts"
}

# Start FastAPI with retry
start_fastapi() {
    log_header "Starting FastAPI"
    
    # Check if port is already in use
    if lsof -Pi :8000 -sTCP:LISTEN -t > /dev/null 2>&1; then
        log_warning "Port 8000 is already in use"
        log_info "Attempting to stop existing process..."
        lsof -ti:8000 | xargs kill -9 2> /dev/null || true
        sleep 2
    fi
    
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        log_info "Attempt $((retry_count + 1))/$MAX_RETRIES"
        
        # Start FastAPI in background
        cd backend
        nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "../$LOG_DIR/api.log" 2>&1 &
        
        local api_pid=$!
        cd ..
        echo $api_pid > "$PID_DIR/api.pid"
        
        sleep $SERVICE_START_DELAY
        
        # Check if process is still running
        if kill -0 $api_pid 2> /dev/null; then
            # Wait for service to be ready
            if wait_for_service "FastAPI" "127.0.0.1" "8000" 10; then
                # Test health endpoint
                log_info "Testing API health endpoint..."
                if curl -sf http://127.0.0.1:8000/health > /dev/null 2>&1; then
                    log_success "FastAPI started and health check passed (PID: $api_pid)"
                    return 0
                else
                    log_warning "FastAPI started but health check failed"
                fi
            else
                log_warning "FastAPI process started but service not responding"
                kill $api_pid 2> /dev/null || true
            fi
        else
            log_warning "FastAPI process died immediately"
            log_info "Last 10 lines of api.log:"
            tail -n 10 "$LOG_DIR/api.log"
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            log_info "Retrying in ${RETRY_DELAY}s..."
            sleep $RETRY_DELAY
        fi
    done
    
    error_exit "Failed to start FastAPI after $MAX_RETRIES attempts"
}

# Display service URLs
display_service_info() {
    log_header "Service Information"
    
    echo -e "${CYAN}📊 Access Services:${NC}"
    echo -e "   🌐 API:        ${GREEN}http://127.0.0.1:8000${NC}"
    echo -e "   📚 API Docs:   ${GREEN}http://127.0.0.1:8000/docs${NC}"
    echo -e "   📊 MLflow:     ${GREEN}http://127.0.0.1:5001${NC}"
    echo -e "   🗄️  PgAdmin:    ${GREEN}http://127.0.0.1:5050${NC}"
    echo ""
    echo -e "${CYAN}📝 View Logs:${NC}"
    echo -e "   tail -f $LOG_DIR/api.log"
    echo -e "   tail -f $LOG_DIR/mlflow.log"
    echo -e "   tail -f $LOG_DIR/postgres.log"
    echo ""
    echo -e "${CYAN}🛑 Stop Services:${NC}"
    echo -e "   ./stop.sh"
    echo ""
    echo -e "${CYAN}📊 Check Status:${NC}"
    echo -e "   ./status.sh"
    echo ""
}

# Main execution
main() {
    log_header "Fraud Detection ML - Starting Services"
    
    # Check prerequisites
    check_prerequisites
    
    # Start services in order
    start_postgresql
    start_mlflow
    start_fastapi
    
    # Display service information
    log_header "All Services Started Successfully! 🎉"
    display_service_info
}

# Run main function
main
