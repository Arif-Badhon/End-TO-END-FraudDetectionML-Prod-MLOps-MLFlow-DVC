# Production Deployment Guide (Phase 6)

*Note: This document outlines the deployment strategy planned for Phase 6.*

## 1. Containerization
The entire stack is containerized using Docker. 
- **API Service:** A minimal Python Docker image running Uvicorn and FastAPI.
- **MLflow Service:** A container running the MLflow tracking server, backed by a PostgreSQL database.
- **Database:** Standard PostgreSQL 16 image.

## 2. CI/CD Pipeline (GitHub Actions)
Our automated pipeline ensures quality and safe deployments.
1. **Continuous Integration (CI):**
   - Linting (`ruff`, `black`).
   - Type checking (`mypy`).
   - Unit and Integration tests (`pytest`).
   - Data validation runs (`Great Expectations`).
2. **Continuous Deployment (CD):**
   - On a push to the `main` branch, a new Docker image is built and pushed to a container registry.
   - The deployment manifest is updated to point to the new image tag.

## 3. Kubernetes (Optional / Advanced)
For highly scalable deployments, the Docker containers are orchestrated via Kubernetes.
- **Deployments:** Manage the replicas of the FastAPI pods.
- **Services:** Route traffic to the API pods.
- **ConfigMaps/Secrets:** Securely inject environment variables and database credentials.

## 4. Monitoring
- **Prometheus & Grafana:** Used to monitor system metrics (CPU, Memory, Request Latency) and business metrics (Fraud Rate, Prediction Confidence distributions).
- **Evidently:** Continuously monitors for Data Drift (input features changing over time) and Concept Drift (the relationship between features and fraud changing).
