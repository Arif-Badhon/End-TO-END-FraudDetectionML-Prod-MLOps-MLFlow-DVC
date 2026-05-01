# 🚀 Fraud Detection ML System

> **Production-Grade Machine Learning Platform** | From Data to Deployment | End-to-End MLOps

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📋 Quick Overview

**Fraud Detection ML System** is a complete, production-ready machine learning platform focused on teaching and implementing real-world MLOps practices. Unlike standard tutorials that only focus on training a model, this project demonstrates how to build, version, serve, and monitor an entire ML system using industry-standard tools.

### Built With Industry Standards
- **FastAPI** - Modern async web framework for prediction serving
- **PostgreSQL** - Production relational database
- **MLflow** - Experiment tracking & model registry
- **DVC** - Data and model versioning pipelines
- **Feast** - Feature store for online and offline features
- **Great Expectations** - Data quality validation

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Git
- `uv` (Fast Python package installer)

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/fraud-detection-ml.git
cd fraud-detection-ml

# 2. Install dependencies via uv
uv venv
source .venv/bin/activate
uv sync

# 3. Setup configuration
cp .env.example .env

# 4. Start all backend services (Postgres, MLflow, API)
./start.sh

# 5. Verify health
./health_check.sh
```

### Reproducing the ML Pipeline
We use DVC to manage our data pipeline (from ingestion to feature engineering).
```bash
# Pull the latest data (requires remote access)
uv run dvc pull

# Run the full data and feature engineering pipeline
uv run dvc repro
```

---

## 📖 Documentation Directory

To keep this README clean, detailed information has been split into dedicated documents. **Please start here to understand the system:**

- **[Project Progress Tracker](docs/PROGRESS.md):** Live tracking of the 8 development phases.
- **[System Architecture](docs/ARCHITECTURE.md):** Diagrams and explanations of how the API, MLflow, Feast, and Postgres interact.
- **[API Reference](docs/API_REFERENCE.md):** Documentation for the FastAPI prediction and health endpoints.
- **[Deployment Guide](docs/DEPLOYMENT.md):** Details on Docker, CI/CD, and monitoring.

### Phase Learning Guides
Deep dive into the specific technologies and decisions made during each phase of the project:
- 📘 **[Phase 0: Foundation](docs/PHASE_0_LEARNING.md)** (Backend, Docker, MLflow, DVC)
- 📊 **[Phase 1: Data & EDA](docs/PHASE_1_LEARNING.md)** (Great Expectations, ydata-profiling)
- 🛠️ **[Phase 2: Features](docs/PHASE_2_LEARNING.md)** (NLP Text Metrics, Feast Feature Store)
- 🤖 **[Phase 3: Models](docs/PHASE_3_LEARNING.md)** (XGBoost, Imbalanced Data, SHAP)

---

## 💻 Services & Ports

When running `./start.sh`, the following services are available locally:

| Service | URL | Purpose |
|---------|-----|---------|
| **FastAPI Docs** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Interactive API Testing |
| **MLflow UI** | [http://127.0.0.1:5001](http://127.0.0.1:5001) | Experiment & Model Tracking |
| **PgAdmin** | [http://127.0.0.1:5050](http://127.0.0.1:5050) | Database Manager |

*To stop the services safely, run `./stop.sh`.*

---

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'feat: add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

## 📄 License
MIT License - feel free to use this for learning, projects, and portfolios.
