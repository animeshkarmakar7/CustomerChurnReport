
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration (MySQL)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DB_NAME', 'customer_churn'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Project Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = BASE_DIR / 'dataset'  # Updated to point to dataset folder
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
EXPORTS_DIR = DATA_DIR / 'exports'
MODELS_DIR = BASE_DIR / 'models'
REPORTS_DIR = BASE_DIR / 'reports'
VISUALIZATIONS_DIR = BASE_DIR / 'visualizations'
SQL_DIR = BASE_DIR / 'sql'

# Create directories if they don't exist
for directory in [PROCESSED_DATA_DIR, EXPORTS_DIR, MODELS_DIR, REPORTS_DIR, VISUALIZATIONS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Model Configuration
MODEL_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'cv_folds': 5
}

# Feature Engineering
FEATURE_COLUMNS = [
    'PhoneService', 'InternetService', 'OnlineSecurity', 
    'OnlineBackup', 'DeviceProtection', 'TechSupport', 
    'StreamingTV', 'StreamingMovies'
]

# Risk Segments
RISK_BINS = [0, 0.2, 0.6, 0.8, 1.0]
RISK_LABELS = ['Low', 'Medium', 'High', 'Critical']
