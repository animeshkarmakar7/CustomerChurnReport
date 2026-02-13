
import pandas as pd
from pathlib import Path

print("=" * 80)
print("DIAGNOSING CHURN ENCODING ISSUE")
print("=" * 80)

# Load raw CSV
raw_csv = Path('dataset/WA_Fn-UseC_-Telco-Customer-Churn.csv')
print(f"\n1. Loading raw CSV from: {raw_csv}")
df_raw = pd.read_csv(raw_csv)
print(f"   Shape: {df_raw.shape}")
print(f"   Churn column type: {df_raw['Churn'].dtype}")
print(f"   Churn values: {df_raw['Churn'].value_counts().to_dict()}")

# Load processed CSV
processed_csv = Path('data/processed/customer_features.csv')
if processed_csv.exists():
    print(f"\n2. Loading processed CSV from: {processed_csv}")
    df_processed = pd.read_csv(processed_csv)
    print(f"   Shape: {df_processed.shape}")
    
    if 'Churn' in df_processed.columns:
        print(f"   Churn column type: {df_processed['Churn'].dtype}")
        print(f"   Churn NaN count: {df_processed['Churn'].isna().sum()}")
        print(f"   Churn unique values: {df_processed['Churn'].unique()}")
    else:
        print("   ERROR: No Churn column found!")
else:
    print(f"\n2. Processed CSV not found at: {processed_csv}")

print("\n" + "=" * 80)
print("SOLUTION: Re-running feature engineering with explicit Churn handling")
print("=" * 80)

# Run feature engineering
import subprocess
result = subprocess.run(['python', 'src/02_feature_engineering.py'], 
                       capture_output=True, text=True)

if result.returncode == 0:
    print("\n✓ Feature engineering completed successfully!")
    
    # Verify the fix
    df_check = pd.read_csv('data/processed/customer_features.csv')
    if 'Churn' in df_check.columns:
        nan_count = df_check['Churn'].isna().sum()
        if nan_count == 0:
            print(f"✓ Churn column properly encoded!")
            print(f"  Values: {df_check['Churn'].value_counts().to_dict()}")
        else:
            print(f"✗ Still has {nan_count} NaN values in Churn column")
    else:
        print("✗ Churn column missing!")
else:
    print(f"\n✗ Feature engineering failed!")
    print(f"Error: {result.stderr}")

print("\n" + "=" * 80)
