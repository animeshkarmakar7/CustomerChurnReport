"""
Feature Engineering Script

This script creates derived features from raw customer data to improve
machine learning model performance.

Features Created:
    - Customer Lifetime Value (LTV)
    - Engagement Score (number of services used)
    - Tenure Groups
    - Charges per tenure month
    - Feature interaction terms
    - Encoded categorical variables

Output:
    - data/processed/customer_features.csv
    - data/processed/feature_names.json
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

from src.config import (PROCESSED_DATA_DIR, RAW_DATA_DIR, FEATURE_COLUMNS, 
                         VISUALIZATIONS_DIR, REPORTS_DIR)
from src.db_utils import query_to_df, test_connection

import matplotlib.pyplot as plt
import seaborn as sns


def load_data():
    """Load customer data from database or CSV."""
    print("=" * 80)
    print("LOADING DATA")
    print("=" * 80)
    
    if test_connection():
        print("Loading data from PostgreSQL database...")
        query = "SELECT * FROM customers"
        try:
            df = query_to_df(query)
            print(f"✓ Loaded {len(df)} records from database")
            return df
        except Exception as e:
            print(f"Failed to load from database: {e}")
    
    print("Loading data from CSV file...")
    csv_path = Path('D:/CustomerEarlyRisk/dataset/WA_Fn-UseC_-Telco-Customer-Churn.csv')
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(df)} records from CSV")
    return df


def clean_data(df):
    """Clean and preprocess data."""
    print("\n" + "=" * 80)
    print("DATA CLEANING")
    print("=" * 80)
    
    df_clean = df.copy()
    
    # Convert TotalCharges to numeric (handle empty strings)
    if 'TotalCharges' in df_clean.columns:
        df_clean['TotalCharges'] = pd.to_numeric(df_clean['TotalCharges'], errors='coerce')
        
        # Fill missing TotalCharges with 0 (likely new customers)
        missing_count = df_clean['TotalCharges'].isnull().sum()
        if missing_count > 0:
            print(f"  Filling {missing_count} missing TotalCharges values with 0")
            df_clean['TotalCharges'].fillna(0, inplace=True)
    
    # Convert SeniorCitizen to Yes/No for consistency
    if 'SeniorCitizen' in df_clean.columns:
        df_clean['SeniorCitizen'] = df_clean['SeniorCitizen'].map({0: 'No', 1: 'Yes'})
    
    print(f"✓ Data cleaned. Shape: {df_clean.shape}")
    return df_clean


def create_derived_features(df):
    """Create derived features from existing columns."""
    print("\n" + "=" * 80)
    print("CREATING DERIVED FEATURES")
    print("=" * 80)
    
    df_features = df.copy()
    
    # 1. Customer Lifetime Value (LTV)
    df_features['ltv'] = df_features['tenure'] * df_features['MonthlyCharges']
    print("✓ Created: ltv (Customer Lifetime Value)")
    
    # 2. Engagement Score (number of services used)
    service_cols = []
    for col in FEATURE_COLUMNS:
        if col in df_features.columns:
            service_cols.append(col)
    
    if service_cols:
        df_features['engagement_score'] = df_features[service_cols].apply(
            lambda row: sum(1 for val in row if str(val).lower() in ['yes', 'dsl', 'fiber optic']), 
            axis=1
        )
        print(f"✓ Created: engagement_score (based on {len(service_cols)} services)")
    
    # 3. Tenure Groups
    df_features['tenure_group'] = pd.cut(
        df_features['tenure'], 
        bins=[0, 12, 24, 48, 72], 
        labels=['0-12mo', '12-24mo', '24-48mo', '48+mo'],
        include_lowest=True
    )
    print("✓ Created: tenure_group (categorical tenure bins)")
    
    # 4. Charges per tenure month
    df_features['charges_per_tenure'] = df_features['TotalCharges'] / (df_features['tenure'] + 1)
    print("✓ Created: charges_per_tenure (average monthly spend)")
    
    # 5. Monthly charges category
    df_features['monthly_charges_category'] = pd.cut(
        df_features['MonthlyCharges'],
        bins=[0, 35, 70, 120],
        labels=['Low', 'Medium', 'High']
    )
    print("✓ Created: monthly_charges_category")
    
    # 6. Has multiple services flag
    if 'engagement_score' in df_features.columns:
        df_features['has_multiple_services'] = (df_features['engagement_score'] >= 3).astype(int)
        print("✓ Created: has_multiple_services (binary flag)")
    
    # 7. Is new customer (tenure < 6 months)
    df_features['is_new_customer'] = (df_features['tenure'] <= 6).astype(int)
    print("✓ Created: is_new_customer (binary flag)")
    
    # 8. High value customer (top 25% by LTV)
    ltv_threshold = df_features['ltv'].quantile(0.75)
    df_features['is_high_value'] = (df_features['ltv'] >= ltv_threshold).astype(int)
    print(f"✓ Created: is_high_value (LTV >= ${ltv_threshold:.2f})")
    
    print(f"\n✓ Total features created: 8")
    print(f"  New shape: {df_features.shape}")
    
    return df_features


def encode_categorical_features(df):
    """Encode categorical variables for machine learning."""
    print("\n" + "=" * 80)
    print("ENCODING CATEGORICAL FEATURES")
    print("=" * 80)
    
    df_encoded = df.copy()
    
    # Binary encoding for Yes/No columns
    binary_cols = []
    for col in df_encoded.columns:
        if df_encoded[col].dtype == 'object':
            unique_vals = df_encoded[col].unique()
            if set(unique_vals).issubset({'Yes', 'No', 'No internet service', 'No phone service'}):
                # Map to binary
                df_encoded[col] = df_encoded[col].map({
                    'Yes': 1, 
                    'No': 0, 
                    'No internet service': 0, 
                    'No phone service': 0
                })
                binary_cols.append(col)
    
    print(f"✓ Binary encoded {len(binary_cols)} columns")
    
    # One-hot encoding for multi-class categorical variables
    categorical_cols = ['Contract', 'PaymentMethod', 'InternetService', 'tenure_group', 'monthly_charges_category']
    categorical_cols = [col for col in categorical_cols if col in df_encoded.columns]
    
    if categorical_cols:
        df_encoded = pd.get_dummies(df_encoded, columns=categorical_cols, drop_first=True)
        print(f"✓ One-hot encoded {len(categorical_cols)} columns")
    
    # Encode target variable (Churn)
    if 'Churn' in df_encoded.columns:
        df_encoded['Churn'] = df_encoded['Churn'].map({'Yes': 1, 'No': 0})
        print("✓ Encoded target variable: Churn")
    
    print(f"\n✓ Final encoded shape: {df_encoded.shape}")
    
    return df_encoded


def feature_importance_preview(df):
    """Quick preview of feature importance using correlation with target."""
    print("\n" + "=" * 80)
    print("FEATURE IMPORTANCE PREVIEW")
    print("=" * 80)
    
    if 'Churn' not in df.columns:
        print("Churn column not found, skipping importance preview")
        return
    
    # Select only numerical columns
    numerical_df = df.select_dtypes(include=[np.number])
    
    if 'Churn' in numerical_df.columns:
        # Calculate correlation with Churn
        correlations = numerical_df.corr()['Churn'].abs().sort_values(ascending=False)
        
        # Remove Churn itself
        correlations = correlations[correlations.index != 'Churn']
        
        print("\nTop 10 Features by Correlation with Churn:")
        print(correlations.head(10))
        
        # Visualize top features
        plt.figure(figsize=(10, 6))
        correlations.head(15).plot(kind='barh', color='#3498db')
        plt.title('Top 15 Features by Correlation with Churn', fontsize=14, fontweight='bold')
        plt.xlabel('Absolute Correlation')
        plt.ylabel('Feature')
        plt.tight_layout()
        plt.savefig(VISUALIZATIONS_DIR / '05_feature_importance_preview.png', dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved visualization: 05_feature_importance_preview.png")
        plt.close()


def save_features(df, feature_names):
    """Save engineered features to CSV and feature names to JSON."""
    print("\n" + "=" * 80)
    print("SAVING FEATURES")
    print("=" * 80)
    
    # Save feature dataset
    output_path = PROCESSED_DATA_DIR / 'customer_features.csv'
    df.to_csv(output_path, index=False)
    print(f"✓ Saved features to: {output_path}")
    print(f"  Shape: {df.shape}")
    
    # Save feature names
    feature_names_path = PROCESSED_DATA_DIR / 'feature_names.json'
    with open(feature_names_path, 'w') as f:
        json.dump(feature_names, f, indent=2)
    print(f"✓ Saved feature names to: {feature_names_path}")
    
    # Create feature summary report
    report_path = REPORTS_DIR / 'feature_engineering_report.txt'
    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("FEATURE ENGINEERING REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total Features: {len(feature_names)}\n")
        f.write(f"Total Samples: {len(df)}\n\n")
        
        f.write("DERIVED FEATURES CREATED:\n")
        f.write("-" * 40 + "\n")
        f.write("1. ltv - Customer Lifetime Value\n")
        f.write("2. engagement_score - Number of services used\n")
        f.write("3. tenure_group - Categorical tenure bins\n")
        f.write("4. charges_per_tenure - Average monthly spend\n")
        f.write("5. monthly_charges_category - Spending tier\n")
        f.write("6. has_multiple_services - Binary flag\n")
        f.write("7. is_new_customer - Tenure < 6 months\n")
        f.write("8. is_high_value - Top 25% by LTV\n\n")
        
        f.write("ENCODING APPLIED:\n")
        f.write("-" * 40 + "\n")
        f.write("- Binary encoding for Yes/No columns\n")
        f.write("- One-hot encoding for multi-class categories\n")
        f.write("- Target variable (Churn) encoded as 0/1\n\n")
        
        f.write("OUTPUT FILES:\n")
        f.write("-" * 40 + "\n")
        f.write(f"- {output_path}\n")
        f.write(f"- {feature_names_path}\n\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"✓ Saved report to: {report_path}")


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("SAAS CHURN ANALYTICS - FEATURE ENGINEERING")
    print("=" * 80 + "\n")
    
    # Load data
    df = load_data()
    
    # Clean data
    df_clean = clean_data(df)
    
    # Create derived features
    df_features = create_derived_features(df_clean)
    
    # Encode categorical features
    df_encoded = encode_categorical_features(df_features)
    
    # Feature importance preview
    feature_importance_preview(df_encoded)
    
    # Get feature names (exclude customerID if present)
    feature_names = [col for col in df_encoded.columns if col != 'customerID']
    
    # Save features
    save_features(df_encoded, feature_names)
    
    print("\n" + "=" * 80)
    print("FEATURE ENGINEERING COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nOutput saved to: {PROCESSED_DATA_DIR / 'customer_features.csv'}")
    print(f"Total features: {len(feature_names)}")
    print("\nNext step: Run 04_model_training.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
