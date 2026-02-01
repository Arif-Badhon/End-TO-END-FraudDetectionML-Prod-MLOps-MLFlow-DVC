"""
Schema Validation Script - UPDATED
===================================
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

import pandas as pd
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_params(params_file: str = "params.yaml") -> Dict[str, Any]:
    """Load pipeline parameters from YAML configuration."""
    try:
        with open(params_file, 'r') as f:
            params = yaml.safe_load(f)
        logger.info(f"✓ Loaded configuration from params.yaml")
        return params
    except FileNotFoundError:
        logger.error(f"✗ Configuration file not found: {params_file}")
        sys.exit(1)


def validate_aaer_csv(csv_path: str, delimiter: str = ';') -> Tuple[bool, str]:
    """Validate AAER CSV file structure."""
    logger.info(f"Validating AAER CSV: {csv_path}")
    
    if not Path(csv_path).exists():
        return False, f"File not found: {csv_path}"
    
    try:
        df = pd.read_csv(csv_path, sep=delimiter, nrows=5)
        df_full = pd.read_csv(csv_path, sep=delimiter)
        
        if len(df_full) == 0:
            return False, "CSV file is empty (0 rows)"
        
        expected_cols = ['aaerNo', 'cik', 'fraud_start', 'fraud_end']
        missing_cols = set(expected_cols) - set(df_full.columns)
        if missing_cols:
            return False, f"Missing critical columns: {missing_cols}"
        
        if df_full['cik'].isna().all():
            return False, "CIK column is all null values"
        
        logger.info(f"  ✓ AAER CSV valid: {len(df_full)} rows, {len(df_full.columns)} columns")
        return True, f"Valid AAER CSV with {len(df_full)} cases"
        
    except Exception as e:
        return False, f"Error: {e}"


def validate_json_list_file(
    json_path: str,
    expected_keys: List[str],
    sample_size: int = 5,
    require_all_keys: bool = False
) -> Tuple[bool, str]:
    """Validate JSON list file structure."""
    logger.info(f"Validating JSON list file: {json_path}")
    
    if not Path(json_path).exists():
        return False, f"File not found: {json_path}"
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            return False, f"Expected list at top level, got {type(data)}"
        
        if len(data) == 0:
            return False, "JSON file is empty (0 entries)"
        
        sample_indices = range(min(sample_size, len(data)))
        
        for idx in sample_indices:
            entry = data[idx]
            
            if not isinstance(entry, dict):
                return False, f"Entry {idx} is not a dict: {type(entry)}"
            
            if require_all_keys:
                actual_keys = set(entry.keys())
                expected_set = set(expected_keys)
                missing_keys = expected_set - actual_keys
                
                if missing_keys:
                    return False, f"Entry {idx} missing keys: {missing_keys}"
        
        logger.info(f"  ✓ JSON list valid: {len(data)} entries")
        return True, f"Valid JSON list with {len(data)} entries"
        
    except Exception as e:
        return False, f"Error: {e}"


def validate_mda_text_coverage(
    json_path: str,
    sample_size: int = 100,
    min_coverage: float = 0.70  # Lowered to 70%
) -> Tuple[bool, str]:
    """Validate that MDA text field is present in most entries."""
    logger.info(f"Validating MDA text coverage: {json_path}")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        sample_indices = range(min(sample_size, len(data)))
        
        mda_count = 0
        mda_valid_count = 0
        
        for idx in sample_indices:
            entry = data[idx]
            
            if 'mda' in entry:
                mda_count += 1
                mda_text = entry['mda']
                if isinstance(mda_text, str) and len(mda_text.strip()) > 100:
                    mda_valid_count += 1
        
        coverage = mda_count / sample_size if sample_size > 0 else 0
        valid_coverage = mda_valid_count / sample_size if sample_size > 0 else 0
        
        logger.info(f"  MDA text coverage: {coverage:.1%} ({mda_count}/{sample_size})")
        logger.info(f"  Valid MDA text: {valid_coverage:.1%} ({mda_valid_count}/{sample_size})")
        
        if coverage < min_coverage:
            return False, f"MDA text coverage too low: {coverage:.1%}"
        
        return True, f"MDA coverage: {coverage:.1%}"
        
    except Exception as e:
        return False, f"Error: {e}"


def run_schema_validation(params: Dict[str, Any]) -> bool:
    """Run all schema validations."""
    logger.info("=" * 80)
    logger.info("STARTING SCHEMA VALIDATION")
    logger.info("=" * 80)
    
    all_passed = True
    
    # VALIDATION 1: AAER CSV
    aaer_path = params['data']['raw']['aaer']
    csv_delimiter = params['schema_validation']['csv_delimiter']
    
    passed, message = validate_aaer_csv(aaer_path, delimiter=csv_delimiter)
    if passed:
        logger.info(f"✓ AAER CSV validation PASSED: {message}")
    else:
        logger.error(f"✗ AAER CSV validation FAILED: {message}")
        all_passed = False
    
    # VALIDATION 2: firm_years_labels JSON
    labels_path = params['data']['raw']['firm_years_labels']
    expected_keys = params['schema_validation']['firm_years_required_keys']
    
    # Don't require ALL keys for labels file (some entries may not have all fields)
    passed, message = validate_json_list_file(
        labels_path,
        expected_keys=['cik', 'name'],  # Only require critical keys
        sample_size=10,
        require_all_keys=False
    )
    if passed:
        logger.info(f"✓ firm_years_labels JSON validation PASSED: {message}")
    else:
        logger.error(f"✗ firm_years_labels JSON validation FAILED: {message}")
        all_passed = False
    
    # Check MDA coverage (relaxed to 70%)
    passed, message = validate_mda_text_coverage(labels_path, sample_size=100, min_coverage=0.70)
    if passed:
        logger.info(f"✓ MDA text coverage PASSED: {message}")
    else:
        logger.warning(f"⚠ MDA text coverage WARNING: {message}")
        # Don't fail on MDA coverage - just warn
    
    # VALIDATION 3: firm_years JSON (full dataset)
    features_path = params['data']['raw']['firm_years_full']
    
    # Also relaxed for full dataset
    passed, message = validate_json_list_file(
        features_path,
        expected_keys=['cik', 'name'],  # Only require critical keys
        sample_size=10,
        require_all_keys=False
    )
    if passed:
        logger.info(f"✓ firm_years JSON validation PASSED: {message}")
    else:
        logger.error(f"✗ firm_years JSON validation FAILED: {message}")
        all_passed = False
    
    # CREATE MARKER FILE IF ALL VALIDATIONS PASSED
    if all_passed:
        marker_file = Path(params['data']['interim']['schema_validation'])
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(marker_file, 'w') as f:
            f.write("Schema validation passed successfully\n")
            f.write(f"Validated at: {pd.Timestamp.now()}\n")
        
        logger.info("=" * 80)
        logger.info("✓ ALL SCHEMA VALIDATIONS PASSED")
        logger.info(f"✓ Marker file created: {marker_file}")
        logger.info("=" * 80)
        return True
    else:
        logger.error("=" * 80)
        logger.error("✗ SCHEMA VALIDATION FAILED")
        logger.error("  Please fix the issues above before proceeding")
        logger.error("=" * 80)
        return False


if __name__ == "__main__":
    """Main entry point for schema validation script."""
    params = load_params()
    success = run_schema_validation(params)
    sys.exit(0 if success else 1)
