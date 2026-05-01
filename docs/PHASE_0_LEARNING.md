# Phase 0: Foundation Learning Guide

Welcome to the deep-dive learning guide for Phase 0 of the Fraud Detection ML System! In this phase, we laid the critical MLOps and Backend foundations necessary for a production-grade ML system.

## 1. FastAPI (Backend API)
FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.8+ based on standard Python type hints.
- **Why we use it:** It's incredibly fast, provides automatic interactive documentation (Swagger UI), and supports asynchronous programming out of the box.
- **Key Concepts:**
  - **Pydantic Models:** Used for data validation and settings management.
  - **Dependency Injection:** Helps in managing database sessions securely and cleanly.
  - **Routers:** We organize our prediction and health endpoints into modular routers.

## 2. PostgreSQL (Database)
PostgreSQL is a powerful, open-source object-relational database system.
- **Why we use it:** Instead of relying on flat CSV files, production systems use relational databases to handle concurrent reads/writes, enforce data integrity, and manage schemas.
- **Schemas:** We organize our data into schemas:
  - `raw_data`: For initial, unprocessed filings.
  - `features`: For engineered features ready for modeling.
  - `models`: For model metadata.

## 3. MLflow (Experiment Tracking & Registry)
MLflow is an open-source platform to manage the ML lifecycle, including experimentation, reproducibility, deployment, and a central model registry.
- **Why we use it:** To track hyperparameters, metrics, and artifacts across multiple training runs, and to version our models.
- **Components:**
  - **Tracking Server:** Logs runs and metrics.
  - **Artifact Store:** Stores the actual model binary files (`.pkl`, etc.).
  - **Model Registry:** Manages the lifecycle of a model (Staging, Production, Archived).

## 4. DVC (Data Version Control)
DVC is built to make ML models shareable and reproducible. It is designed to handle large files, data sets, machine learning models, and metrics as well as code.
- **Why we use it:** Git is not meant for storing gigabytes of data. DVC tracks the data metadata (`.dvc` files) in Git, while the heavy files are stored in a remote storage backend (like AWS S3 or a local remote).
- **Pipelines (`dvc.yaml`):** Automates the steps from data ingestion to feature engineering, ensuring reproducibility.

## 5. Docker & Infrastructure
Docker allows us to package the application with all of its dependencies into a standardized unit for software development.
- **Why we use it:** "It works on my machine" is a thing of the past. Docker ensures consistency across development, staging, and production environments.
- **Docker Compose:** Used to spin up PostgreSQL, PgAdmin, and eventually our FastAPI and MLflow services simultaneously.

## Best Practices Learned
- **Infrastructure as Code (IaC):** Defining our services in code.
- **Health Checks:** Implementing `/health` endpoints to ensure services are ready before traffic is routed to them.
- **Separation of Concerns:** Decoupling the database layer, the ML layer, and the API layer.
