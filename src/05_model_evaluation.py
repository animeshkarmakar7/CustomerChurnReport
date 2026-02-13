
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

from sklearn.metrics import (classification_report, confusion_matrix, roc_auc_score,
                             roc_curve, precision_recall_curve, auc)

import matplotlib.pyplot as plt
import seaborn as sns
import shap

from src.config import (PROCESSED_DATA_DIR, MODELS_DIR, VISUALIZATIONS_DIR, 
                         REPORTS_DIR, RISK_BINS, RISK_LABELS)


def load_model_and_data():
    """Load trained model and test data."""
    print("=" * 80)
    print("LOADING MODEL AND DATA")
    print("=" * 80)
    
    # Load model
    model_path = MODELS_DIR / 'churn_predictor_xgboost.pkl'
    scaler_path = MODELS_DIR / 'feature_scaler.pkl'
    metadata_path = MODELS_DIR / 'model_metadata.json'
    
    if not model_path.exists():
        raise FileNotFoundError("Model not found. Run 04_model_training.py first.")
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    print(f"✓ Loaded model: {metadata['model_type']}")
    print(f"✓ Model AUC: {metadata['performance_metrics']['auc']:.4f}")
    
    # Load feature data
    feature_path = PROCESSED_DATA_DIR / 'customer_features.csv'
    df = pd.read_csv(feature_path)
    
    print(f"✓ Loaded {len(df)} customer records")
    
    return model, scaler, metadata, df


def generate_predictions(model, scaler, df, feature_names):
    """Generate predictions for all customers."""
    print("\n" + "=" * 80)
    print("GENERATING PREDICTIONS")
    print("=" * 80)
    
    # Prepare features
    X = df[feature_names].fillna(df[feature_names].mean())
    X_scaled = scaler.transform(X)
    
    # Generate predictions
    predictions = model.predict(X_scaled)
    prediction_probabilities = model.predict_proba(X_scaled)[:, 1]
    
    # Add predictions to dataframe
    df['churn_prediction'] = predictions
    df['churn_probability'] = prediction_probabilities
    
    # Create risk segments
    df['risk_segment'] = pd.cut(
        df['churn_probability'],
        bins=RISK_BINS,
        labels=RISK_LABELS
    )
    
    print(f"✓ Generated predictions for {len(df)} customers")
    print(f"\nRisk Segment Distribution:")
    print(df['risk_segment'].value_counts().sort_index())
    
    return df


