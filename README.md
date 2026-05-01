# 🚀 Fraud Detection ML System

> **Production-Grade Machine Learning Platform** | From Data to Deployment | End-to-End MLOps

![Status](https://img.shields.io/badge/Phase%200-✅%20Complete-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📋 Quick Overview

**Fraud Detection ML System** is a complete, production-ready machine learning platform that teaches you how to build real ML systems used by Netflix, Uber, and Airbnb.

### What Makes This Different?

Most ML tutorials teach **model training**. This teaches **production ML systems**:

| Aspect | Tutorial | This Project |
|--------|----------|--------------|
| Focus | Train model | Deploy system |
| Database | CSV file | PostgreSQL |
| Versioning | Manual | DVC tracked |
| Tracking | Spreadsheet | MLflow |
| API | None | FastAPI |
| Monitoring | None | Health checks |
| Deployment | Notebook | Docker ready |

### Built With Industry Standards

- **FastAPI** - Modern async web framework
- **PostgreSQL** - Production database with schemas
- **MLflow** - Experiment tracking & model registry
- **DVC** - Data and model versioning
- **Docker** - Containerization & reproducibility
- **ZenML** - ML pipeline orchestration (Phase 2+)
- **Feast** - Feature store management (Phase 2+)

---

## 🎯 Project Goals

### What You'll Learn

✅ **Infrastructure as Code** - Docker, Kubernetes, CI/CD  
✅ **Backend Development** - FastAPI, PostgreSQL, SQLAlchemy  
✅ **Data Management** - Pipelines, versioning, quality checks  
✅ **ML Engineering** - Tracking, serving, monitoring  
✅ **Production Patterns** - Health checks, logging, error handling  
✅ **DevOps Skills** - Deployment, scaling, incident response  

### What You'll Build

- Complete ML platform with 8 phases
- Production-ready API serving predictions
- Data pipeline with quality validation
- Model tracking and versioning
- Real-time monitoring and alerts
- Cloud deployment (Hugging Face, AWS)

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

```bash
# Check you have these
python --version        # Python 3.12+
docker --version        # Docker installed
git --version          # Git installed
```

### Installation

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/fraud-detection-ml.git
cd fraud-detection-ml

# 2. Install dependencies
uv venv
source .venv/bin/activate
uv sync

# 3. Copy configuration
cp .env.example .env

# 4. Start all services
./start.sh

# 5. Verify everything works
./health_check.sh
```

### Access Services

```
🌐 API:        http://127.0.0.1:8000/docs
📊 MLflow:     http://127.0.0.1:5001
🗄️  Database:   http://127.0.0.1:5050 (PgAdmin)
```

### Test It

```bash
# Health check
curl http://127.0.0.1:8000/health

# Stop when done
./stop.sh
```

---

## 📊 Project Structure

```
fraud-detection-ml/
├── backend/              # FastAPI application
├── docker/               # PostgreSQL + PgAdmin
├── data/                 # Datasets (DVC tracked)
├── models/               # Trained models (DVC tracked)
├── notebooks/            # Jupyter notebooks
├── configs/              # Configuration files
├── scripts/              # Training & inference scripts
│
├── start.sh              # Start all services
├── stop.sh               # Stop services
├── status.sh             # Check service health
├── health_check.sh       # Verify all healthy
├── restart.sh            # Restart services
│
├── pyproject.toml        # Python dependencies
├── uv.lock              # Locked dependencies
├── .env.example         # Environment template
└── README.md            # This file
```

---

## 🔄 The 8-Phase Journey

### Phase 0: Foundation ✅ COMPLETE

**Status**: ✅ Complete | **Time**: 8-12 hours

Build production infrastructure with FastAPI, PostgreSQL, MLflow, and DVC.

**What's working:**

- PostgreSQL database with schemas
- FastAPI backend with endpoints
- MLflow experiment tracking
- DVC data versioning
- Production-grade service scripts
- Health monitoring

```bash
./start.sh        # See everything running
./status.sh       # Check health
```

---

### Phase 1: Data & EDA ✅ COMPLETE

**Status**: ✅ Complete | **Time**: 12-16 hours

Download dataset and explore patterns.

**You'll learn:**

- Pandas data manipulation
- Statistical analysis
- Data visualization
- Data quality testing
- Dataset versioning with DVC

**You'll build:**

- EDA Jupyter notebook
- Data ingestion pipeline
- Quality validation tests
- Statistical reports

**Timeline**: 1-2 weeks from now

---

### Phase 2: Features ✅ COMPLETE

**Status**: ✅ Complete | **Time**: 16-20 hours

Engineer features for modeling.

- Feature pipelines
- Feature store (Feast)
- Online/offline features
- Feature monitoring

---

### Phase 3: Model Development ⏳ NEXT

**Status**: Starting Soon | **Time**: 16-20 hours

Train and optimize models.

- Multiple architectures
- Hyperparameter tuning
- MLflow experiment tracking
- Model comparison

---

### Phase 4: API & Serving 📋 Planned

**Status**: Planned | **Time**: 12-16 hours

Production prediction API.

- Prediction endpoints
- Batch inference
- Request validation
- Performance testing

---

### Phase 5: Frontend Dashboard 📋 Planned

**Status**: Planned | **Time**: 10-14 hours

Interactive user interface.

- Streamlit dashboard
- Real-time metrics
- Prediction interface
- Visualizations

---

### Phase 6: Monitoring & Deployment 📋 Planned

**Status**: Planned | **Time**: 16-20 hours

Deploy to production.

- Docker containerization
- CI/CD pipeline
- Kubernetes deployment
- Monitoring (Grafana)
- Drift detection

---

### Phase 7: Documentation 📋 Planned

**Status**: Planned | **Time**: 8-10 hours

Polish and document everything.

- Complete documentation
- Architecture diagrams
- Deployment guide
- Video walkthrough

---

### Phase 8: Advanced Topics 📋 Optional

**Status**: Optional | **Time**: Varies

Advanced production patterns.

- A/B testing
- Model ensembling
- Real-time features
- Cost optimization

---

## 🏗️ Architecture Overview

```
                    ┌─────────────┐
                    │   User UI   │
                    └──────┬──────┘
                           │
                    HTTP Requests
                           │
                           ▼
        ┌──────────────────────────────────┐
        │      FastAPI Backend             │
        │     (http://8000)                │
        │                                  │
        │ ┌─────────┐  ┌──────────────┐   │
        │ │Health   │  │ Prediction   │   │
        │ │Config   │  │ Endpoints    │   │
        │ └─────────┘  └──────────────┘   │
        └──────┬──────────────┬────────────┘
               │              │
          Data │              │ Metrics
               ▼              ▼
        ┌────────────┐  ┌──────────────┐
        │PostgreSQL  │  │  MLflow      │
        │(Port 5433) │  │ (Port 5001)  │
        │            │  │              │
        │ raw_data   │  │Experiments   │
        │ features   │  │Models        │
        │ models     │  │Artifacts     │
        └────────────┘  └──────────────┘
               │
               │ Version Control
               ▼
        ┌──────────────┐
        │     DVC      │
        │(Data Store)  │
        └──────────────┘
```

---

## 📦 Tech Stack Explained

### Backend

- **FastAPI** - Modern, fast async web framework
- **Pydantic** - Type validation and settings
- **SQLAlchemy** - Database ORM

### Database

- **PostgreSQL** - Production relational database
- **Schemas** - Organized data structure
- **PgAdmin** - Web UI for management

### MLOps

- **MLflow** - Experiment tracking and model registry
- **DVC** - Data and model versioning
- **ZenML** - ML pipeline orchestration (Phase 2+)

### Infrastructure

- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Bash Scripts** - Service management

### Deployment (Future)

- **Kubernetes** - Container orchestration
- **GitHub Actions** - CI/CD pipeline
- **Hugging Face** - Model hosting

---

## 💻 Services & Ports

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **FastAPI** | 8000 | <http://127.0.0.1:8000> | REST API |
| **Swagger UI** | 8000 | <http://127.0.0.1:8000/docs> | API Documentation |
| **MLflow** | 5001 | <http://127.0.0.1:5001> | Experiment Tracking |
| **PostgreSQL** | 5433 | 127.0.0.1:5433 | Database |
| **PgAdmin** | 5050 | <http://127.0.0.1:5050> | Database Manager |

### Database Credentials

```
Host: 127.0.0.1
Port: 5433
Username: frauduser
Password: fraudpass123
Database: fraud_detection
```

---

## 🎓 Learning Resources Included

### Documentation

- **Phase 0 Complete Learning Guide** (1,245 lines)
  - Deep dive into each technology
  - Architecture explanations
  - Best practices applied
  
- **Comprehensive README** (1,500+ lines)
  - Quick start guide
  - Full phase breakdown
  - Troubleshooting guide

### External Resources

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) (Official)
- [Docker Curriculum](https://docker-curriculum.com/) (Free)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/) (Free)
- [MLflow Documentation](https://mlflow.org/docs/) (Official)
- [DVC Guide](https://dvc.org/doc) (Official)

---

## 📚 What You'll Learn

### Week 1-2: Foundation

- ✅ Docker containerization
- ✅ API development (FastAPI)
- ✅ Database design (PostgreSQL)
- ✅ Configuration management

### Week 3-4: Data

- 📊 Data exploration (Pandas)
- 📊 Statistical analysis
- 📊 Data validation
- 📊 Dataset versioning

### Week 5-6: Features

- 🛠️ Feature engineering
- 🛠️ Feature stores
- 🛠️ Feature monitoring

### Week 7-8: Models

- 🤖 Model training
- 🤖 Experiment tracking
- 🤖 Model evaluation
- 🤖 Hyperparameter optimization

### Week 9-10: API

- 🔌 Prediction endpoints
- 🔌 Request validation
- 🔌 API testing
- 🔌 Performance optimization

### Week 11-12: Frontend

- 📱 Dashboard creation
- 📱 Real-time metrics
- 📱 Interactive visualizations

### Week 13-14: Deployment

- 🚀 Production deployment
- 🚀 CI/CD pipelines
- 🚀 Monitoring and alerting
- 🚀 Incident response

### Week 15: Polish

- 📖 Documentation
- 📖 Architecture diagrams
- 📖 Deployment guides

---

## 🚀 Getting Started

### Day 1: Setup ✅

```bash
./start.sh              # Start services
./health_check.sh       # Verify everything
curl http://127.0.0.1:8000/health  # Test API
```

### Day 2-3: Explore

- Read Phase 0 Learning Guide (2-3 hours)
- Understand the architecture
- Review best practices
- Examine the code

### Day 4-5: Experiment

- Add a new FastAPI endpoint
- Create a database table
- Log to MLflow
- Write a test

### Week 2+: Phase 1

- Download fraud dataset
- Create EDA notebook
- Build data pipeline
- Track with DVC

---

## 🔧 Common Commands

```bash
# Service Management
./start.sh              # Start all services
./stop.sh               # Stop all services
./status.sh             # Check service status
./health_check.sh       # Verify all healthy
./restart.sh            # Restart services

# Database
psql -h 127.0.0.1 -p 5433 -U frauduser -d fraud_detection

# Logs
tail -f logs/api.log
tail -f logs/mlflow.log

# DVC
uv run dvc status
uv run dvc push
uv run dvc pull

# Testing
uv run pytest
uv run pytest --cov=backend

# Code Quality
uv run black .
uv run ruff check .
```

---

## 📖 Documentation Structure

```
docs/
├── PHASE_0_LEARNING.md      # Deep learning guide (1,245 lines)
├── PROGRESS.md              # Phase completion tracking
├── ARCHITECTURE.md          # System design (coming Phase 6)
├── DEPLOYMENT.md            # Production deployment (coming Phase 6)
└── API_REFERENCE.md         # API documentation (coming Phase 4)
```

---

## ✅ Phase 0 Status

| Component | Status | Details |
|-----------|--------|---------|
| FastAPI Backend | ✅ Running | Port 8000, health checks working |
| PostgreSQL Database | ✅ Running | Port 5433, schemas created |
| MLflow Tracking | ✅ Running | Port 5001, ready for experiments |
| PgAdmin | ✅ Running | Port 5050, database UI |
| DVC Versioning | ✅ Ready | Local remote at ~/dvc-storage |
| Service Scripts | ✅ Ready | Production-grade with retries |
| Documentation | ✅ Complete | 3,400+ lines, comprehensive |

**Next Phase**: Model Development (Phase 3)

---

## 🎯 Success Metrics

You'll know Phase 0 is complete when:

- ✅ `./start.sh` starts all services successfully
- ✅ `./health_check.sh` shows all services healthy
- ✅ Database connects and responds
- ✅ API serves predictions
- ✅ MLflow tracks experiments
- ✅ DVC versions datasets
- ✅ You understand the architecture

**Current Status**: ✅ ALL COMPLETE

---

## 🤝 Contributing

Want to improve this project?

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Make changes
4. Commit (`git commit -m 'feat: add improvement'`)
5. Push (`git push origin feature/improvement`)
6. Open Pull Request

---

## 📄 License

MIT License - feel free to use this for learning, projects, and portfolios.

---

## 🎓 Learning Path Summary

**Total Time**: ~110-130 hours (4-5 months)

| Phase | Hours | Status |
|-------|-------|--------|
| Phase 0 | 8-12h | ✅ Complete |
| Phase 1 | 12-16h | ✅ Complete |
| Phase 2 | 16-20h | ✅ Complete |
| Phase 3 | 16-20h | ⏳ Next |
| Phase 4 | 12-16h | 📋 Planned |
| Phase 5 | 10-14h | 📋 Planned |
| Phase 6 | 16-20h | 📋 Planned |
| Phase 7 | 8-10h | 📋 Planned |

---

## 🆘 Troubleshooting

### Services won't start?

```bash
./stop.sh               # Cleanup
docker ps              # Check containers
docker logs <container> # View logs
./start.sh              # Try again
```

### Database connection failed?

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql -h 127.0.0.1 -p 5433 -U frauduser -d fraud_detection
```

### Need help?

- Read the full README (1,500+ lines)
- Check Troubleshooting section
- See learning resources above

---

## 📞 Questions?

- **Technical**: Check documentation or GitHub issues
- **Learning**: See resources section
- **Feedback**: Open an issue or discussion

---

## 🎉 You're All Set

Everything is ready for Phase 3. Here's your next steps:

1. ✅ Review the `feature_repo/` Feast configuration
2. 📖 Read `reports/features_profile.html`
3. 🔍 Explore `data/processed/text_features.parquet`
4. 📅 Plan Phase 3 Model Development
5. 🚀 Begin Phase 3: Model Development

---

**Built with ❤️ for learning production ML systems**

⭐ Star this repo if it helped you!
