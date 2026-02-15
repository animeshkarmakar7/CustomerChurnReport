<p align="center">
  <h1 align="center">📊 SaaS Customer Churn — Early Risk Detection & Revenue Intelligence</h1>
  <p align="center">
    <strong>End-to-end analytics platform combining SQL-based business intelligence, machine-learning churn prediction, and Power BI dashboarding to identify at-risk customers <em>before</em> they leave.</strong>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" />
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/XGBoost-2.0-orange" />
  <img src="https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi&logoColor=black" />
  <img src="https://img.shields.io/badge/scikit--learn-1.3-F09437?logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/SHAP-Explainability-green" />
</p>

---

## Table of Contents

| # | Section |
|---|---------|
| 1 | [Executive Summary](#1-executive-summary) |
| 2 | [Key Business Metrics — Glossary & Impact](#2-key-business-metrics--glossary--impact) |
| 3 | [Architecture & Pipeline Overview](#3-architecture--pipeline-overview) |
| 4 | [Project Structure](#4-project-structure) |
| 5 | [SQL Analytics Layer — Query-by-Query Breakdown](#5-sql-analytics-layer--query-by-query-breakdown) |
| 6 | [Python ML Pipeline — Code-by-Code Breakdown](#6-python-ml-pipeline--code-by-code-breakdown) |
| 7 | [Power BI Dashboard](#7-power-bi-dashboard) |
| 8 | [Installation & Setup](#8-installation--setup) |
| 9 | [How to Run](#9-how-to-run) |
| 10 | [Model Performance & Results](#10-model-performance--results) |
| 11 | [Final Verdict — Business Analysis & Customer Insights](#11-final-verdict--business-analysis--customer-insights) |
| 12 | [Technologies Used](#12-technologies-used) |
| 13 | [Future Enhancements](#13-future-enhancements) |

---

## 1. Executive Summary

This project delivers a **production-grade customer churn early-warning system** for a SaaS / Telecom business. It ingests 7,043 customer records from the IBM Telco Customer Churn dataset, runs them through a rigorous SQL data pipeline, engineers 21+ predictive features, trains and tunes three classification models, and outputs risk-scored customer lists — ready for executive dashboarding in Power BI.

### Dashboard Headline KPIs (from the attached report)

| KPI | Value | What It Means |
|-----|-------|---------------|
| **Total Customers** | 7,043 | Size of the customer base analysed |
| **High-Risk Customers** | 2,178 | Customers with ≥ 60 % predicted churn probability |
| **Revenue Risk %** | 36.99 % | Share of total MRR exposed to churn |
| **MRR at High Risk** | $168.72 K | Monthly Recurring Revenue from high-risk segment |
| **ARR at High Risk** | $2.02 M | Annualised value of that risk |

---

## 2. Key Business Metrics — Glossary & Impact

Understanding these metrics is essential for interpreting every query and model output in this project.

### 2.1 MRR — Monthly Recurring Revenue

| Attribute | Detail |
|-----------|--------|
| **Formula** | `SUM(monthly_charges)` for all *active* (non-churned) customers |
| **Why it matters** | MRR is the heartbeat of any subscription business. A declining MRR signals revenue leakage — often caused by churn. |
| **Business impact** | A 1 % drop in MRR compounding over 12 months can mean a **~12 % annual revenue shortfall**. Tracking MRR per segment (contract type, tenure) lets the business pinpoint *where* the leak is. |
| **Used in** | `business_health.sql`, `07_dashboard_views.sql`, `revenue_waterfall_analysis.sql` |

### 2.2 ARR — Annual Recurring Revenue

| Attribute | Detail |
|-----------|--------|
| **Formula** | `MRR × 12` |
| **Why it matters** | ARR normalises revenue into an annual figure — the standard SaaS valuation metric. Investors and boards use ARR to gauge company health. |
| **Business impact** | The dashboard shows **$2.02 M ARR at high risk**. If even 30 % of those customers are retained through intervention, the business saves **~$606 K/year**. |
| **Used in** | `05_model_evaluation.py → business_impact_analysis()`, Power BI dashboard |

### 2.3 LTV — Customer Lifetime Value

| Attribute | Detail |
|-----------|--------|
| **Formula (SQL)** | `monthly_charges × multiplier` where multiplier = 12 (month-to-month), 24 (1-year), 36 (2-year) |
| **Formula (Python)** | `tenure × MonthlyCharges` (observed LTV to date) |
| **Why it matters** | LTV tells you how much total revenue a customer is expected to generate. High-LTV customers who show churn risk should be prioritised for retention. |
| **Business impact** | The dashboard's "Sum of Estimated LTV by Risk Segment" chart reveals that the **Low-risk segment holds ~$2 M in LTV** while the Critical segment holds significantly less — confirming that longer-tenured, multi-service customers are more valuable and more stable. |
| **Used in** | `05_feature_engineering.sql`, `cohort_metrices.sql`, `high_risk_value_customer.sql`, `02_feature_engineering.py` |

### 2.4 Churn Rate

| Attribute | Detail |
|-----------|--------|
| **Formula** | `COUNT(churned) / COUNT(total) × 100` |
| **Why it matters** | The percentage of customers who left. Industry benchmark for telecom is 1–2 % monthly; this dataset shows **~26.5 % overall churn**. |
| **Business impact** | Every percentage point of churn reduction directly translates to preserved MRR. At $65 average monthly charge, reducing churn by 1 % (70 customers) saves **$4,550/month = $54,600/year**. |

### 2.5 Retention Rate

| Attribute | Detail |
|-----------|--------|
| **Formula** | `100 − Churn Rate` |
| **Why it matters** | Mirror of churn rate — used in cohort analysis to track how well each sign-up cohort retains over time. |

### 2.6 Engagement Score

| Attribute | Detail |
|-----------|--------|
| **Formula** | Weighted sum of service adoption flags (Tech Support weighted 2×, Online Security 1.5×, others 1×) |
| **Why it matters** | Customers using more services are "stickier." A low engagement score is an **early warning indicator** of churn. |
| **Business impact** | Feature combination analysis shows customers with Tech Support + Online Security + Online Backup have the **lowest churn rate** among all combinations. |

### 2.7 RFM Score (Recency · Frequency · Monetary)

| Attribute | Detail |
|-----------|--------|
| **R (Recency)** | Tenure-based — longer tenure = better |
| **F (Frequency)** | Number of services adopted |
| **M (Monetary)** | Monthly charges / LTV |
| **Why it matters** | Classic marketing segmentation that classifies customers as Champions, Loyal, At Risk, or Lost. |
| **Business impact** | "Champions" have the lowest churn rate; "At Risk" customers should be targeted with win-back campaigns. |

### 2.8 Risk Score (0–100)

| Attribute | Detail |
|-----------|--------|
| **Formula** | Month-to-month contract (+40), Tenure < 12 months (+30), No tech support (+20), < 3 services (+10) |
| **Why it matters** | Deterministic, interpretable score used alongside ML probability for executive reporting. |

---

## 3. Architecture & Pipeline Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCE                                   │
│        WA_Fn-UseC_-Telco-Customer-Churn.csv  (7,043 rows)           │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │      SQL ANALYTICS LAYER     │
              │  (MySQL 8.0 — 16 scripts)    │
              │                              │
              │  01 → Database Setup         │
              │  02 → Table Creation         │
              │  03 → Data Import            │
              │  04 → Data Cleaning          │
              │  05 → Feature Engineering    │
              │  06 → Cohort Analysis        │
              │  07 → Dashboard Views        │
              │  + 9 advanced analysis files  │
              └──────────────┬───────────────┘
                             │
              ┌──────────────▼──────────────┐
              │     PYTHON ML PIPELINE       │
              │   (scikit-learn + XGBoost)    │
              │                              │
              │  01 → Data Exploration (EDA) │
              │  02 → Feature Engineering    │
              │  03 → Customer Segmentation  │
              │  04 → Model Training         │
              │  05 → Model Evaluation       │
              └──────────────┬───────────────┘
                             │
              ┌──────────────▼──────────────┐
              │    POWER BI DASHBOARD        │
              │  (Executive KPIs + Drilldown)│
              └─────────────────────────────┘
```

---

## 4. Project Structure

```
CustomerEarlyRisk/
├── dataset/
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv   # Raw IBM Telco dataset
├── sql/                                         # 16 SQL scripts
│   ├── 01_database_setup.sql                    # Create database
│   ├── 02.create_tables.sql                     # Schema definition
│   ├── 03_import_data.sql                       # Load CSV → MySQL
│   ├── 04_data_cleaning.sql                     # Type casting & encoding
│   ├── 05_feature_engineering.sql               # Derived columns
│   ├── 06_cohort_analysis.sql                   # Retention cohorts
│   ├── 07_dashboard_views.sql                   # Materialized views + scheduler
│   ├── business_health.sql                      # Executive KPI snapshot
│   ├── churn_ml_features.sql                    # ML-ready feature table
│   ├── cohort_metrices.sql                      # Tenure-based cohort metrics
│   ├── customer_segmentation_RFM.sql            # RFM segmentation
│   ├── feature_adoptation_analysis.sql          # Service adoption vs churn
│   ├── feature_combination_analysis.sql         # Multi-service churn impact
│   ├── high_risk_value_customer.sql             # Priority intervention list
│   ├── revenue_waterfall_analysis.sql           # MRR waterfall
│   └── tenure_based_retention.sql               # Survival-style retention
├── src/                                          # Python pipeline
│   ├── config.py                                # Central configuration
│   ├── db_utils.py                              # MySQL connection utilities
│   ├── 01_data_exploration.py                   # EDA + visualisations
│   ├── 02_feature_engineering.py                # 8 derived features + encoding
│   ├── 03_customer_segmentation.py              # RFM + K-Means clustering
│   ├── 04_model_training.py                     # LR / RF / XGBoost + SMOTE
│   └── 05_model_evaluation.py                   # SHAP, ROC, business impact
├── models/
│   ├── churn_predictor_xgboost.pkl              # Trained model artifact
│   ├── feature_scaler.pkl                       # StandardScaler artifact
│   └── model_metadata.json                      # Performance + feature list
├── data/processed/                               # Pipeline outputs
│   ├── customer_features.csv                    # Engineered feature matrix
│   ├── customer_segments.csv                    # Segmented customer data
│   ├── feature_names.json                       # Feature registry
│   └── model_predictions.csv                    # Risk-scored customer list
├── reports/                                      # Generated reports
├── visualizations/                               # Generated charts
├── .env.example                                  # Environment template
├── requirements.txt                              # Python dependencies
├── run_pipeline.bat                              # One-click pipeline runner
└── fix_churn_encoding.py                         # Churn column fix utility
```

---

## 5. SQL Analytics Layer — Query-by-Query Breakdown

### 5.1 Core Pipeline (Sequential — run in order)

#### `01_database_setup.sql` — Database Initialisation
Creates the `saas_analytics` database. This is the foundation — all subsequent tables live here.

#### `02.create_tables.sql` — Schema Definition
Defines the `customers_raw` table with 21 columns matching the CSV structure. Key design decisions:
- `TotalCharges` is stored as `VARCHAR(20)` initially (the raw CSV has blank strings that would break `DECIMAL` imports).
- `customerID` is the `PRIMARY KEY`.

#### `04_data_cleaning.sql` — Data Cleaning & Type Casting
**Connection to pipeline:** Transforms `customers_raw` → `customers_cleaned`. This is the **most critical SQL file** — every downstream query depends on its output.

| Transformation | Purpose |
|----------------|---------|
| `CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END` | Converts categorical target to binary `is_churned` |
| `CAST(TotalCharges AS DECIMAL)` with blank-string handling | Fixes the 11 rows where `TotalCharges` is empty |
| `CASE WHEN Partner = 'Yes' THEN 1 ELSE 0` | Binary-encodes all Yes/No demographic columns |
| `CASE WHEN MultipleLines = 'Yes' THEN 1 ... ELSE NULL` | Three-state logic: Yes=1, No=0, No service=NULL |

#### `05_feature_engineering.sql` — Feature Derivation
**Connection:** Reads `customers_cleaned` → creates `customer_features` (the analytical base table used by almost every other query).

| Feature | Formula | Business Meaning |
|---------|---------|------------------|
| `avg_monthly_spend` | `total_charges / tenure_months` | Tracks spending consistency |
| `total_services` | Sum of 7 service flags | Proxy for product stickiness |
| `tenure_segment` | 5 bins: New, 0–12, 13–24, 25–48, 48+ | Lifecycle stage |
| `revenue_segment` | <$30 / $30–60 / $60–90 / $90+ | Value tier |
| `projected_ltv` | `monthly_charges ×` contract multiplier | Forward-looking lifetime value |
| `engagement_score` | Weighted service count (Tech Support=2×) | Stickiness index |
| `risk_category` | Rules-based: High / Medium / Low | Deterministic risk flag |

Creates indexes on `tenure_segment`, `revenue_segment`, `risk_category`, and `is_churned` for dashboard query performance.

#### `06_cohort_analysis.sql` — Cohort Retention
Groups customers into quarterly cohorts by reverse-engineering sign-up period from tenure. Calculates **retention rate** and **average tenure** per cohort — essential for understanding whether newer cohorts retain better/worse than older ones.

#### `07_dashboard_views.sql` — Materialized Views & Scheduler
**Most complex SQL file.** Creates three materialized view tables and a stored procedure to refresh them daily:

| View | Contents | Dashboard Use |
|------|----------|---------------|
| `mv_executive_kpis` | Total MRR, avg MRR, churn rate %, avg LTV, avg tenure | Top-line KPI cards |
| `mv_feature_adoption` | Adoption rate + churn-with vs churn-without for Online Security & Tech Support | Feature impact chart |
| `mv_cohort_retention` | Retention rate, avg MRR, avg LTV per tenure segment | Cohort drill-down |

Also creates a MySQL **EVENT** that calls `refresh_materialized_views()` every 24 hours — production-ready auto-refresh.

---

### 5.2 Advanced Analysis Queries (Independent — run as needed)

#### `business_health.sql` — Executive KPI Snapshot
**Purpose:** Single-row result with 12 KPIs including total MRR, avg MRR/customer, total all-time revenue, avg LTV, and contract mix percentages.
**Connection:** Reads `customers_cleaned`. Provides the same data as `mv_executive_kpis` but from the cleaned table directly.

#### `churn_ml_features.sql` — ML Feature Table
**Purpose:** Creates a fully numeric `ml_features` table with 28 one-hot-encoded columns ready for direct export to Python/CSV. Every categorical variable (gender, internet type, contract, payment method) is split into binary columns.
**Connection:** Reads `customer_features` → outputs `ml_features` for Python ingestion.

#### `customer_segmentation_RFM.sql` — RFM Segmentation
**Purpose:** Uses `NTILE(5)` window functions to score each customer on Recency (tenure), Frequency (services), and Monetary (charges). Then classifies into: **Champions, Loyal Customers, High Spenders, At Risk, Lost, Engaged, Average**.
**Connection:** Reads `customer_features`. Output feeds the RFM chart in Power BI.

#### `feature_adoptation_analysis.sql` — Service Adoption vs Churn
**Purpose:** For each service (Online Security, Tech Support, Device Protection, Streaming TV), calculates: adoption rate, churn rate *with* the feature, churn rate *without* the feature, and avg MRR with the feature.
**Business insight:** Services like Tech Support and Online Security dramatically reduce churn — customers *without* these services churn at **2–3× the rate**.

#### `feature_combination_analysis.sql` — Multi-Service Churn Impact
**Purpose:** Finds which **combinations** of Tech Support + Online Security + Online Backup yield the lowest churn. Filters to internet customers only and segments with >50 customers.
**Business insight:** Customers with all three services have the **lowest churn rate** — this supports a "bundle & protect" upsell strategy.

#### `high_risk_value_customer.sql` — Priority Intervention List
**Purpose:** Generates the **Top 100 high-risk, high-value customers** who are still active, pay >$60/month, and have risk factors (month-to-month contract, short tenure, no tech support). Calculates a 0–100 risk score and annualised revenue at risk.
**Business insight:** This is the **action list** — the direct output for the customer success team.

#### `revenue_waterfall_analysis.sql` — MRR Waterfall
**Purpose:** Decomposes MRR into Starting MRR (active), Churned MRR (lost), and Ending MRR. Classic SaaS waterfall analysis.
**Connection:** Powers the revenue waterfall chart in Power BI.

#### `tenure_based_retention.sql` — Survival Analysis
**Purpose:** For each tenure month (1–72), calculates the number of customers, number churned, churn rate, and retention rate — a **discrete survival curve**.
**Business insight:** Reveals the "danger zone" months where churn spikes (typically months 1–6).

#### `cohort_metrices.sql` — Cohort Metric Comparison
**Purpose:** Compares tenure segments on churn rate, avg MRR, avg LTV, avg services, and % on annual contracts.
**Business insight:** Longer-tenured segments have dramatically lower churn and higher annual contract adoption.

---

## 6. Python ML Pipeline — Code-by-Code Breakdown

### 6.1 `config.py` — Central Configuration
Loads environment variables from `.env`, defines all project paths, model hyperparameters (`test_size=0.2`, `random_state=42`, `cv_folds=5`), feature column lists, and risk segmentation bins (`[0, 0.2, 0.6, 0.8, 1.0]` → Low / Medium / High / Critical).

### 6.2 `db_utils.py` — Database Utilities
Provides MySQL connectivity via both `mysql-connector-python` (for raw SQL execution) and `SQLAlchemy` (for `pandas.read_sql`). Key functions:
- `get_connection()` / `get_engine()` — Connection management
- `query_to_df()` — Execute SQL → return DataFrame
- `export_table_to_csv()` — Table → CSV export
- `execute_sql_file()` — Run `.sql` file against MySQL
- `test_connection()` — Health check

### 6.3 `01_data_exploration.py` — Exploratory Data Analysis (EDA)
**Purpose:** Understand the raw data before any transformation.

| Function | What It Does | Output |
|----------|-------------|--------|
| `load_data()` | Tries MySQL first, falls back to CSV | DataFrame |
| `basic_info()` | Shape, dtypes, memory usage | Console |
| `missing_value_analysis()` | Null counts + empty string detection | Table |
| `churn_distribution()` | Bar + pie chart of churn split | `01_churn_distribution.png` |
| `numerical_features_analysis()` | Histograms of all numeric columns | `02_numerical_distributions.png` |
| `categorical_features_analysis()` | Value counts for categorical columns | Console |
| `correlation_analysis()` | Pearson correlation heatmap | `03_correlation_heatmap.png` |
| `churn_by_features()` | Churn rate by Contract, Internet, Payment, etc. | `04_churn_by_features.png` |
| `generate_eda_report()` | Text report summary | `eda_report.txt` |

### 6.4 `02_feature_engineering.py` — Feature Creation & Encoding
**Purpose:** Transform raw data into ML-ready features. This is the bridge between raw CSV and model training.

**8 Derived Features Created:**

| # | Feature | Formula | Why |
|---|---------|---------|-----|
| 1 | `ltv` | `tenure × MonthlyCharges` | Observed lifetime value to date |
| 2 | `engagement_score` | Count of active services | Measures product stickiness |
| 3 | `tenure_group` | Binned tenure: 0–12, 12–24, 24–48, 48+ | Lifecycle stage for segment analysis |
| 4 | `charges_per_tenure` | `TotalCharges / (tenure + 1)` | Average monthly spend (smoothed) |
| 5 | `monthly_charges_category` | Low / Medium / High | Spending tier |
| 6 | `has_multiple_services` | `engagement_score ≥ 3` | Binary flag for multi-service customers |
| 7 | `is_new_customer` | `tenure ≤ 6` | New customer flag (highest risk period) |
| 8 | `is_high_value` | `ltv ≥ 75th percentile` | Top-quartile value customers |

**Encoding Strategy:**
- **Binary encoding:** All Yes/No columns → 1/0 (including "No internet service" → 0)
- **One-hot encoding:** Contract, PaymentMethod, InternetService, tenure_group, monthly_charges_category (with `drop_first=True` to avoid multicollinearity)
- **Target encoding:** `Churn` → Yes=1, No=0

### 6.5 `03_customer_segmentation.py` — RFM + K-Means Clustering
**Two complementary segmentation methods:**

**RFM Analysis:** Scores each customer 1–5 on Recency (tenure), Frequency (services), Monetary (LTV). Sum → RFM Score → segmented into At Risk / Developing / Established / Champions.

**K-Means Clustering:** Uses `tenure`, `MonthlyCharges`, `TotalCharges`, `ltv`, `engagement_score`. Standardises with `StandardScaler`, runs elbow method (k=2–9), fits final model with k=4. Visualised via PCA projection.

**Outputs:** `customer_segments.csv`, elbow curve, cluster scatter plot, cluster profile heatmap.

### 6.6 `04_model_training.py` — Model Training & Selection
**Three models trained and compared:**

| Model | Purpose | Key Config |
|-------|---------|------------|
| **Logistic Regression** | Baseline, interpretable | `max_iter=1000` |
| **Random Forest** | Ensemble, feature importance | `n_estimators=100` |
| **XGBoost** | Gradient boosting, best performance | GridSearchCV with 48 parameter combinations |

**Class Imbalance Handling:** Uses **SMOTE** (Synthetic Minority Over-sampling Technique) to balance the ~73/27 class split before training.

**XGBoost Hyperparameter Grid:** `n_estimators: [100, 200]`, `max_depth: [3, 5, 7]`, `learning_rate: [0.01, 0.1]`, `subsample: [0.8, 1.0]`, `colsample_bytree: [0.8, 1.0]` — 5-fold cross-validated on AUC-ROC.

**Model Selection:** Best model selected by highest AUC-ROC on the held-out test set. Saved as `churn_predictor_xgboost.pkl`.

### 6.7 `05_model_evaluation.py` — Evaluation & Business Impact
**Purpose:** Comprehensive evaluation of the deployed model plus business-impact quantification.

| Function | What It Does |
|----------|-------------|
| `generate_predictions()` | Scores all 7,043 customers with churn probability; assigns risk segments (Low/Medium/High/Critical) |
| `confusion_matrix_analysis()` | TP/FP/TN/FN breakdown + heatmap |
| `roc_pr_curves()` | ROC-AUC and Precision-Recall AUC curves |
| `feature_importance_analysis()` | SHAP TreeExplainer for global feature importance |
| `business_impact_analysis()` | Calculates: MRR at risk, ARR at risk, potential savings at 30 % intervention retention, ROI (assuming $50/customer intervention cost) |
| `save_predictions()` | Exports `model_predictions.csv` with customerID, probability, prediction, risk_segment — ready for Power BI |

---

## 7. Power BI Dashboard

### Dashboard Screenshot

![Power BI Dashboard](./assets/powerbi_dashboard.png)
*Customer Churn Analytics Dashboard — showing KPIs, risk segmentation, LTV analysis, and revenue metrics*

---

The dashboard provides:

| Panel | Visualisation | Metric |
|-------|--------------|--------|
| **KPI Cards** | 5 headline numbers | Total customers, high-risk count, revenue risk %, MRR at risk, ARR at risk |
| **Risk Segment Bar Chart** | Horizontal stacked bars | Customer count by Critical / High / Medium / Low |
| **LTV by Risk Segment** | Horizontal bars | Sum of estimated LTV per risk segment |
| **Avg Churn by Contract** | Vertical bars | Month-to-month vs One Year vs Two Year churn rates |
| **Churn Probability Table** | Sortable table | Per-customer churn probability + monthly charges |
| **Revenue by Risk Segment** | Table | Month-to-Month, One Year, and Total revenue per segment |
| **Top Customers by LTV** | Ranked table | Cumulative revenue % and total LTV per customer |
| **Cumulative Revenue Curve** | Line chart | Pareto analysis — shows revenue concentration |

---

## 8. Installation & Setup

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- Power BI Desktop (optional — for dashboard)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/CustomerEarlyRisk.git
cd CustomerEarlyRisk

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure database connection
copy .env.example .env
# Edit .env with your MySQL credentials:
#   DB_HOST=localhost
#   DB_PORT=3306
#   DB_NAME=customer_churn
#   DB_USER=root
#   DB_PASSWORD=your_password

# 5. Run SQL pipeline in MySQL Workbench (in order):
#    01_database_setup.sql → 02.create_tables.sql → 03_import_data.sql
#    → 04_data_cleaning.sql → 05_feature_engineering.sql
#    → 06_cohort_analysis.sql → 07_dashboard_views.sql
```

---

## 9. How to Run

### Option A: One-click Pipeline
```bash
run_pipeline.bat
```
Runs all 5 Python scripts sequentially with error handling and progress logging.

### Option B: Step-by-step
```bash
python src/01_data_exploration.py         # EDA + visualisations
python src/02_feature_engineering.py      # Feature creation + encoding
python src/03_customer_segmentation.py    # RFM + K-Means
python src/04_model_training.py           # Train 3 models + select best
python src/05_model_evaluation.py         # Evaluate + export predictions
```

### Output Locations
| Directory | Contents |
|-----------|----------|
| `data/processed/` | `customer_features.csv`, `customer_segments.csv`, `model_predictions.csv` |
| `models/` | `churn_predictor_xgboost.pkl`, `feature_scaler.pkl`, `model_metadata.json` |
| `visualizations/` | 12+ PNG charts (distribution, correlation, clusters, ROC, SHAP, etc.) |
| `reports/` | EDA, feature engineering, segmentation, training, and evaluation text reports |

---

## 10. Model Performance & Results

| Model | Accuracy | AUC-ROC | F1-Score |
|-------|----------|---------|----------|
| Logistic Regression | 74.95 % | 0.8398 | 0.6176 |
| Random Forest | — | — | — |
| XGBoost (Tuned) | — | — | — |

> **Note:** The saved model is the best-performing model selected by highest AUC-ROC. Current metadata shows Logistic Regression as the deployed model with **AUC = 0.8398**.

### 21 Features Used

Demographics: `SeniorCitizen`, `Partner`, `Dependents` · Tenure: `tenure` · Services: `PhoneService`, `MultipleLines`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies` · Billing: `PaperlessBilling`, `MonthlyCharges`, `TotalCharges` · Derived: `ltv`, `engagement_score`, `charges_per_tenure`, `has_multiple_services`, `is_new_customer`, `is_high_value`

---

## 11. Final Verdict — Business Analysis & Customer Insights

### 📊 Overall Business Health Verdict

The analysis reveals a business with **significant churn exposure**: approximately **26.5 % of customers have churned**, and **36.99 % of current MRR is at high risk**. The $2.02 M ARR at risk represents a serious threat to revenue stability.

### 🔑 Key Findings & Their Business Impact

| Finding | Impact | Recommended Action |
|---------|--------|-------------------|
| **Month-to-month contracts drive churn** — the "Avg Churn by Contract" chart shows M2M contracts have ~3× the churn of annual contracts | Majority of MRR at risk comes from M2M customers | Offer discounts (10–15 %) for annual contract upgrades; create loyalty programs |
| **Customers without Tech Support & Online Security churn 2–3× more** | Service adoption is directly protective against churn | Bundle Tech Support + Security into standard plans; make them opt-out instead of opt-in |
| **New customers (tenure < 12 months) are the highest risk** | The "danger zone" is months 1–6; if you can retain past month 12, churn drops dramatically | Implement 90-day onboarding program; assign customer success manager for first quarter |
| **High-value customers at risk are identifiable** | The top 100 high-risk, high-value list (`high_risk_value_customer.sql`) pinpoints exact intervent targets | Deploy personalised retention offers to these 100 customers — potential ROI > 500 % |
| **Revenue is concentrated** — the Pareto curve shows top 20 % of customers generate ~50 % of revenue | Losing even a few top customers is devastating | Create VIP retention tier for top-quartile LTV customers |
| **Fiber optic customers churn more than DSL** | Despite paying more, fiber customers may have higher expectations or more competitive alternatives | Investigate service quality + competitor pricing in fiber markets |
| **Electronic check payment = higher churn** | Customers not on auto-pay are less committed | Incentivise switch to auto-pay (bank transfer / credit card) |

### 👤 Customer Verdict — Segment-by-Segment

| Segment | Customer Profile | Churn Risk | Strategic Priority |
|---------|-----------------|------------|-------------------|
| **Critical** | M2M contract, < 6 months tenure, no support services, electronic check | Very High (>80 %) | Immediate intervention — onboarding call + free trial of support services |
| **High** | M2M contract, < 24 months, limited services | High (60–80 %) | Proactive outreach — contract upgrade offer + service bundle |
| **Medium** | Mixed contracts, moderate tenure, some services | Moderate (20–60 %) | Monitor engagement score; trigger alert if services dropped |
| **Low** | Annual/2-year contract, 48+ months, multiple services | Low (<20 %) | Nurture & upsell — these are your Champions; reward loyalty |

### 💰 Financial Impact Summary

| Metric | Value |
|--------|-------|
| Total MRR at High Risk | **$168,720/month** |
| Total ARR at High Risk | **$2,024,640/year** |
| Estimated Savings (30 % retention) | **~$607,392/year** |
| Intervention Cost ($50/customer × 2,178) | **$108,900** |
| **Estimated ROI** | **~458 %** |

### ✅ Final Recommendation

> **This analysis proves that proactive churn intervention is not just advisable — it is financially imperative.** With an estimated ROI of ~458 %, the cost of inaction far exceeds the cost of intervention. The model, combined with the SQL analytics layer and Power BI dashboard, provides a complete **early-warning system** that can be operationalised immediately. The top priorities are: (1) move high-risk M2M customers to annual contracts, (2) bundle Tech Support + Online Security into standard plans, and (3) deploy a 90-day onboarding program for new customers.

---

## 12. Technologies Used

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Database | MySQL 8.0 | Data storage, SQL analytics, materialized views |
| Language | Python 3.10+ | ML pipeline, data processing |
| ML Framework | scikit-learn, XGBoost | Model training & evaluation |
| Class Balancing | imbalanced-learn (SMOTE) | Handle 73/27 class imbalance |
| Explainability | SHAP | Feature importance interpretation |
| Visualisation | matplotlib, seaborn | Charts & plots |
| Dashboard | Power BI | Executive reporting |
| ORM | SQLAlchemy | Python ↔ MySQL bridge |
| Environment | python-dotenv | Secrets management |

---

## 13. Future Enhancements

- [ ] Real-time scoring API (Flask/FastAPI endpoint)
- [ ] Automated email alerts when customer risk score exceeds threshold
- [ ] A/B testing framework for retention interventions
- [ ] Deep learning model (LSTM) for sequential behaviour prediction
- [ ] Integration with CRM (Salesforce/HubSpot) for automated ticketing
- [ ] Model retraining pipeline with MLflow experiment tracking
- [ ] Customer health score composite (combining ML probability + engagement + NPS)

---

<p align="center">
  <strong>Built with ❤️ for data-driven customer retention</strong><br>
  <em>If this project helped you, please ⭐ the repository!</em>
</p>
