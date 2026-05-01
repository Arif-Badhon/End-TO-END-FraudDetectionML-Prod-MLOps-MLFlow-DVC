# Phase 1: Data & EDA Learning Guide

Welcome to the deep-dive learning guide for Phase 1! In this phase, we transitioned from infrastructure to actually understanding and processing our data.

## 1. Exploratory Data Analysis (EDA)
EDA is the critical first step in any ML project. Before building models, you must understand the shape, distribution, and quality of your data.
- **Pandas:** The workhorse for data manipulation in Python. We used it to load `.parquet` files, inspect column types, and aggregate statistics.
- **Handling Missing Values:** We identified that features like `mda` (Management's Discussion and Analysis) had missing values and mapped strategies to handle them (e.g., dropping or imputing).
- **Class Imbalance:** Fraud datasets are notoriously imbalanced (e.g., 99% normal, 1% fraud). Identifying this early dictates our modeling strategies (using SMOTE, class weights, or tree-based algorithms) and evaluation metrics (using PR-AUC instead of Accuracy).

## 2. Automated Data Profiling
- **ydata-profiling:** Generating manual plots for every feature is time-consuming. We utilized `ydata-profiling` to automatically generate comprehensive HTML reports covering correlations, missing values, and distributions.

## 3. Data Validation with Great Expectations (GX)
"Garbage in, garbage out." In production, data changes constantly.
- **What is GX?** Great Expectations is a tool for data quality validation, testing, and profiling.
- **Expectations:** We define rules (e.g., "column X must be between 0 and 100", "column Y must not be null"). If new data violates these rules, the pipeline fails before training a bad model.

## 4. DVC Pipeline Integration
We integrated our data validation scripts into a reproducible DVC pipeline.
- `scripts/merge_data.py`: Centralized ingestion script.
- `scripts/validate_data_ge.py`: Runs GX validations.
- **Why this matters:** We guarantee that any data entering Phase 2 has passed stringent quality gates, tracked directly via Git and DVC.
