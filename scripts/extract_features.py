import pandas as pd
import yaml
import logging
import textstat
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_params():
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)

def clean_text(text, lowercase=True):
    if not isinstance(text, str):
        return ""
    # Very basic cleaning
    if lowercase:
        text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def count_financial_terms(text, terms):
    if not text:
        return 0
    words = set(text.split())
    return sum(1 for term in terms if term in words)

def extract_features(df, params):
    logging.info("Extracting features...")
    text_config = params.get("text_preprocessing", {})
    financial_terms = text_config.get("financial_terms", [])
    
    # Text features
    mda_col = df["mda"].fillna("")
    
    logging.info("Calculating basic text metrics...")
    df["mda_length"] = mda_col.str.len()
    
    # Word count (rough)
    words_series = mda_col.str.split()
    df["mda_word_count"] = words_series.apply(len)
    
    # Sentence count
    logging.info("Calculating textstat metrics...")
    # textstat can be slow, so we will use a simplified approach or sample if it takes too long.
    # For a large dataset, this might be slow, so we implement simple fallbacks if needed.
    df["mda_sentence_count"] = mda_col.apply(lambda x: textstat.sentence_count(x) if len(x) > 0 else 0)
    
    # Averages
    df["mda_avg_word_length"] = df.apply(lambda row: row["mda_length"] / row["mda_word_count"] if row["mda_word_count"] > 0 else 0, axis=1)
    df["mda_avg_sentence_length"] = df.apply(lambda row: row["mda_word_count"] / row["mda_sentence_count"] if row["mda_sentence_count"] > 0 else 0, axis=1)
    
    # Lexical Diversity (Unique words / total words)
    logging.info("Calculating lexical diversity...")
    df["mda_lexical_diversity"] = words_series.apply(lambda w: len(set(w)) / len(w) if len(w) > 0 else 0)
    
    # Readability (can be slow, wrap in try/except or skip if empty)
    logging.info("Calculating readability scores...")
    df["mda_flesch_reading_ease"] = mda_col.apply(lambda x: textstat.flesch_reading_ease(x[:5000]) if len(x) > 0 else 0) # Use first 5000 chars for speed
    
    # Financial terms
    logging.info("Calculating financial term density...")
    df["mda_clean"] = mda_col.apply(lambda x: clean_text(x, text_config.get("lowercase", True)))
    df["mda_fin_term_count"] = df["mda_clean"].apply(lambda x: count_financial_terms(x, financial_terms))
    df["mda_fin_term_density"] = df.apply(lambda row: row["mda_fin_term_count"] / row["mda_word_count"] if row["mda_word_count"] > 0 else 0, axis=1)
    
    # Drop intermediate column
    df = df.drop(columns=["mda_clean"])

    # Temporal features
    logging.info("Extracting temporal features...")
    df["filing_date_dt"] = pd.to_datetime(df["filing_date"], errors="coerce")
    df["filing_year"] = df["filing_date_dt"].dt.year
    df["filing_month"] = df["filing_date_dt"].dt.month
    
    # Categorical Features mapping
    df["filing_type_cat"] = df["filing_type"].astype("category").cat.codes
    
    logging.info("Feature extraction complete.")
    return df

def main():
    params = load_params()
    
    input_path = params["data"]["interim"]["firm_years_with_labels"]
    output_path = params["data"]["processed"]["text_features"]
    
    # Ensure directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"Loading data from {input_path}")
    df = pd.read_parquet(input_path)
    
    # For testing/speed in ML Ops tutorial, you might want to sample, but let's process all.
    df_features = extract_features(df, params)
    
    logging.info(f"Saving features to {output_path}")
    df_features.to_parquet(output_path, index=False)
    
if __name__ == "__main__":
    main()
