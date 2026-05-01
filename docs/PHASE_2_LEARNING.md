# Phase 2: Features Learning Guide

Welcome to Phase 2! In this phase, we transformed raw data into meaningful signals (features) and set up a Feature Store to serve them.

## 1. Feature Engineering (NLP & Text Metrics)
Since fraud often hides in the nuances of financial filings, we extracted features from the MD&A (Management's Discussion and Analysis) text.
- **Text Length & Word Count:** Basic structural signals. Unusually short or long filings can indicate anomalies.
- **Lexical Diversity:** Measures the richness of the vocabulary.
- **Readability Scores (Flesch Reading Ease):** Obfuscation is a common tactic in fraud. Hard-to-read filings might intentionally hide poor performance.
- **Financial Term Density:** Counting the frequency of terms like "revenue", "loss", and "liability" normalizes the context of the filing.

## 2. Feature Stores (Feast)
In production, features need to be shared across teams, served to models in real-time with low latency, and retrieved historically for training without "point-in-time" leakage.
- **What is Feast?** An open-source feature store. It acts as a bridge between data engineering and machine learning.
- **Offline Store:** Used for batch training. Feast manages the historical retrieval of our `.parquet` features, ensuring we don't accidentally leak future data into our training set.
- **Online Store (SQLite/Redis):** Used for low-latency inference. When the API receives a request to score Company A, Feast rapidly retrieves Company A's pre-computed features from the online store.
- **Feature Views:** We defined logical groupings of our extracted text features, assigning a TTL (Time-To-Live) to dictate how long a feature value is considered "fresh".

## 3. Feature Monitoring
Features drift over time as business environments change.
- We set up a pipeline step using `ydata-profiling` to continuously monitor the distribution of our extracted features. This ensures that the distributions our models were trained on match the distributions seen in production.
