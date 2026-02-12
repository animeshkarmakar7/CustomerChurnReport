"""
Quick fix script to properly encode Churn column
"""
import pandas as pd
from pathlib import Path

print("=" * 80)
print("FIXING CHURN COLUMN ENCODING")
print("=" * 80)

# Load raw CSV
raw_path = Path('dataset/WA_Fn-UseC_-Telco-Customer-Churn.csv')
print(f"\nLoading raw data from: {raw_path}")
df = pd.read_csv(raw_path)

print(f"Original shape: {df.shape}")
print(f"Churn column before encoding: {df['Churn'].value_counts().to_dict()}")

# Clean TotalCharges
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'].fillna(0, inplace=True)

# Convert SeniorCitizen to Yes/No
df['SeniorCitizen'] = df['SeniorCitizen'].map({0: 'No', 1: 'Yes'})

# Create derived features
df['ltv'] = df['tenure'] * df['MonthlyCharges']
df['engagement_score'] = 0
for col in ['PhoneService', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 
            'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']:
    if col in df.columns:
        df['engagement_score'] += (df[col].isin(['Yes', 'DSL', 'Fiber optic'])).astype(int)

df['tenure_group'] = pd.cut(df['tenure'], bins=[0, 12, 24, 48, 72], 
                             labels=['0-12mo', '12-24mo', '24-48mo', '48+mo'], include_lowest=True)
df['charges_per_tenure'] = df['TotalCharges'] / (df['tenure'] + 1)
df['monthly_charges_category'] = pd.cut(df['MonthlyCharges'], bins=[0, 35, 70, 120], 
                                         labels=['Low', 'Medium', 'High'])
df['has_multiple_services'] = (df['engagement_score'] >= 3).astype(int)
df['is_new_customer'] = (df['tenure'] <= 6).astype(int)
ltv_threshold = df['ltv'].quantile(0.75)
df['is_high_value'] = (df['ltv'] >= ltv_threshold).astype(int)

print(f"\n✓ Created 8 derived features")

# Binary encoding for Yes/No columns
for col in df.columns:
    if df[col].dtype == 'object' and col != 'Churn':
        unique_vals = df[col].unique()
        if set(unique_vals).issubset({'Yes', 'No', 'No internet service', 'No phone service'}):
            df[col] = df[col].map({'Yes': 1, 'No': 0, 'No internet service': 0, 'No phone service': 0})

print(f"✓ Binary encoded Yes/No columns")

# One-hot encoding for categorical
categorical_cols = ['Contract', 'PaymentMethod', 'InternetService', 'tenure_group', 'monthly_charges_category']
categorical_cols = [col for col in categorical_cols if col in df.columns]
df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

print(f"✓ One-hot encoded {len(categorical_cols)} columns")

# CRITICAL: Encode Churn LAST
print(f"\nChurn column before final encoding: {df['Churn'].value_counts().to_dict()}")
df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})
print(f"Churn column after encoding: {df['Churn'].value_counts().to_dict()}")
print(f"Churn NaN count: {df['Churn'].isna().sum()}")

# Save
output_path = Path('data/processed/customer_features.csv')
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

print(f"\n✓ Saved to: {output_path}")
print(f"  Final shape: {df.shape}")
print(f"  Churn encoded: {df['Churn'].value_counts().to_dict()}")

print("\n" + "=" * 80)
print("CHURN ENCODING FIXED SUCCESSFULLY!")
print("=" * 80)
print("\nYou can now run:")
print("  python src/04_model_training.py")
print("=" * 80)
