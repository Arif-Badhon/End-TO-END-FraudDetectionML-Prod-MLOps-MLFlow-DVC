"""
Step 2: Data Merging
====================

Goal:
    Take the raw SEC fraud cases (AAER CSV) and firm-year filings (JSON),
    and produce ONE labeled dataset for modeling.

High-level:
    1) Load config (params.yaml)
    2) Build fraud lookup from AAER (by CIK)
    3) Load firm_years_labels.json (list of filings)
    4) For each filing, attach fraud label + AAER metadata
    5) Save as Parquet in data/interim/

This script is intentionally written in a teaching style:
    - Small, clear functions
    - Explicit logging
    - No fancy abstractions
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import yaml


# -----------------------------------------------------------------------------
# 1. Logging setup
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# -----------------------------------------------------------------------------
# 2. Config loader
# -----------------------------------------------------------------------------
def load_params(params_file: str = "params.yaml") -> Dict[str, Any]:
    """
    Load pipeline configuration.

    Why:
        - Central place for paths and thresholds
        - Makes script reusable across environments
    """
    try:
        with open(params_file, "r") as f:
            params = yaml.safe_load(f)
        logger.info("✓ Loaded configuration from %s", params_file)
        return params
    except FileNotFoundError:
        logger.error("✗ Configuration file not found: %s", params_file)
        sys.exit(1)


# -----------------------------------------------------------------------------
# 3. Build fraud index from AAER CSV
# -----------------------------------------------------------------------------
def load_aaer_as_fraud_index(
    csv_path: Path,
    delimiter: str = ";",
) -> Dict[int, Dict[str, Any]]:
    """
    Load AAER CSV and build a lookup by CIK.

    Output structure (example):
        {
            123456: {
                "aaerNo": "AAER-1234",
                "fraud_start": "2005-01-01",
                "fraud_end": "2008-12-31",
                "dateTime": "...",
                ...
            },
            ...
        }

    Why:
        - Fast CIK → fraud info lookup when labeling firm-year filings
    """
    logger.info("Loading AAER CSV from %s", csv_path)

    if not csv_path.exists():
        logger.error("AAER CSV not found: %s", csv_path)
        sys.exit(1)

    # Read entire AAER file (570 rows, small enough)
    df = pd.read_csv(csv_path, sep=delimiter)

    # Normalize CIK to integer where possible, drop rows without CIK
    # (We keep it simple; later we could handle strings if needed.)
    if "cik" not in df.columns:
        logger.error("AAER CSV missing 'cik' column")
        sys.exit(1)

    # Drop rows with missing CIK
    df = df.dropna(subset=["cik"])

    # Convert to int safely (coerce errors, then drop invalid)
    df["cik"] = pd.to_numeric(df["cik"], errors="coerce")
    df = df.dropna(subset=["cik"])
    df["cik"] = df["cik"].astype(int)

    logger.info("AAER CSV: %d rows with valid CIK", len(df))

    # Build fraud index
    fraud_index: Dict[int, Dict[str, Any]] = {}
    for _, row in df.iterrows():
        cik = int(row["cik"])

        # We keep a subset of useful fields; you can expand this later
        fraud_entry = {
            "aaerNo": row.get("aaerNo"),
            "fraud_start": row.get("fraud_start"),
            "fraud_end": row.get("fraud_end"),
            "dateTime": row.get("dateTime"),
            "releaseNo": row.get("releaseNo"),
        }

        # If same CIK appears multiple times, last one wins (simple rule for now)
        fraud_index[cik] = fraud_entry

    logger.info("Built fraud index for %d unique CIKs", len(fraud_index))
    return fraud_index


# -----------------------------------------------------------------------------
# 4. Load firm_years_labels and attach fraud labels
# -----------------------------------------------------------------------------
def load_firm_years_labels(
    json_path: Path,
) -> List[Dict[str, Any]]:
    """
    Load firm_years_labels.json as a list of dicts.

    Why:
        - This is our main modeling dataset (10,764 filings)
        - We will enrich each entry with fraud labels
    """
    logger.info("Loading firm_years_labels from %s", json_path)

    if not json_path.exists():
        logger.error("Labels JSON not found: %s", json_path)
        sys.exit(1)

    with open(json_path, "r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        logger.error("Expected list at top level in labels JSON, got %s", type(data))
        sys.exit(1)

    logger.info("Loaded %d labeled firm-year entries", len(data))
    return data


def enrich_with_fraud_labels(
    firm_years: List[Dict[str, Any]],
    fraud_index: Dict[int, Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Attach fraud labels and AAER metadata to each firm-year entry.

    Logic:
        - Parse CIK from entry
        - If CIK in fraud_index → is_fraud = 1, attach AAER fields
        - Else → is_fraud = 0

    Returns:
        - enriched list
        - number of fraud cases
        - number of non-fraud cases
    """
    logger.info("Enriching firm-year entries with fraud labels")

    enriched: List[Dict[str, Any]] = []
    fraud_count = 0
    non_fraud_count = 0

    for entry in firm_years:
        # Copy to avoid mutating original
        e = dict(entry)

        raw_cik = e.get("cik", None)
        cik_int = None

        # Normalize CIK to int (to match AAER index)
        if raw_cik is not None:
            try:
                cik_int = int(raw_cik)
            except (TypeError, ValueError):
                cik_int = None

        if cik_int is not None and cik_int in fraud_index:
            # Fraudulent company (according to AAER)
            e["is_fraud"] = 1
            fraud_meta = fraud_index[cik_int]

            # Attach a few AAER fields (names chosen for clarity)
            e["fraud_aaer_no"] = fraud_meta.get("aaerNo")
            e["fraud_start"] = fraud_meta.get("fraud_start")
            e["fraud_end"] = fraud_meta.get("fraud_end")
            e["fraud_case_datetime"] = fraud_meta.get("dateTime")
            e["fraud_release_no"] = fraud_meta.get("releaseNo")

            fraud_count += 1
        else:
            # Non-fraud (or unknown)
            e["is_fraud"] = 0
            e["fraud_aaer_no"] = None
            e["fraud_start"] = None
            e["fraud_end"] = None
            e["fraud_case_datetime"] = None
            e["fraud_release_no"] = None

            non_fraud_count += 1

        enriched.append(e)

    logger.info(
        "Labeling complete: %d fraud, %d non-fraud", fraud_count, non_fraud_count
    )
    return enriched, fraud_count, non_fraud_count


