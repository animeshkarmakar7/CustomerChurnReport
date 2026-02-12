# 🔧 MySQL Setup Guide

## Quick MySQL Configuration

### **Step 1: Update .env File**

Open `.env` and update with your MySQL credentials:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=customer_churn
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD_HERE
```

### **Step 2: Create Database in MySQL**

Open MySQL Workbench and run:

```sql
CREATE DATABASE customer_churn;
USE customer_churn;
```

### **Step 3: Test Connection**

```bash
python test_mysql_connection.py
```

You should see:
```
✓ SUCCESS: MySQL connection works!
```

### **Step 4: (Optional) Import Data to MySQL**

If you want to use MySQL instead of CSV files, run your SQL scripts in MySQL Workbench:

1. Open MySQL Workbench
2. Connect to your database
3. Run SQL scripts in order:
   - `sql/01_database_setup.sql`
   - `sql/02_create_tables.sql`
   - `sql/03_import_data.sql`
   - etc.

**Note:** The Python scripts will work with **either** MySQL database **OR** CSV files. If MySQL connection fails, they automatically fall back to CSV files.

---

## Troubleshooting

### **"Access denied for user 'root'@'localhost'"**
→ Wrong password in `.env` file. Update `DB_PASSWORD`

### **"Unknown database 'customer_churn'"**
→ Database doesn't exist. Run: `CREATE DATABASE customer_churn;`

### **"Can't connect to MySQL server"**
→ MySQL service not running. Start MySQL from Services or MySQL Workbench

### **Port 3306 already in use**
→ Another MySQL instance running, or check your MySQL port in Workbench

---

## Ready to Run!

Once connection test passes, run the pipeline:

```bash
venv\Scripts\activate
run_pipeline.bat
```

Or run scripts individually:

```bash
python src/01_data_exploration.py
python src/02_feature_engineering.py
python src/03_customer_segmentation.py
python src/04_model_training.py
python src/05_model_evaluation.py
```
