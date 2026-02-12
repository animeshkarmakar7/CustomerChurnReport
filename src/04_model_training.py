"""
Churn Prediction Model Training

This script trains multiple machine learning models to predict customer churn,
performs hyperparameter tuning, and saves the best model for production use.

Models Trained:
    - Logistic Regression (baseline)
    - Random Forest Classifier
    - XGBoost Classifier (primary model)

Output:
    - models/churn_predictor_xgboost.pkl
    - models/feature_scaler.pkl
    - models/model_metadata.json
    - Model performance comparison report
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
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (classification_report, confusion_matrix, roc_auc_score,
                             roc_curve, precision_recall_curve, f1_score, accuracy_score)
from imblearn.over_sampling import SMOTE

import matplotlib.pyplot as plt
import seaborn as sns

from src.config import PROCESSED_DATA_DIR, MODELS_DIR, VISUALIZATIONS_DIR, REPORTS_DIR, MODEL_CONFIG


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


def prepare_data(df):
    """Prepare data for model training."""
    print("\n" + "=" * 80)
    print("PREPARING DATA FOR TRAINING")
    print("=" * 80)
    
    # Separate features and target
    if 'Churn' not in df.columns:
        raise ValueError("Target variable 'Churn' not found in dataset")
    
    # Drop non-feature columns
    drop_cols = ['customerID', 'Churn']
    drop_cols = [col for col in drop_cols if col in df.columns]
    
    X = df.drop(columns=drop_cols)
    y = df['Churn']
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"\nClass distribution:")
    print(y.value_counts())
    print(f"Churn rate: {y.mean() * 100:.2f}%")
    
    # Handle any remaining non-numeric columns
    X = X.select_dtypes(include=[np.number])
    
    # Fill any missing values
    X = X.fillna(X.mean())
    
    print(f"\nFinal feature count: {X.shape[1]}")
    
    return X, y


def split_and_scale_data(X, y):
    """Split data into train/test sets and scale features."""
    print("\n" + "=" * 80)
    print("SPLITTING AND SCALING DATA")
    print("=" * 80)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=MODEL_CONFIG['test_size'], 
        random_state=MODEL_CONFIG['random_state'],
        stratify=y
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("✓ Features scaled using StandardScaler")
    
    # Save scaler
    scaler_path = MODELS_DIR / 'feature_scaler.pkl'
    joblib.dump(scaler, scaler_path)
    print(f"✓ Scaler saved to: {scaler_path}")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, X_train.columns.tolist()


def handle_class_imbalance(X_train, y_train):
    """Handle class imbalance using SMOTE."""
    print("\n" + "=" * 80)
    print("HANDLING CLASS IMBALANCE")
    print("=" * 80)
    
    print(f"Original class distribution:")
    print(y_train.value_counts())
    
    # Apply SMOTE
    smote = SMOTE(random_state=MODEL_CONFIG['random_state'])
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    print(f"\nResampled class distribution:")
    print(pd.Series(y_train_resampled).value_counts())
    print(f"✓ SMOTE applied successfully")
    
    return X_train_resampled, y_train_resampled


def train_baseline_model(X_train, X_test, y_train, y_test):
    """Train baseline Logistic Regression model."""
    print("\n" + "=" * 80)
    print("TRAINING BASELINE MODEL (Logistic Regression)")
    print("=" * 80)
    
    lr_model = LogisticRegression(random_state=MODEL_CONFIG['random_state'], max_iter=1000)
    lr_model.fit(X_train, y_train)
    
    # Predictions
    y_pred = lr_model.predict(X_test)
    y_pred_proba = lr_model.predict_proba(X_test)[:, 1]
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    f1 = f1_score(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"AUC-ROC: {auc:.4f}")
    print(f"F1-Score: {f1:.4f}")
    
    return lr_model, {'accuracy': accuracy, 'auc': auc, 'f1': f1}


def train_random_forest(X_train, X_test, y_train, y_test):
    """Train Random Forest model."""
    print("\n" + "=" * 80)
    print("TRAINING RANDOM FOREST MODEL")
    print("=" * 80)
    
    rf_model = RandomForestClassifier(
        n_estimators=100,
        random_state=MODEL_CONFIG['random_state'],
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    
    # Predictions
    y_pred = rf_model.predict(X_test)
    y_pred_proba = rf_model.predict_proba(X_test)[:, 1]
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    f1 = f1_score(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"AUC-ROC: {auc:.4f}")
    print(f"F1-Score: {f1:.4f}")
    
    return rf_model, {'accuracy': accuracy, 'auc': auc, 'f1': f1}


def train_xgboost_with_tuning(X_train, X_test, y_train, y_test):
    """Train XGBoost model with hyperparameter tuning."""
    print("\n" + "=" * 80)
    print("TRAINING XGBOOST MODEL WITH HYPERPARAMETER TUNING")
    print("=" * 80)
    
    # Define parameter grid
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0]
    }
    
    # Base model
    xgb_base = XGBClassifier(
        random_state=MODEL_CONFIG['random_state'],
        eval_metric='logloss'
    )
    
    # Grid search
    print("Performing grid search (this may take a few minutes)...")
    grid_search = GridSearchCV(
        xgb_base,
        param_grid,
        cv=MODEL_CONFIG['cv_folds'],
        scoring='roc_auc',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"\n✓ Best parameters: {grid_search.best_params_}")
    print(f"✓ Best CV AUC score: {grid_search.best_score_:.4f}")
    
    # Best model
    best_model = grid_search.best_estimator_
    
    # Predictions on test set
    y_pred = best_model.predict(X_test)
    y_pred_proba = best_model.predict_proba(X_test)[:, 1]
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    f1 = f1_score(y_test, y_pred)
    
    print(f"\nTest Set Performance:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"AUC-ROC: {auc:.4f}")
    print(f"F1-Score: {f1:.4f}")
    
    return best_model, {'accuracy': accuracy, 'auc': auc, 'f1': f1, 'best_params': grid_search.best_params_}


def compare_models(models_performance):
    """Compare performance of all models."""
    print("\n" + "=" * 80)
    print("MODEL COMPARISON")
    print("=" * 80)
    
    comparison_df = pd.DataFrame(models_performance).T
    print("\n", comparison_df)
    
    # Visualize comparison
    metrics = ['accuracy', 'auc', 'f1']
    comparison_df[metrics].plot(kind='bar', figsize=(12, 6))
    plt.title('Model Performance Comparison', fontsize=14, fontweight='bold')
    plt.xlabel('Model')
    plt.ylabel('Score')
    plt.legend(title='Metrics')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_DIR / '09_model_comparison.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved model comparison visualization")
    plt.close()
    
    # Select best model based on AUC
    best_model_name = comparison_df['auc'].idxmax()
    print(f"\n🏆 Best model: {best_model_name} (AUC: {comparison_df.loc[best_model_name, 'auc']:.4f})")
    
    return best_model_name


def save_model(model, model_name, performance_metrics, feature_names):
    """Save the trained model and metadata."""
    print("\n" + "=" * 80)
    print("SAVING MODEL")
    print("=" * 80)
    
    # Save model
    model_path = MODELS_DIR / 'churn_predictor_xgboost.pkl'
    joblib.dump(model, model_path)
    print(f"✓ Model saved to: {model_path}")
    
    # Save metadata
    metadata = {
        'model_name': model_name,
        'model_type': type(model).__name__,
        'performance_metrics': performance_metrics,
        'feature_count': len(feature_names),
        'feature_names': feature_names,
        'training_config': MODEL_CONFIG
    }
    
    metadata_path = MODELS_DIR / 'model_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved to: {metadata_path}")
    
    # Create training report
    report_path = REPORTS_DIR / 'model_training_report.txt'
    with open(report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("MODEL TRAINING REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Best Model: {model_name}\n")
        f.write(f"Model Type: {type(model).__name__}\n\n")
        
        f.write("PERFORMANCE METRICS:\n")
        f.write("-" * 40 + "\n")
        for metric, value in performance_metrics.items():
            if metric != 'best_params':
                f.write(f"{metric.upper()}: {value:.4f}\n")
        f.write("\n")
        
        if 'best_params' in performance_metrics:
            f.write("HYPERPARAMETERS:\n")
            f.write("-" * 40 + "\n")
            for param, value in performance_metrics['best_params'].items():
                f.write(f"{param}: {value}\n")
            f.write("\n")
        
        f.write(f"Total Features: {len(feature_names)}\n\n")
        
        f.write("OUTPUT FILES:\n")
        f.write("-" * 40 + "\n")
        f.write(f"- {model_path}\n")
        f.write(f"- {MODELS_DIR / 'feature_scaler.pkl'}\n")
        f.write(f"- {metadata_path}\n\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"✓ Training report saved to: {report_path}")


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("SAAS CHURN ANALYTICS - MODEL TRAINING")
    print("=" * 80 + "\n")
    
    # Load data
    df = load_data()
    
    # Prepare data
    X, y = prepare_data(df)
    
    # Split and scale
    X_train, X_test, y_train, y_test, scaler, feature_names = split_and_scale_data(X, y)
    
    # Handle class imbalance
    X_train_resampled, y_train_resampled = handle_class_imbalance(X_train, y_train)
    
    # Train models
    models_performance = {}
    
    # Baseline: Logistic Regression
    lr_model, lr_perf = train_baseline_model(X_train_resampled, X_test, y_train_resampled, y_test)
    models_performance['Logistic Regression'] = lr_perf
    
    # Random Forest
    rf_model, rf_perf = train_random_forest(X_train_resampled, X_test, y_train_resampled, y_test)
    models_performance['Random Forest'] = rf_perf
    
    # XGBoost with tuning
    xgb_model, xgb_perf = train_xgboost_with_tuning(X_train_resampled, X_test, y_train_resampled, y_test)
    models_performance['XGBoost'] = xgb_perf
    
    # Compare models
    best_model_name = compare_models(models_performance)
    
    # Select best model
    if best_model_name == 'XGBoost':
        best_model = xgb_model
        best_performance = xgb_perf
    elif best_model_name == 'Random Forest':
        best_model = rf_model
        best_performance = rf_perf
    else:
        best_model = lr_model
        best_performance = lr_perf
    
    # Save best model
    save_model(best_model, best_model_name, best_performance, feature_names)
    
    print("\n" + "=" * 80)
    print("MODEL TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nBest Model: {best_model_name}")
    print(f"AUC-ROC: {best_performance['auc']:.4f}")
    print(f"\nModel saved to: {MODELS_DIR / 'churn_predictor_xgboost.pkl'}")
    print("\nNext step: Run 05_model_evaluation.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
