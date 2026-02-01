"""
Schema Validation Script
========================

Purpose:
    Validate the structure and format of raw data files before processing.
    This is the FIRST step in the data pipeline - fail fast if schema is wrong.

Why This Matters:
    - Prevents downstream errors (garbage in = garbage out)
    - Catches data format changes early (e.g., if source system changes schema)
    - Documents expected data structure (self-documenting code)
    - Similar to how Netflix/Uber validate data at ingestion boundaries

Big Tech Pattern:
    "Schema validation at data boundaries" - validate data structure
    at every system boundary to prevent cascading failures.

Author: Your Name
Date: February 01, 2026
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

import pandas as pd
import yaml

# =============================================================================
# SETUP LOGGING
# =============================================================================
# Why logging instead of print():
# - Logs can be filtered by level (INFO, WARNING, ERROR)
# - Logs can be written to files for debugging
# - Production systems use logs, not prints
# - Can be integrated with monitoring systems (Phase 6)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# LOAD CONFIGURATION
# =============================================================================
def load_params(params_file: str = "params.yaml") -> Dict[str, Any]:
    """
    Load pipeline parameters from YAML configuration.
    
    Why YAML for config?
    - Human-readable (vs JSON)
    - Supports comments (documentation)
    - Industry standard (Kubernetes, Docker Compose, etc.)
    - Easy to version control
    
    Args:
        params_file: Path to parameters YAML file
        
    Returns:
        Dictionary of configuration parameters
        
    Raises:
        FileNotFoundError: If params.yaml doesn't exist
        yaml.YAMLError: If YAML syntax is invalid
    """
    try:
        with open(params_file, 'r') as f:
            params = yaml.safe_load(f)
        logger.info(f"✓ Loaded configuration from {params_file}")
        return params
    except FileNotFoundError:
        logger.error(f"✗ Configuration file not found: {params_file}")
        logger.error("  Please create params.yaml in project root")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"✗ Invalid YAML syntax in {params_file}: {e}")
        sys.exit(1)


# =============================================================================
# SCHEMA VALIDATION FUNCTIONS
# =============================================================================

def validate_csv_schema(
    csv_path: str,
    expected_columns: List[str]
) -> Tuple[bool, str]:
    """
    Validate CSV file structure.
    
    Checks:
    1. File exists and is readable
    2. File is valid CSV format
    3. Expected columns are present
    4. File has data (not empty)
    
    Args:
        csv_path: Path to CSV file
        expected_columns: List of expected column names
        
    Returns:
        Tuple of (validation_passed: bool, message: str)
    """
    logger.info(f"Validating CSV schema: {csv_path}")
    
    # Check 1: File exists
    if not Path(csv_path).exists():
        return False, f"File not found: {csv_path}"
    
    try:
        # Check 2: Valid CSV format
        # Why nrows=5? Just need to validate structure, not load entire file
        df = pd.read_csv(csv_path, nrows=5)
        
        # Check 3: Expected columns present
        # Why set()? Order doesn't matter, just presence
        actual_columns = set(df.columns)
        expected_set = set(expected_columns)
        
        missing_columns = expected_set - actual_columns
        if missing_columns:
            return False, f"Missing columns: {missing_columns}"
        
        # Check 4: File has data
        df_full = pd.read_csv(csv_path)
        if len(df_full) == 0:
            return False, "CSV file is empty (0 rows)"
        
        logger.info(f"  ✓ CSV schema valid: {len(df_full)} rows, {len(df_full.columns)} columns")
        return True, f"Valid CSV with {len(df_full)} rows"
        
    except pd.errors.EmptyDataError:
        return False, "CSV file is empty"
    except pd.errors.ParserError as e:
        return False, f"CSV parsing error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def validate_json_schema(
    json_path: str,
    expected_keys: List[str],
    sample_size: int = 5
) -> Tuple[bool, str]:
    """
    Validate JSON file structure.
    
    Why this is complex:
    - JSON can be nested (unlike flat CSV)
    - Need to validate structure of nested objects
    - Large JSON files need sampling (can't load all in memory)
    
    Checks:
    1. File exists and is readable
    2. File is valid JSON format
    3. Top-level structure is correct (dict of dicts)
    4. Sample entries have expected keys
    5. File has data (not empty)
    
    Args:
        json_path: Path to JSON file
        expected_keys: List of expected keys in nested objects
        sample_size: Number of entries to validate (default 5)
        
    Returns:
        Tuple of (validation_passed: bool, message: str)
    """
    logger.info(f"Validating JSON schema: {json_path}")
    
    # Check 1: File exists
    if not Path(json_path).exists():
        return False, f"File not found: {json_path}"
    
    try:
        # Check 2: Valid JSON format
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Check 3: Top-level structure
        if not isinstance(data, dict):
            return False, f"Expected dict at top level, got {type(data)}"
        
        # Check 4: Not empty
        if len(data) == 0:
            return False, "JSON file is empty (0 entries)"
        
        # Check 5: Sample entries have expected keys
        # Why sample? Large JSON files (89K entries) - don't need to check all
        sample_keys = list(data.keys())[:sample_size]
        
        for key in sample_keys:
            entry = data[key]
            
            # Validate nested structure
            if not isinstance(entry, dict):
                return False, f"Entry '{key}' is not a dict: {type(entry)}"
            
            # Check for expected keys
            actual_keys = set(entry.keys())
            expected_set = set(expected_keys)
            missing_keys = expected_set - actual_keys
            
            if missing_keys:
                return False, f"Entry '{key}' missing keys: {missing_keys}"
        
        logger.info(f"  ✓ JSON schema valid: {len(data)} entries")
        return True, f"Valid JSON with {len(data)} entries"
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def validate_firm_years_structure(
    json_path: str,
    expected_ratio_features: List[str],
    sample_size: int = 5
) -> Tuple[bool, str]:
    """
    Validate firm_years.json nested structure (financial_ratios).
    
    This is SPECIFIC to our dataset structure:
    {
        "firm_123_2005": {
            "year": 2005,
            "cik": "123",
            "mda_text": "...",
            "financial_ratios": {
                "current_ratio": 1.5,
                "debt_to_equity": 0.8,
                ...
            }
        }
    }
    
    Why separate function?
    - firm_years.json has nested "financial_ratios" dict
    - Need to validate this nested structure
    - Different from labels.json (flat structure)
    
    Args:
        json_path: Path to firm_years.json
        expected_ratio_features: List of expected financial ratio names
        sample_size: Number of entries to validate
        
    Returns:
        Tuple of (validation_passed: bool, message: str)
    """
    logger.info(f"Validating firm_years nested structure: {json_path}")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Sample entries to validate
        sample_keys = list(data.keys())[:sample_size]
        
        for key in sample_keys:
            entry = data[key]
            
            # Check 1: Has financial_ratios key
            if 'financial_ratios' not in entry:
                return False, f"Entry '{key}' missing 'financial_ratios' key"
            
            # Check 2: financial_ratios is a dict
            ratios = entry['financial_ratios']
            if not isinstance(ratios, dict):
                return False, f"Entry '{key}' financial_ratios is not dict: {type(ratios)}"
            
            # Check 3: Has expected ratio features
            actual_ratios = set(ratios.keys())
            expected_set = set(expected_ratio_features)
            missing_ratios = expected_set - actual_ratios
            
            # Why allow some missing? Real data may have NULL values
            # But should have at least 80% of expected features
            coverage = len(actual_ratios & expected_set) / len(expected_set)
            if coverage < 0.8:
                return False, (
                    f"Entry '{key}' has only {coverage:.1%} of expected ratios. "
                    f"Missing: {missing_ratios}"
                )
            
            # Check 4: MDA text exists and is non-empty
            mda_text = entry.get('mda_text', '')
            if not isinstance(mda_text, str) or len(mda_text) < 10:
                return False, f"Entry '{key}' has invalid or empty MDA text"
        
        logger.info(f"  ✓ firm_years nested structure valid")
        return True, "Valid nested structure"
        
    except Exception as e:
        return False, f"Validation error: {e}"


# =============================================================================
# MAIN VALIDATION ORCHESTRATOR
# =============================================================================

def run_schema_validation(params: Dict[str, Any]) -> bool:
    """
    Run all schema validations.
    
    This is the ORCHESTRATOR function that:
    1. Validates AAER CSV
    2. Validates labels JSON
    3. Validates firm_years JSON (with nested structure)
    4. Creates validation marker file if all pass
    
    Why marker file?
    - DVC pipeline needs to know validation passed
    - Marker file = validation output artifact
    - DVC can track this dependency for next stage
    
    Args:
        params: Configuration parameters from params.yaml
        
    Returns:
        True if all validations pass, False otherwise
    """
    logger.info("=" * 80)
    logger.info("STARTING SCHEMA VALIDATION")
    logger.info("=" * 80)
    
    all_passed = True
    
    # -------------------------------------------------------------------------
    # VALIDATION 1: AAER CSV
    # -------------------------------------------------------------------------
    aaer_path = params['data']['raw']['aaer']
    expected_aaer_cols = params['schema_validation']['aaer_columns']
    
    passed, message = validate_csv_schema(aaer_path, expected_aaer_cols)
    if passed:
        logger.info(f"✓ AAER CSV validation PASSED: {message}")
    else:
        logger.error(f"✗ AAER CSV validation FAILED: {message}")
        all_passed = False
    
    # -------------------------------------------------------------------------
    # VALIDATION 2: Labels JSON
    # -------------------------------------------------------------------------
    labels_path = params['data']['raw']['labels']
    # Labels JSON is simple: {"firm_year_id": {"fraud_label": 0/1, ...}}
    # Just check it's valid JSON with entries
    
    passed, message = validate_json_schema(
        labels_path,
        expected_keys=['fraud_label'],  # Minimum required key
        sample_size=5
    )
    if passed:
        logger.info(f"✓ Labels JSON validation PASSED: {message}")
    else:
        logger.error(f"✗ Labels JSON validation FAILED: {message}")
        all_passed = False
    
    # -------------------------------------------------------------------------
    # VALIDATION 3: Firm Years JSON (with nested structure)
    # -------------------------------------------------------------------------
    features_path = params['data']['raw']['features']
    expected_keys = params['schema_validation']['firm_years_required_keys']
    expected_ratios = params['schema_validation']['financial_ratio_features']
    
    # First validate top-level structure
    passed, message = validate_json_schema(
        features_path,
        expected_keys=expected_keys,
        sample_size=5
    )
    if not passed:
        logger.error(f"✗ Firm years JSON validation FAILED: {message}")
        all_passed = False
    else:
        logger.info(f"✓ Firm years JSON top-level validation PASSED: {message}")
        
        # Then validate nested financial_ratios structure
        passed, message = validate_firm_years_structure(
            features_path,
            expected_ratio_features=expected_ratios,
            sample_size=5
        )
        if passed:
            logger.info(f"✓ Firm years nested structure validation PASSED: {message}")
        else:
            logger.error(f"✗ Firm years nested structure validation FAILED: {message}")
            all_passed = False
    
    # -------------------------------------------------------------------------
    # CREATE MARKER FILE IF ALL VALIDATIONS PASSED
    # -------------------------------------------------------------------------
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


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    """
    Main entry point for schema validation script.
    
    Usage:
        python scripts/validate_schema.py
    
    Exit codes:
        0: Success (all validations passed)
        1: Failure (one or more validations failed)
    """
    # Load configuration
    params = load_params()
    
    # Run validations
    success = run_schema_validation(params)
    
    # Exit with appropriate code
    # Why exit codes? DVC pipeline needs to know if script succeeded
    sys.exit(0 if success else 1)
