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
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

from src.config import PROCESSED_DATA_DIR, VISUALIZATIONS_DIR, REPORTS_DIR
from src.db_utils import query_to_df, test_connection


def load_data():
    """Load feature-engineered data."""
    print("=" * 80)
    print("LOADING DATA")
    print("=" * 80)
    
    feature_path = PROCESSED_DATA_DIR / 'customer_features.csv'
    
    if feature_path.exists():
        df = pd.read_csv(feature_path)
        print(f"✓ Loaded {len(df)} records from {feature_path}")
        return df
    else:
        raise FileNotFoundError(f"Feature file not found. Run 02_feature_engineering.py first.")


def rfm_analysis(df):
    """Perform RFM (Recency, Frequency, Monetary) analysis."""
    print("\n" + "=" * 80)
    print("RFM ANALYSIS")
    print("=" * 80)
    
    # For telecom churn:
    # R (Recency) = tenure (how long they've been a customer)
    # F (Frequency) = engagement_score (how many services they use)
    # M (Monetary) = TotalCharges or ltv
    
    rfm_df = df.copy()
    
    # Calculate RFM scores (1-5 scale)
    # Use rank-based scoring to avoid issues with duplicate values
    rfm_df['R_score'] = pd.cut(rfm_df['tenure'], bins=5, labels=[5, 4, 3, 2, 1])  # Higher tenure = lower recency score
    
    # For Frequency (engagement_score), handle duplicates by using rank percentiles
    if 'engagement_score' in rfm_df.columns:
        try:
            rfm_df['F_score'] = pd.qcut(rfm_df['engagement_score'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        except ValueError:
            # If qcut fails due to too many duplicates, use rank-based approach
            rfm_df['F_score'] = pd.cut(rfm_df['engagement_score'].rank(method='first'), 
                                        bins=5, labels=[1, 2, 3, 4, 5])
    else:
        rfm_df['F_score'] = 3  # Default mid-value if engagement_score is missing
    
    # For Monetary (ltv), handle duplicates similarly
    try:
        rfm_df['M_score'] = pd.qcut(rfm_df['ltv'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    except ValueError:
        rfm_df['M_score'] = pd.cut(rfm_df['ltv'].rank(method='first'), 
                                    bins=5, labels=[1, 2, 3, 4, 5])
    
    # Convert to numeric
    rfm_df['R_score'] = rfm_df['R_score'].astype(int)
    rfm_df['F_score'] = rfm_df['F_score'].astype(int)
    rfm_df['M_score'] = rfm_df['M_score'].astype(int)
    
    # Calculate RFM score
    rfm_df['RFM_Score'] = rfm_df['R_score'] + rfm_df['F_score'] + rfm_df['M_score']
    
    # Segment based on RFM score
    rfm_df['RFM_Segment'] = pd.cut(
        rfm_df['RFM_Score'],
        bins=[0, 6, 9, 12, 15],
        labels=['At Risk', 'Developing', 'Established', 'Champions']
    )
    
    print("\nRFM Segment Distribution:")
    print(rfm_df['RFM_Segment'].value_counts().sort_index())
    
    # Analyze churn by RFM segment
    if 'Churn' in rfm_df.columns:
        churn_by_segment = rfm_df.groupby('RFM_Segment')['Churn'].agg(['sum', 'count', 'mean'])
        churn_by_segment.columns = ['Churned', 'Total', 'Churn_Rate']
        churn_by_segment['Churn_Rate'] = churn_by_segment['Churn_Rate'] * 100
        
        print("\nChurn Rate by RFM Segment:")
        print(churn_by_segment)
    
    return rfm_df


def kmeans_clustering(df, n_clusters=4):
    """Perform K-Means clustering."""
    print("\n" + "=" * 80)
    print("K-MEANS CLUSTERING")
    print("=" * 80)
    
    # Select features for clustering
    clustering_features = ['tenure', 'MonthlyCharges', 'TotalCharges', 'ltv']
    
    if 'engagement_score' in df.columns:
        clustering_features.append('engagement_score')
    
    # Prepare data
    X = df[clustering_features].copy()
    X = X.fillna(X.mean())  # Handle any missing values
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Determine optimal number of clusters using elbow method
    print("\nDetermining optimal number of clusters...")
    inertias = []
    K_range = range(2, 10)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
    
    # Plot elbow curve
    plt.figure(figsize=(10, 6))
    plt.plot(K_range, inertias, 'bo-')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Inertia')
    plt.title('Elbow Method for Optimal k', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / '06_elbow_curve.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved elbow curve visualization")
    plt.close()
    
    # Fit final model with chosen number of clusters
    print(f"\nFitting K-Means with {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['KMeans_Cluster'] = kmeans.fit_predict(X_scaled)
    
    print(f"\nCluster Distribution:")
    print(df['KMeans_Cluster'].value_counts().sort_index())
    
    # Visualize clusters using PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df['KMeans_Cluster'], 
                         cmap='viridis', alpha=0.6, s=50)
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
    plt.title('Customer Segments (K-Means Clustering)', fontsize=14, fontweight='bold')
    plt.colorbar(scatter, label='Cluster')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / '07_kmeans_clusters.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved cluster visualization")
    plt.close()
    
    return df


def segment_profiling(df):
    """Profile each segment with key metrics."""
    print("\n" + "=" * 80)
    print("SEGMENT PROFILING")
    print("=" * 80)
    
    if 'KMeans_Cluster' not in df.columns:
        print("No clusters found. Skipping profiling.")
        return
    
    # Profile by K-Means clusters
    profile_features = ['tenure', 'MonthlyCharges', 'TotalCharges', 'ltv']
    
    if 'engagement_score' in df.columns:
        profile_features.append('engagement_score')
    
    if 'Churn' in df.columns:
        profile_features.append('Churn')
    
    cluster_profiles = df.groupby('KMeans_Cluster')[profile_features].mean()
    
    print("\nCluster Profiles (Average Values):")
    print(cluster_profiles)
    
    # Visualize cluster profiles
    cluster_profiles_normalized = (cluster_profiles - cluster_profiles.min()) / (cluster_profiles.max() - cluster_profiles.min())
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(cluster_profiles_normalized.T, annot=True, fmt='.2f', cmap='YlOrRd', 
                cbar_kws={'label': 'Normalized Value'})
    plt.title('Cluster Profiles Heatmap', fontsize=14, fontweight='bold')
    plt.xlabel('Cluster')
    plt.ylabel('Feature')
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / '08_cluster_profiles.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved cluster profile visualization")
    plt.close()
    
    return cluster_profiles


def save_segments(df):
    """Save segmented customer data."""
    print("\n" + "=" * 80)
    print("SAVING SEGMENTS")
    print("=" * 80)
    
    output_path = PROCESSED_DATA_DIR / 'customer_segments.csv'
    df.to_csv(output_path, index=False)
    print(f"✓ Saved segmented data to: {output_path}")
    
    # Create segmentation report
    report_path = REPORTS_DIR / 'segmentation_report.txt'
    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("CUSTOMER SEGMENTATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        if 'RFM_Segment' in df.columns:
            f.write("RFM SEGMENTS:\n")
            f.write("-" * 40 + "\n")
            f.write(df['RFM_Segment'].value_counts().to_string())
            f.write("\n\n")
        
        if 'KMeans_Cluster' in df.columns:
            f.write("K-MEANS CLUSTERS:\n")
            f.write("-" * 40 + "\n")
            f.write(df['KMeans_Cluster'].value_counts().to_string())
            f.write("\n\n")
        
        f.write("VISUALIZATIONS GENERATED:\n")
        f.write("-" * 40 + "\n")
        f.write("- 06_elbow_curve.png\n")
        f.write("- 07_kmeans_clusters.png\n")
        f.write("- 08_cluster_profiles.png\n\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"✓ Saved report to: {report_path}")


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("SAAS CHURN ANALYTICS - CUSTOMER SEGMENTATION")
    print("=" * 80 + "\n")
    
    # Load data
    df = load_data()
    
    # RFM Analysis
    df_rfm = rfm_analysis(df)
    
    # K-Means Clustering
    df_clustered = kmeans_clustering(df_rfm, n_clusters=4)
    
    # Segment Profiling
    segment_profiling(df_clustered)
    
    # Save segments
    save_segments(df_clustered)
    
    print("\n" + "=" * 80)
    print("CUSTOMER SEGMENTATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nOutput saved to: {PROCESSED_DATA_DIR / 'customer_segments.csv'}")
    print("\nNext step: Run 04_model_training.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
