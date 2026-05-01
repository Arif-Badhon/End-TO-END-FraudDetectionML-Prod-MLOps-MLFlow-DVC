# API Reference

This document outlines the REST API endpoints provided by the FastAPI backend (available at `http://127.0.0.1:8000`).
*Full interactive documentation is always available via Swagger UI at `/docs`.*

## Base Endpoints

### `GET /health`
Verifies that the API and its dependent services (Database, MLflow) are accessible and operational.
**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "mlflow": "reachable",
  "timestamp": "2024-03-15T12:00:00Z"
}
```

## Prediction Endpoints

### `POST /api/v1/predict/single`
Submit a single record for real-time fraud scoring.

**Request Body:**
```json
{
  "cik": 123456,
  "filing_type": "10-K",
  "mda_text": "Management's discussion and analysis of financial condition..."
}
```

**Response:**
```json
{
  "prediction": 1,
  "probability": 0.87,
  "model_version": "v1.2.0",
  "features_used": {
    "mda_word_count": 5420,
    "mda_lexical_diversity": 0.35
  }
}
```

### `POST /api/v1/predict/batch`
Submit an array of records for batch processing.

**Request Body:**
```json
{
  "records": [
    { "cik": 123456, "filing_type": "10-K", "mda_text": "..." },
    { "cik": 789012, "filing_type": "10-Q", "mda_text": "..." }
  ]
}
```

**Response:**
```json
{
  "predictions": [
    { "cik": 123456, "prediction": 1, "probability": 0.87 },
    { "cik": 789012, "prediction": 0, "probability": 0.05 }
  ],
  "batch_size": 2,
  "processing_time_ms": 145
}
```
