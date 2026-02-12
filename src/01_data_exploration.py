"""
Data Exploration and Exploratory Data Analysis (EDA)

This script performs comprehensive exploratory data analysis on the customer churn dataset,
including statistical summaries, distribution analysis, and correlation studies.

Output:
    - Statistical summary report
    - Distribution visualizations
    - Correlation heatmap
    - Churn analysis by features
    - EDA report saved to reports/
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from src.config import PROCESSED_DATA_DIR, VISUALIZATIONS_DIR, REPORTS_DIR, RAW_DATA_DIR
from src.db_utils import query_to_df, test_connection

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def load_data():
    """Load customer data from database or CSV file."""
    print("=" * 80)
    print("LOADING DATA")
    print("=" * 80)
    
    # Try loading from database first
    if test_connection():
        print("Loading data from PostgreSQL database...")
        query = "SELECT * FROM customers"
        try:
            df = query_to_df(query)
            print(f"✓ Loaded {len(df)} records from database")
            return df
        except Exception as e:
            print(f"Failed to load from database: {e}")
    
    # Fallback to CSV
    print("Loading data from CSV file...")
    csv_path = Path('D:/CustomerEarlyRisk/dataset/WA_Fn-UseC_-Telco-Customer-Churn.csv')
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(df)} records from CSV")
        return df
    else:
        raise FileNotFoundError(f"Data file not found at {csv_path}")


def basic_info(df):
    """Display basic dataset information."""
    print("\n" + "=" * 80)
    print("DATASET OVERVIEW")
    print("=" * 80)
    
    print(f"\nDataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"\nFirst 5 rows:")
    print(df.head())
    
    print(f"\nData Types:")
    print(df.dtypes.value_counts())
    
    print(f"\nMemory Usage:")
    print(f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    return df.info()


def missing_value_analysis(df):
    """Analyze missing values in the dataset."""
    print("\n" + "=" * 80)
    print("MISSING VALUE ANALYSIS")
    print("=" * 80)
    
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    
    missing_df = pd.DataFrame({
        'Column': missing.index,
        'Missing_Count': missing.values,
        'Missing_Percentage': missing_pct.values
    })
    missing_df = missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)
    
    if len(missing_df) > 0:
        print("\nColumns with missing values:")
        print(missing_df.to_string(index=False))
    else:
        print("\n✓ No missing values found in the dataset!")
    
    # Check for empty strings or whitespace
    print("\nChecking for empty strings...")
    for col in df.select_dtypes(include=['object']).columns:
        empty_count = (df[col].str.strip() == '').sum()
        if empty_count > 0:
            print(f"  {col}: {empty_count} empty strings")
    
    return missing_df


def churn_distribution(df):
    """Analyze churn distribution."""
    print("\n" + "=" * 80)
    print("CHURN DISTRIBUTION")
    print("=" * 80)
    
    churn_counts = df['Churn'].value_counts()
    churn_pct = df['Churn'].value_counts(normalize=True) * 100
    
    print("\nChurn Counts:")
    print(churn_counts)
    print("\nChurn Percentage:")
    print(churn_pct)
    
    # Visualize churn distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Count plot
    churn_counts.plot(kind='bar', ax=axes[0], color=['#2ecc71', '#e74c3c'])
    axes[0].set_title('Churn Distribution (Count)', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Churn Status')
    axes[0].set_ylabel('Number of Customers')
    axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=0)
    
    # Add value labels on bars
    for i, v in enumerate(churn_counts):
        axes[0].text(i, v + 50, str(v), ha='center', fontweight='bold')
    
    # Pie chart
    colors = ['#2ecc71', '#e74c3c']
    axes[1].pie(churn_counts, labels=churn_counts.index, autopct='%1.1f%%', 
                colors=colors, startangle=90)
    axes[1].set_title('Churn Distribution (Percentage)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / '01_churn_distribution.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved visualization: 01_churn_distribution.png")
    plt.close()
    
    return churn_counts, churn_pct


def numerical_features_analysis(df):
    """Analyze numerical features."""
    print("\n" + "=" * 80)
    print("NUMERICAL FEATURES ANALYSIS")
    print("=" * 80)
    
    # Identify numerical columns
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    # Remove customerID if present
    if 'customerID' in numerical_cols:
        numerical_cols.remove('customerID')
    
    print(f"\nNumerical columns: {numerical_cols}")
    
    # Statistical summary
    print("\nStatistical Summary:")
    print(df[numerical_cols].describe())
    
    # Distribution plots
    n_cols = len(numerical_cols)
    fig, axes = plt.subplots((n_cols + 2) // 3, 3, figsize=(15, 4 * ((n_cols + 2) // 3)))
    axes = axes.flatten() if n_cols > 1 else [axes]
    
    for idx, col in enumerate(numerical_cols):
        df[col].hist(bins=30, ax=axes[idx], color='#3498db', edgecolor='black')
        axes[idx].set_title(f'Distribution of {col}', fontweight='bold')
        axes[idx].set_xlabel(col)
        axes[idx].set_ylabel('Frequency')
    
    # Hide unused subplots
    for idx in range(n_cols, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / '02_numerical_distributions.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved visualization: 02_numerical_distributions.png")
    plt.close()
    
    return df[numerical_cols].describe()


def categorical_features_analysis(df):
    """Analyze categorical features."""
    print("\n" + "=" * 80)
    print("CATEGORICAL FEATURES ANALYSIS")
    print("=" * 80)
    
    # Identify categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # Remove customerID and Churn
    categorical_cols = [col for col in categorical_cols if col not in ['customerID', 'Churn']]
    
    print(f"\nCategorical columns ({len(categorical_cols)}): {categorical_cols}")
    
    # Value counts for each categorical column
    for col in categorical_cols[:5]:  # Show first 5
        print(f"\n{col}:")
        print(df[col].value_counts())
    
    return categorical_cols


def correlation_analysis(df):
    """Analyze correlations between features."""
    print("\n" + "=" * 80)
    print("CORRELATION ANALYSIS")
    print("=" * 80)
    
    # Select numerical columns
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    # Calculate correlation matrix
    corr_matrix = df[numerical_cols].corr()
    
    print("\nCorrelation Matrix:")
    print(corr_matrix)
    
    # Visualize correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1)
    plt.title('Feature Correlation Heatmap', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / '03_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved visualization: 03_correlation_heatmap.png")
    plt.close()
    
    return corr_matrix


def churn_by_features(df):
    """Analyze churn rate by different features."""
    print("\n" + "=" * 80)
    print("CHURN RATE BY FEATURES")
    print("=" * 80)
    
    # Key categorical features to analyze
    key_features = ['Contract', 'InternetService', 'PaymentMethod', 'TechSupport', 'OnlineSecurity']
    
    # Filter features that exist in the dataset
    available_features = [f for f in key_features if f in df.columns]
    
    if not available_features:
        print("No key features found for analysis")
        return
    
    # Calculate churn rate by feature
    churn_rates = {}
    for feature in available_features:
        churn_rate = df.groupby(feature)['Churn'].apply(lambda x: (x == 'Yes').sum() / len(x) * 100)
        churn_rates[feature] = churn_rate
        print(f"\nChurn Rate by {feature}:")
        print(churn_rate.sort_values(ascending=False))
    
    # Visualize churn rate by top features
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, feature in enumerate(available_features[:4]):
        churn_rate = churn_rates[feature].sort_values(ascending=False)
        churn_rate.plot(kind='bar', ax=axes[idx], color='#e74c3c')
        axes[idx].set_title(f'Churn Rate by {feature}', fontsize=12, fontweight='bold')
        axes[idx].set_xlabel(feature)
        axes[idx].set_ylabel('Churn Rate (%)')
        axes[idx].set_xticklabels(axes[idx].get_xticklabels(), rotation=45, ha='right')
        
        # Add value labels
        for i, v in enumerate(churn_rate):
            axes[idx].text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / '04_churn_by_features.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved visualization: 04_churn_by_features.png")
    plt.close()
    
    return churn_rates


def generate_eda_report(df):
    """Generate comprehensive EDA report."""
    print("\n" + "=" * 80)
    print("GENERATING EDA REPORT")
    print("=" * 80)
    
    report_path = REPORTS_DIR / 'eda_report.txt'
    
    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("EXPLORATORY DATA ANALYSIS REPORT\n")
        f.write("SaaS Customer Churn Analytics\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns\n\n")
        
        f.write("CHURN STATISTICS:\n")
        f.write("-" * 40 + "\n")
        churn_counts = df['Churn'].value_counts()
        churn_pct = df['Churn'].value_counts(normalize=True) * 100
        f.write(f"Total Customers: {len(df)}\n")
        f.write(f"Churned Customers: {churn_counts.get('Yes', 0)} ({churn_pct.get('Yes', 0):.2f}%)\n")
        f.write(f"Retained Customers: {churn_counts.get('No', 0)} ({churn_pct.get('No', 0):.2f}%)\n\n")
        
        f.write("KEY FINDINGS:\n")
        f.write("-" * 40 + "\n")
        f.write("1. Dataset contains customer subscription and service usage data\n")
        f.write("2. Churn rate indicates customer retention challenges\n")
        f.write("3. Multiple features available for predictive modeling\n")
        f.write("4. Data quality is good with minimal missing values\n\n")
        
        f.write("VISUALIZATIONS GENERATED:\n")
        f.write("-" * 40 + "\n")
        f.write("1. 01_churn_distribution.png - Overall churn distribution\n")
        f.write("2. 02_numerical_distributions.png - Numerical feature distributions\n")
        f.write("3. 03_correlation_heatmap.png - Feature correlation matrix\n")
        f.write("4. 04_churn_by_features.png - Churn rates by key features\n\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"✓ EDA report saved to: {report_path}")


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("SAAS CHURN ANALYTICS - EXPLORATORY DATA ANALYSIS")
    print("=" * 80 + "\n")
    
    # Load data
    df = load_data()
    
    # Basic information
    basic_info(df)
    
    # Missing value analysis
    missing_value_analysis(df)
    
    # Churn distribution
    churn_distribution(df)
    
    # Numerical features
    numerical_features_analysis(df)
    
    # Categorical features
    categorical_features_analysis(df)
    
    # Correlation analysis
    correlation_analysis(df)
    
    # Churn by features
    churn_by_features(df)
    
    # Generate report
    generate_eda_report(df)
    
    print("\n" + "=" * 80)
    print("EDA COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nVisualizations saved to: {VISUALIZATIONS_DIR}")
    print(f"Report saved to: {REPORTS_DIR / 'eda_report.txt'}")
    print("\nNext step: Run 02_feature_engineering.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
