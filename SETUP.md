# 🚀 Setup Guide - SaaS Churn Analytics

This guide will walk you through setting up and running the complete project.

---

## ⚡ Quick Setup (5 minutes)

### **Step 1: Install Python**
Download Python 3.8+ from [python.org](https://www.python.org/downloads/)

Verify installation:
```bash
python --version
```

### **Step 2: Create Virtual Environment**
```bash
cd d:\CustomerEarlyRisk

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

This will install all required Python packages (~5 minutes).

### **Step 4: Configure Database (Optional)**

If you want to use PostgreSQL:

1. Open `.env` file
2. Update with your database credentials:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=customer_churn
   DB_USER=postgres
   DB_PASSWORD=your_actual_password
   ```

**Note**: If you don't have PostgreSQL, the scripts will automatically use CSV files instead.

---

## 🎯 Running the Project

### **Option 1: Run All Scripts (Recommended)**

Execute scripts in order:

```bash
# 1. Data Exploration (5-10 minutes)
python src/01_data_exploration.py

# 2. Feature Engineering (3-5 minutes)
python src/02_feature_engineering.py

# 3. Customer Segmentation (5 minutes)
python src/03_customer_segmentation.py

# 4. Model Training (10-15 minutes - includes hyperparameter tuning)
python src/04_model_training.py

# 5. Model Evaluation (5 minutes)
python src/05_model_evaluation.py
```

**Total time**: ~30-40 minutes

### **Option 2: Run Individual Scripts**

Run any script independently:
```bash
python src/01_data_exploration.py
```

---

## 📂 What Gets Created

After running all scripts, you'll have:

### **1. Processed Data** (`data/processed/`)
- `customer_features.csv` - Engineered features
- `customer_segments.csv` - Customer segments
- `model_predictions.csv` - Churn predictions for all customers

### **2. Trained Models** (`models/`)
- `churn_predictor_xgboost.pkl` - Trained XGBoost model
- `feature_scaler.pkl` - Feature scaling transformer
- `model_metadata.json` - Model performance metrics

### **3. Visualizations** (`visualizations/`)
- 12+ charts and graphs (PNG files)
- Churn distribution, correlation heatmaps, ROC curves, etc.

### **4. Reports** (`reports/`)
- `eda_report.txt` - Exploratory data analysis summary
- `feature_engineering_report.txt` - Feature creation details
- `segmentation_report.txt` - Customer segment profiles
- `model_training_report.txt` - Model comparison
- `model_evaluation_report.txt` - Business impact analysis

---

## 🔍 Verifying Success

### **Check 1: Data Files Created**
```bash
dir data\processed
```
You should see 3 CSV files.

### **Check 2: Model Files Created**
```bash
dir models
```
You should see 3 files (2 .pkl files + 1 .json).

### **Check 3: Visualizations Created**
```bash
dir visualizations
```
You should see 12+ PNG image files.

### **Check 4: Model Performance**
Open `reports/model_evaluation_report.txt` and check:
- ROC-AUC Score should be > 0.80
- Business impact should show ARR saved

---

## ⚠️ Troubleshooting

### **Problem: "ModuleNotFoundError"**
**Solution**: Make sure virtual environment is activated and dependencies installed:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### **Problem: "Database connection failed"**
**Solution**: The scripts will automatically fall back to CSV files. No action needed.

If you want to use PostgreSQL:
1. Make sure PostgreSQL is running
2. Update `.env` with correct credentials
3. Run SQL scripts first

### **Problem: "FileNotFoundError: WA_Fn-UseC_-Telco-Customer-Churn.csv"**
**Solution**: Make sure the dataset is in `data/raw/` folder.

### **Problem: Script takes too long**
**Solution**: 
- Model training (script 4) can take 10-15 minutes due to hyperparameter tuning
- This is normal - it's testing multiple model configurations
- You can reduce `param_grid` in `src/04_model_training.py` for faster runs

### **Problem: "Memory Error"**
**Solution**: 
- Close other applications
- Reduce sample size in SHAP analysis (edit `src/05_model_evaluation.py`, line with `sample_size`)

---

## 🎨 Next Steps After Setup

### **1. Review Outputs**
- Open visualizations in `visualizations/` folder
- Read reports in `reports/` folder
- Check predictions in `data/processed/model_predictions.csv`

### **2. Customize for Your Data**
- Replace `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv` with your own dataset
- Update column names in `src/config.py` if needed
- Re-run all scripts

### **3. Create Power BI Dashboard** (Optional)
- Open Power BI Desktop
- Import `data/processed/model_predictions.csv`
- Import SQL exports from `data/exports/`
- Build interactive dashboard

### **4. Deploy to Production** (Advanced)
- Set up automated daily runs
- Integrate with CRM system
- Create email alerts for high-risk customers

---

## 📊 Understanding the Output

### **Model Predictions CSV**
```csv
customerID,churn_probability,churn_prediction,risk_segment,MonthlyCharges,tenure
7590-VHVEG,0.87,1,Critical,29.85,1
5575-GNVDE,0.23,0,Low,56.95,34
```

- `churn_probability`: 0-1 score (higher = more likely to churn)
- `churn_prediction`: 0 (won't churn) or 1 (will churn)
- `risk_segment`: Low, Medium, High, Critical

### **Business Impact**
Check `reports/model_evaluation_report.txt` for:
- Number of high-risk customers
- Revenue at risk
- Potential ARR saved through intervention
- ROI calculation

---

## 🔄 Re-running the Analysis

To re-run with fresh data:

```bash
# Delete processed files
del data\processed\*.csv
del models\*.pkl
del models\*.json
del visualizations\*.png
del reports\*.txt

# Run all scripts again
python src/01_data_exploration.py
python src/02_feature_engineering.py
python src/03_customer_segmentation.py
python src/04_model_training.py
python src/05_model_evaluation.py
```

---

## 💡 Tips for Best Results

1. **Run scripts in order** - Each script depends on outputs from previous ones
2. **Check reports after each script** - Verify outputs look correct
3. **Don't interrupt model training** - It takes time but produces best results
4. **Review visualizations** - They tell the story of your data
5. **Use predictions CSV for dashboards** - Perfect for Power BI/Tableau

---

## 📞 Getting Help

If you encounter issues:

1. Check error message carefully
2. Review this troubleshooting guide
3. Check `reports/` folder for clues
4. Verify all dependencies installed correctly
5. Make sure virtual environment is activated

---

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] All 5 scripts run successfully
- [ ] 3 CSV files in `data/processed/`
- [ ] 3 model files in `models/`
- [ ] 12+ visualizations in `visualizations/`
- [ ] 5 reports in `reports/`
- [ ] Model AUC-ROC > 0.80

**If all checked ✅ - Congratulations! Your project is ready! 🎉**

---

## 🚀 What's Next?

1. Review all visualizations and reports
2. Understand the business insights
3. Create Power BI dashboard (optional)
4. Add to your portfolio
5. Share on LinkedIn/GitHub

---

**Need more help? Check README.md for detailed documentation.**
