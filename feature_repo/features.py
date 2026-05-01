from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int32, Int64

# Read data from the parquet file
fraud_features_source = FileSource(
    name="fraud_features",
    path="../data/processed/text_features.parquet",
    timestamp_field="filing_date_dt",
)

# Define the entity
company = Entity(
    name="company",
    join_keys=["cik"],
    description="Company identifier",
)

# Define the FeatureView
fraud_feature_view = FeatureView(
    name="fraud_text_features",
    entities=[company],
    ttl=timedelta(days=365 * 10), # 10 years ttl since it's yearly filings
    source=fraud_features_source,
    schema=[
        Field(name="mda_length", dtype=Int64),
        Field(name="mda_word_count", dtype=Int64),
        Field(name="mda_sentence_count", dtype=Int64),
        Field(name="mda_avg_word_length", dtype=Float32),
        Field(name="mda_avg_sentence_length", dtype=Float32),
        Field(name="mda_lexical_diversity", dtype=Float32),
        Field(name="mda_flesch_reading_ease", dtype=Float32),
        Field(name="mda_fin_term_count", dtype=Int64),
        Field(name="mda_fin_term_density", dtype=Float32),
        Field(name="filing_year", dtype=Int32),
        Field(name="filing_month", dtype=Int32),
        Field(name="filing_type_cat", dtype=Int32),
        Field(name="is_fraud", dtype=Int64),
    ],
)