def confusion_matrix_analysis(y_true, y_pred):
    """Create and visualize confusion matrix."""
    print("\n" + "=" * 80)
    print("CONFUSION MATRIX ANALYSIS")
    print("=" * 80)
    
    cm = confusion_matrix(y_true, y_pred)
    
    print("\nConfusion Matrix:")
    print(cm)
    
    # Calculate metrics from confusion matrix
    tn, fp, fn, tp = cm.ravel()
    
    print(f"\nTrue Negatives: {tn}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"True Positives: {tp}")
    
    # Visualize confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / '10_confusion_matrix.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved confusion matrix visualization")
    plt.close()
    
    return cm


def roc_pr_curves(y_true, y_pred_proba):
    """Generate ROC and Precision-Recall curves."""
    print("\n" + "=" * 80)
    print("ROC AND PRECISION-RECALL CURVES")
    print("=" * 80)
    
    # ROC Curve
    fpr, tpr, thresholds_roc = roc_curve(y_true, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    # Precision-Recall Curve
    precision, recall, thresholds_pr = precision_recall_curve(y_true, y_pred_proba)
    pr_auc = auc(recall, precision)
    
    print(f"ROC-AUC: {roc_auc:.4f}")
    print(f"PR-AUC: {pr_auc:.4f}")
    
    # Plot both curves
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # ROC Curve
    axes[0].plot(fpr, tpr, color='#e74c3c', lw=2, label=f'ROC Curve (AUC = {roc_auc:.3f})')
    axes[0].plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', label='Random Classifier')
    axes[0].set_xlabel('False Positive Rate')
    axes[0].set_ylabel('True Positive Rate')
    axes[0].set_title('ROC Curve', fontsize=12, fontweight='bold')
    axes[0].legend(loc='lower right')
    axes[0].grid(True, alpha=0.3)
    
    # Precision-Recall Curve
    axes[1].plot(recall, precision, color='#3498db', lw=2, label=f'PR Curve (AUC = {pr_auc:.3f})')
    axes[1].set_xlabel('Recall')
    axes[1].set_ylabel('Precision')
    axes[1].set_title('Precision-Recall Curve', fontsize=12, fontweight='bold')
    axes[1].legend(loc='lower left')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / '11_roc_pr_curves.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved ROC and PR curves")
    plt.close()
    
    return roc_auc, pr_auc


def feature_importance_analysis(model, feature_names, X_sample):
    """Analyze feature importance using SHAP values."""
    print("\n" + "=" * 80)
    print("FEATURE IMPORTANCE ANALYSIS (SHAP)")
    print("=" * 80)
    
    try:
        # Create SHAP explainer
        explainer = shap.TreeExplainer(model)
        
        # Calculate SHAP values (use sample for speed)
        sample_size = min(500, len(X_sample))
        X_sample_subset = X_sample[:sample_size]
        shap_values = explainer.shap_values(X_sample_subset)
        
        # Summary plot
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X_sample_subset, feature_names=feature_names, 
                         plot_type="bar", show=False)
        plt.title('Feature Importance (SHAP Values)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(VISUALIZATIONS_DIR / '12_feature_importance_shap.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved SHAP feature importance visualization")
        plt.close()
        
        # Get feature importance values
        feature_importance = np.abs(shap_values).mean(axis=0)
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': feature_importance
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(importance_df.head(10).to_string(index=False))
        
        return importance_df
        
    except Exception as e:
        print(f"SHAP analysis failed: {e}")
        print("Falling back to model's feature_importances_")
        
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\nTop 10 Most Important Features:")
            print(importance_df.head(10).to_string(index=False))
            
            # Plot
            plt.figure(figsize=(10, 8))
            importance_df.head(15).plot(x='feature', y='importance', kind='barh', color='#3498db')
            plt.title('Feature Importance', fontsize=14, fontweight='bold')
            plt.xlabel('Importance')
            plt.ylabel('Feature')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig(VISUALIZATIONS_DIR / '12_feature_importance.png', dpi=300, bbox_inches='tight')
            print(f"✓ Saved feature importance visualization")
            plt.close()
            
            return importance_df


def business_impact_analysis(df):
    """Calculate business impact of churn predictions."""
    print("\n" + "=" * 80)
    print("BUSINESS IMPACT ANALYSIS")
    print("=" * 80)
    
    # High-risk customers
    high_risk = df[df['risk_segment'].isin(['High', 'Critical'])]
    
    print(f"\nHigh-Risk Customers: {len(high_risk)}")
    print(f"Percentage of total: {len(high_risk) / len(df) * 100:.2f}%")
    
    # Calculate potential revenue at risk
    if 'MonthlyCharges' in df.columns:
        monthly_revenue_at_risk = high_risk['MonthlyCharges'].sum()
        annual_revenue_at_risk = monthly_revenue_at_risk * 12
        
        print(f"\nMonthly Revenue at Risk: ${monthly_revenue_at_risk:,.2f}")
        print(f"Annual Revenue at Risk (ARR): ${annual_revenue_at_risk:,.2f}")
        
        # Assuming 30% retention through intervention
        retention_rate = 0.30
        potential_arr_saved = annual_revenue_at_risk * retention_rate
        
        print(f"\nAssuming {retention_rate*100:.0f}% retention through intervention:")
        print(f"Potential ARR Saved: ${potential_arr_saved:,.2f}")
        
        # ROI calculation (assuming intervention cost of $50 per customer)
        intervention_cost = len(high_risk) * 50
        roi = (potential_arr_saved - intervention_cost) / intervention_cost * 100
        
        print(f"\nIntervention Cost (${50}/customer): ${intervention_cost:,.2f}")
        print(f"ROI: {roi:,.0f}%")
        
        return {
            'high_risk_count': len(high_risk),
            'monthly_revenue_at_risk': monthly_revenue_at_risk,
            'annual_revenue_at_risk': annual_revenue_at_risk,
            'potential_arr_saved': potential_arr_saved,
            'intervention_cost': intervention_cost,
            'roi': roi
        }
    
    return {}


def save_predictions(df):
    """Save predictions for Power BI dashboard."""
    print("\n" + "=" * 80)
    print("SAVING PREDICTIONS")
    print("=" * 80)
    
    # Select relevant columns for export
    export_cols = ['customerID', 'churn_probability', 'churn_prediction', 'risk_segment']
    
    # Add business metrics if available
    if 'MonthlyCharges' in df.columns:
        export_cols.append('MonthlyCharges')
    if 'tenure' in df.columns:
        export_cols.append('tenure')
    if 'Contract' in df.columns or any('Contract_' in col for col in df.columns):
        contract_cols = [col for col in df.columns if 'Contract' in col]
        export_cols.extend(contract_cols[:1])  # Add first contract column
    
    # Filter columns that exist
    export_cols = [col for col in export_cols if col in df.columns]
    
    output_path = PROCESSED_DATA_DIR / 'model_predictions.csv'
    df[export_cols].to_csv(output_path, index=False)
    
    print(f"✓ Saved predictions to: {output_path}")
    print(f"  Columns: {export_cols}")
    print(f"  Rows: {len(df)}")


def generate_evaluation_report(metrics, business_impact):
    """Generate comprehensive evaluation report."""
    print("\n" + "=" * 80)
    print("GENERATING EVALUATION REPORT")
    print("=" * 80)
    
    report_path = REPORTS_DIR / 'model_evaluation_report.txt'
    
    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("MODEL EVALUATION REPORT\n")
        f.write("SaaS Customer Churn Prediction\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("MODEL PERFORMANCE:\n")
        f.write("-" * 40 + "\n")
        f.write(f"ROC-AUC Score: {metrics.get('roc_auc', 'N/A'):.4f}\n")
        f.write(f"PR-AUC Score: {metrics.get('pr_auc', 'N/A'):.4f}\n\n")
        
        if business_impact:
            f.write("BUSINESS IMPACT:\n")
            f.write("-" * 40 + "\n")
            f.write(f"High-Risk Customers: {business_impact.get('high_risk_count', 0):,}\n")
            f.write(f"Annual Revenue at Risk: ${business_impact.get('annual_revenue_at_risk', 0):,.2f}\n")
            f.write(f"Potential ARR Saved: ${business_impact.get('potential_arr_saved', 0):,.2f}\n")
            f.write(f"ROI: {business_impact.get('roi', 0):,.0f}%\n\n")
        
        f.write("VISUALIZATIONS GENERATED:\n")
        f.write("-" * 40 + "\n")
        f.write("- 10_confusion_matrix.png\n")
        f.write("- 11_roc_pr_curves.png\n")
        f.write("- 12_feature_importance_shap.png\n\n")
        
        f.write("OUTPUT FILES:\n")
        f.write("-" * 40 + "\n")
        f.write(f"- {PROCESSED_DATA_DIR / 'model_predictions.csv'}\n\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"✓ Evaluation report saved to: {report_path}")


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("SAAS CHURN ANALYTICS - MODEL EVALUATION")
    print("=" * 80 + "\n")
    
    # Load model and data
    model, scaler, metadata, df = load_model_and_data()
    
    # Generate predictions
    df_with_predictions = generate_predictions(model, scaler, df, metadata['feature_names'])
    
    # Prepare data for evaluation
    y_true = df['Churn']
    y_pred = df_with_predictions['churn_prediction']
    y_pred_proba = df_with_predictions['churn_probability']
    
    # Confusion matrix
    cm = confusion_matrix_analysis(y_true, y_pred)
    
    # ROC and PR curves
    roc_auc, pr_auc = roc_pr_curves(y_true, y_pred_proba)
    
    # Feature importance
    X = df[metadata['feature_names']].fillna(df[metadata['feature_names']].mean())
    X_scaled = scaler.transform(X)
    feature_importance_analysis(model, metadata['feature_names'], X_scaled)
    
    # Business impact
    business_impact = business_impact_analysis(df_with_predictions)
    
    # Save predictions
    save_predictions(df_with_predictions)
    
    # Generate report
    metrics = {'roc_auc': roc_auc, 'pr_auc': pr_auc}
    generate_evaluation_report(metrics, business_impact)
    
    print("\n" + "=" * 80)
    print("MODEL EVALUATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nROC-AUC: {roc_auc:.4f}")
    if business_impact:
        print(f"Potential ARR Saved: ${business_impact.get('potential_arr_saved', 0):,.2f}")
    print(f"\nPredictions saved to: {PROCESSED_DATA_DIR / 'model_predictions.csv'}")
    print("\nNext step: Create Power BI dashboard using the predictions CSV")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
