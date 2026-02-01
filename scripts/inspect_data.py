import json
import pandas as pd

print("=" * 80)
print("INSPECTING AAER CSV")
print("=" * 80)
aaer_df = pd.read_csv('data/raw/aaer_mark5.csv', nrows=5)
print(f"Columns: {aaer_df.columns.tolist()}")
print(f"\nFirst row:\n{aaer_df.iloc[0]}")

print("\n" + "=" * 80)
print("INSPECTING LABELS JSON")
print("=" * 80)
with open('data/raw/firm_years_labels.json', 'r') as f:
    labels_data = json.load(f)
print(f"Type: {type(labels_data)}")
if isinstance(labels_data, list):
    print(f"Length: {len(labels_data)}")
    print(f"First entry: {labels_data[0]}")
elif isinstance(labels_data, dict):
    first_key = list(labels_data.keys())[0]
    print(f"First key: {first_key}")
    print(f"First value: {labels_data[first_key]}")

print("\n" + "=" * 80)
print("INSPECTING FIRM YEARS JSON (first 2 entries only)")
print("=" * 80)
with open('data/raw/firm_years.json', 'r') as f:
    firm_years_data = json.load(f)
print(f"Type: {type(firm_years_data)}")
if isinstance(firm_years_data, list):
    print(f"Length: {len(firm_years_data)}")
    print(f"First entry keys: {list(firm_years_data[0].keys()) if len(firm_years_data) > 0 else 'N/A'}")
    print(f"First entry: {firm_years_data[0]}")
elif isinstance(firm_years_data, dict):
    first_key = list(firm_years_data.keys())[0]
    print(f"First key: {first_key}")
    print(f"First value keys: {list(firm_years_data[first_key].keys())}")
    print(f"First value: {firm_years_data[first_key]}")
