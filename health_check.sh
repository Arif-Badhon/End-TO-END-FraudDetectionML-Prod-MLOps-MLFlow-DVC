#!/bin/bash

set -euo pipefail

# Colors
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

echo "🏥 Running comprehensive health checks..."
echo ""

all_healthy=true

# Check FastAPI
if curl -sf http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ FastAPI: Healthy${NC}"
else
    echo -e "${RED}❌ FastAPI: Unhealthy${NC}"
    all_healthy=false
fi

# Check MLflow
if curl -sf http://127.0.0.1:5001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ MLflow: Healthy${NC}"
else
    echo -e "${RED}❌ MLflow: Unhealthy${NC}"
    all_healthy=false
fi

# Check PostgreSQL
if docker exec fraud_detection_db pg_isready -U frauduser > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL: Healthy${NC}"
else
    echo -e "${RED}❌ PostgreSQL: Unhealthy${NC}"
    all_healthy=false
fi

echo ""
if $all_healthy; then
    echo -e "${GREEN}🎉 All services are healthy!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some services are unhealthy. Check logs.${NC}"
    exit 1
fi
