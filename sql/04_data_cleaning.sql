-- Create cleaned table with proper data types (MySQL syntax)
DROP TABLE IF EXISTS customers_cleaned;

CREATE TABLE customers_cleaned AS
SELECT 
    customerID,
    gender,
    -- MySQL uses TINYINT for boolean (1 = TRUE, 0 = FALSE)
    CASE WHEN SeniorCitizen = 1 THEN 1 ELSE 0 END as is_senior_citizen,
    CASE WHEN Partner = 'Yes' THEN 1 ELSE 0 END as has_partner,
    CASE WHEN Dependents = 'Yes' THEN 1 ELSE 0 END as has_dependents,
    tenure as tenure_months,
    
    -- Phone Services
    CASE WHEN PhoneService = 'Yes' THEN 1 ELSE 0 END as has_phone_service,
    CASE 
        WHEN MultipleLines = 'Yes' THEN 1 
        WHEN MultipleLines = 'No' THEN 0
        ELSE NULL 
    END as has_multiple_lines,
    
    -- Internet Services
    InternetService as internet_service_type,
    CASE 
        WHEN OnlineSecurity = 'Yes' THEN 1 
        WHEN OnlineSecurity = 'No' THEN 0
        ELSE NULL 
    END as has_online_security,
    CASE 
        WHEN OnlineBackup = 'Yes' THEN 1 
        WHEN OnlineBackup = 'No' THEN 0
        ELSE NULL 
    END as has_online_backup,
    CASE 
        WHEN DeviceProtection = 'Yes' THEN 1 
        WHEN DeviceProtection = 'No' THEN 0
        ELSE NULL 
    END as has_device_protection,
    CASE 
        WHEN TechSupport = 'Yes' THEN 1 
        WHEN TechSupport = 'No' THEN 0
        ELSE NULL 
    END as has_tech_support,
    CASE 
        WHEN StreamingTV = 'Yes' THEN 1 
        WHEN StreamingTV = 'No' THEN 0
        ELSE NULL 
    END as has_streaming_tv,
    CASE 
        WHEN StreamingMovies = 'Yes' THEN 1 
        WHEN StreamingMovies = 'No' THEN 0
        ELSE NULL 
    END as has_streaming_movies,
    
    -- Contract & Billing
    Contract as contract_type,
    CASE WHEN PaperlessBilling = 'Yes' THEN 1 ELSE 0 END as has_paperless_billing,
    PaymentMethod as payment_method,
    
    -- Financial Metrics
    MonthlyCharges as monthly_charges,
    -- Fix TotalCharges: convert to numeric, handle nulls
    -- MySQL uses CAST differently
    CASE 
        WHEN TotalCharges = '' OR TotalCharges = ' ' THEN MonthlyCharges
        ELSE CAST(TotalCharges AS DECIMAL(10,2))
    END as total_charges,
    
    -- Target Variable
    CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END as is_churned
    
FROM customers_raw;

-- Add primary key (MySQL requires separate ALTER)
ALTER TABLE customers_cleaned ADD PRIMARY KEY (customerID);

-- Verify cleaning
SELECT COUNT(*) FROM customers_cleaned;
SELECT * FROM customers_cleaned LIMIT 10;