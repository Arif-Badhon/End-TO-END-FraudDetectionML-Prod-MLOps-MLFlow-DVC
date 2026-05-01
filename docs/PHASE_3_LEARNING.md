# Phase 3: Model Development Learning Guide

Welcome to Phase 3! This is where we build the "brain" of the system.

## 1. Handling Imbalanced Data
Fraud detection is the classic imbalanced classification problem.
- **Metrics:** Accuracy is useless (predicting "No Fraud" always yields 99% accuracy). We use **Precision**, **Recall**, **F1-Score**, and **PR-AUC** (Precision-Recall Area Under Curve).
- **Techniques:** We will explore techniques such as:
  - Class Weighting in tree algorithms (e.g., `scale_pos_weight` in XGBoost).
  - Resampling (SMOTE for oversampling, or random undersampling).

## 2. Algorithm Selection
- **XGBoost & LightGBM:** Gradient boosted trees are highly effective for tabular data with mixed numerical and categorical features. They are robust to outliers and require minimal scaling.
- **Random Forest:** A strong, robust baseline model that provides excellent feature importance interpretability.

## 3. Hyperparameter Tuning
- We utilize libraries like **Optuna** or **Hyperopt** to systematically search for the optimal model hyperparameters, maximizing our PR-AUC metric.

## 4. MLflow Experiment Tracking
Model development is an iterative science.
- **Tracking:** We log every run to MLflow, recording parameters (learning rate, max depth), metrics (F1, PR-AUC), and the model artifacts themselves.
- **Model Registry:** Once we identify a winning model, we register it in MLflow's Model Registry, transitioning its state to "Staging" for evaluation, and eventually "Production".

## 5. Model Evaluation & Explainability
- **SHAP (SHapley Additive exPlanations):** In finance, "black box" models are often unacceptable. We use SHAP values to explain *why* the model flagged a specific filing as fraudulent, providing transparency to end-users and compliance teams.