# -----------------------------------------------------------------------------
# 5. Save to parquet
# -----------------------------------------------------------------------------
def save_enriched_to_parquet(
    enriched: List[Dict[str, Any]],
    output_path: Path,
) -> None:
    """
    Save enriched firm-year data to parquet.

    Why parquet:
        - Columnar, compressed, efficient for analytics
        - Better than CSV for large datasets and repeated reads
    """
    logger.info("Saving enriched dataset to %s", output_path)

    # Convert to DataFrame
    df = pd.DataFrame(enriched)

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Let pandas choose the parquet engine (pyarrow/fastparquet)
    df.to_parquet(output_path, index=False)

    logger.info("Saved %d rows, %d columns", df.shape[0], df.shape[1])


# -----------------------------------------------------------------------------
# 6. Orchestration function
# -----------------------------------------------------------------------------
def run_merge_pipeline(params: Dict[str, Any]) -> None:
    """
    Main orchestration for Step 2.

    Reads:
        - data/raw/aaer_mark5.csv
        - data/raw/firm_years_labels.json

    Writes:
        - data/interim/firm_years_labeled.parquet
    """
    logger.info("=" * 80)
    logger.info("STARTING STEP 2: DATA MERGING (AAER + FIRM YEARS LABELS)")
    logger.info("=" * 80)

    # Resolve paths from params.yaml
    raw_paths = params["data"]["raw"]
    interim_paths = params["data"]["interim"]
    schema_cfg = params["schema_validation"]

    aaer_path = Path(raw_paths["aaer"])
    labels_path = Path(raw_paths["firm_years_labels"])
    output_path = Path(interim_paths["firm_years_with_labels"])
    csv_delimiter = schema_cfg.get("csv_delimiter", ";")

    # 1) Build fraud index from AAER CSV
    fraud_index = load_aaer_as_fraud_index(aaer_path, delimiter=csv_delimiter)

    # 2) Load firm_years_labels.json
    firm_years = load_firm_years_labels(labels_path)

    # 3) Enrich with fraud labels
    enriched, fraud_count, non_fraud_count = enrich_with_fraud_labels(
        firm_years, fraud_index
    )

    # Basic sanity check on label distribution
    total = fraud_count + non_fraud_count
    if total == 0:
        logger.error("No records to save (total=0). Aborting.")
        sys.exit(1)

    fraud_rate = fraud_count / total
    logger.info("Fraud rate in labeled dataset: %.4f (%.2f%%)", fraud_rate, fraud_rate * 100)

    # 4) Save to parquet
    save_enriched_to_parquet(enriched, output_path)

    logger.info("=" * 80)
    logger.info("STEP 2 COMPLETE: DATA MERGING FINISHED")
    logger.info("Output file: %s", output_path)
    logger.info("=" * 80)


# -----------------------------------------------------------------------------
# 7. CLI entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Usage:
        uv run python scripts/merge_data.py
    """
    params = load_params()
    try:
        run_merge_pipeline(params)
    except Exception as e:
        logger.exception("Unhandled error during merge pipeline: %s", e)
        sys.exit(1)
