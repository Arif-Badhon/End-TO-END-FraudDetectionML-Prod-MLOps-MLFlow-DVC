import pandas as pd
import yaml
import logging
from pathlib import Path
from ydata_profiling import ProfileReport

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_params():
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    params = load_params()
    
    input_path = params["data"]["processed"]["text_features"]
    output_dir = params["reporting"]["output_dir"]
    report_title = "Feature Monitoring Report - text_features"
    output_path = f"{output_dir}/features_profile.html"
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    logging.info(f"Loading features from {input_path}")
    df = pd.read_parquet(input_path)
    
    logging.info("Generating feature profile report...")
    profile = ProfileReport(
        df,
        title=report_title,
        vars={
            "num": {"chi_squared_threshold": 0.0},
            "cat": {"chi_squared_threshold": 0.0},
        },
        correlations=None,
    )
    
    logging.info(f"Saving report to {output_path}")
    profile.to_file(output_path)
    logging.info("Feature monitoring report generated successfully.")

if __name__ == "__main__":
    main()
