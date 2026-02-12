@echo off
REM ====================================================================
REM SaaS Churn Analytics - Complete Pipeline Runner
REM This script runs all analysis scripts in sequence
REM ====================================================================

echo.
echo ========================================================================
echo   SAAS CHURN ANALYTICS - COMPLETE PIPELINE
echo ========================================================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo WARNING: Virtual environment not activated!
    echo Please run: venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

echo Virtual environment: ACTIVE
echo Python version:
python --version
echo.

REM Create timestamp for this run
set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%

echo ========================================================================
echo STEP 1/5: DATA EXPLORATION
echo ========================================================================
echo.
python src/01_data_exploration.py
if errorlevel 1 (
    echo ERROR: Data exploration failed!
    pause
    exit /b 1
)
echo.
echo ✓ Data exploration completed successfully
echo.
pause

echo ========================================================================
echo STEP 2/5: FEATURE ENGINEERING
echo ========================================================================
echo.
python src/02_feature_engineering.py
if errorlevel 1 (
    echo ERROR: Feature engineering failed!
    pause
    exit /b 1
)
echo.
echo ✓ Feature engineering completed successfully
echo.
pause

echo ========================================================================
echo STEP 3/5: CUSTOMER SEGMENTATION
echo ========================================================================
echo.
python src/03_customer_segmentation.py
if errorlevel 1 (
    echo ERROR: Customer segmentation failed!
    pause
    exit /b 1
)
echo.
echo ✓ Customer segmentation completed successfully
echo.
pause

echo ========================================================================
echo STEP 4/5: MODEL TRAINING (This may take 10-15 minutes)
echo ========================================================================
echo.
python src/04_model_training.py
if errorlevel 1 (
    echo ERROR: Model training failed!
    pause
    exit /b 1
)
echo.
echo ✓ Model training completed successfully
echo.
pause

echo ========================================================================
echo STEP 5/5: MODEL EVALUATION
echo ========================================================================
echo.
python src/05_model_evaluation.py
if errorlevel 1 (
    echo ERROR: Model evaluation failed!
    pause
    exit /b 1
)
echo.
echo ✓ Model evaluation completed successfully
echo.

echo ========================================================================
echo   PIPELINE COMPLETED SUCCESSFULLY!
echo ========================================================================
echo.
echo All outputs saved to:
echo   - data/processed/     (CSV files)
echo   - models/             (Trained models)
echo   - visualizations/     (Charts and graphs)
echo   - reports/            (Analysis reports)
echo.
echo Next steps:
echo   1. Review visualizations in visualizations/ folder
echo   2. Read reports in reports/ folder
echo   3. Check predictions in data/processed/model_predictions.csv
echo   4. Create Power BI dashboard (optional)
echo.
echo ========================================================================
pause
