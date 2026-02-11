from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import yaml
import great_expectations as gx
import great_expectations.expectations as gxe
from great_expectations.core.expectation_suite import ExpectationSuite

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("validate_data_ge")


def load_params(path: str = "params.yaml") -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def require_columns(df: pd.DataFrame, required: List[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def get_or_create_suite(context, suite_name: str) -> ExpectationSuite:
    # GX 1.x manages suites via context.suites [web:195]
    try:
        return context.suites.get(name=suite_name)
    except Exception:
        suite = ExpectationSuite(name=suite_name)
        return context.suites.add(suite)


def main() -> int:
    params = load_params()

    parquet_path = Path(params["data"]["interim"]["firm_years_with_labels"])
    report_dir = Path("reports")
    report_path = report_dir / "gx_validation_report.json"

    if not parquet_path.exists():
        logger.error("Missing parquet: %s", parquet_path)
        return 1

    df = pd.read_parquet(parquet_path)
    logger.info("Loaded parquet: shape=%s", df.shape)

    # 1) Quick “contract” check outside GX (fast + clear errors)
    required_cols = [
        "cik", "name", "filing_date", "reporting_date", "url", "mda",
        "is_fraud", "fraud_aaer_no", "fraud_start", "fraud_end",
    ]
    require_columns(df, required_cols)

    # 2) Load file-based GX context (persists config on disk) [web:140]
    context = gx.get_context(mode="file")

    # 3) Create/get a Pandas datasource + DataFrame asset, then materialize a Batch [web:116]
    ds_name = "pandas_src"
    asset_name = "firm_years_labeled_asset"
    batch_def_name = "whole_dataframe"

    try:
        data_source = context.data_sources.add_pandas(name=ds_name)
    except Exception:
        data_source = context.data_sources.get(ds_name)

    # The asset defines the “kind” of data; the batch supplies the actual DataFrame at runtime.
    try:
        asset = data_source.add_dataframe_asset(name=asset_name)
    except Exception:
        asset = data_source.get_asset(asset_name)

    try:
        batch_def = asset.add_batch_definition_whole_dataframe(name=batch_def_name)
    except Exception:
        batch_def = asset.get_batch_definition(batch_def_name)

    batch = batch_def.get_batch(batch_parameters={"dataframe": df})

    # 4) Define an expectation suite and populate it with expectations (GX 1.x style) [web:195]
    suite_name = "firm_years_labeled_suite"
    suite = get_or_create_suite(context, suite_name)

    # Optional: reset suite expectations each run (keeps script deterministic)
    suite.expectations = []

    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="cik"))
    suite.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="cik", min_value=0, max_value=9_999_999))

    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="is_fraud"))
    suite.add_expectation(gxe.ExpectColumnValuesToBeInSet(column="is_fraud", value_set=[0, 1]))

    suite.add_expectation(gxe.ExpectColumnValuesToMatchRegex(column="url", regex=r"^https?://", mostly=0.99))

    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="mda", mostly=0.70))
    suite.add_expectation(
        gxe.ExpectColumnValueLengthsToBeBetween(column="mda", min_value=100, max_value=1_000_000, mostly=0.70)
    )

    suite.save()  # persists suite in gx/ store [web:195]

    # 5) Validate: Batch.validate(suite) [web:223]
    result = batch.validate(suite)

    report_dir.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(result.to_json_dict(), f, indent=2)

    logger.info("GX validation success=%s; report=%s", bool(result.success), report_path)
    return 0 if result.success else 2


if __name__ == "__main__":
    raise SystemExit(main())
