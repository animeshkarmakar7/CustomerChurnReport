-- Create feature table for machine learning
CREATE TABLE ml_features AS
SELECT 
    customerID,
    
    -- Demographics
    CASE WHEN gender = 'Male' THEN 1 ELSE 0 END as gender_male,
    CASE WHEN is_senior_citizen THEN 1 ELSE 0 END as is_senior,
    CASE WHEN has_partner THEN 1 ELSE 0 END as has_partner,
    CASE WHEN has_dependents THEN 1 ELSE 0 END as has_dependents,
    
    -- Tenure
    tenure_months,
    CASE WHEN tenure_months < 12 THEN 1 ELSE 0 END as is_new_customer,
    
    -- Services (Features)
    CASE WHEN has_phone_service THEN 1 ELSE 0 END as has_phone,
    CASE WHEN has_online_security THEN 1 ELSE 0 END as has_security,
    CASE WHEN has_online_backup THEN 1 ELSE 0 END as has_backup,
    CASE WHEN has_device_protection THEN 1 ELSE 0 END as has_protection,
    CASE WHEN has_tech_support THEN 1 ELSE 0 END as has_support,
    CASE WHEN has_streaming_tv THEN 1 ELSE 0 END as has_tv,
    CASE WHEN has_streaming_movies THEN 1 ELSE 0 END as has_movies,
    total_services,
    
    -- Internet
    CASE WHEN internet_service_type = 'DSL' THEN 1 ELSE 0 END as internet_dsl,
    CASE WHEN internet_service_type = 'Fiber optic' THEN 1 ELSE 0 END as internet_fiber,
    CASE WHEN internet_service_type = 'No' THEN 1 ELSE 0 END as internet_none,
    
    -- Contract
    CASE WHEN contract_type = 'Month-to-month' THEN 1 ELSE 0 END as contract_monthly,
    CASE WHEN contract_type = 'One year' THEN 1 ELSE 0 END as contract_one_year,
    CASE WHEN contract_type = 'Two year' THEN 1 ELSE 0 END as contract_two_year,
    
    -- Billing
    CASE WHEN has_paperless_billing THEN 1 ELSE 0 END as paperless,
    CASE WHEN payment_method = 'Electronic check' THEN 1 ELSE 0 END as payment_echeck,
    CASE WHEN payment_method = 'Mailed check' THEN 1 ELSE 0 END as payment_mailed,
    CASE WHEN payment_method = 'Bank transfer (automatic)' THEN 1 ELSE 0 END as payment_bank,
    CASE WHEN payment_method = 'Credit card (automatic)' THEN 1 ELSE 0 END as payment_credit,
    
    -- Financial
    monthly_charges,
    total_charges,
    engagement_score,
    
    -- Target Variable
    CASE WHEN is_churned THEN 1 ELSE 0 END as churn
    
FROM customer_features;

-- Export to CSV for Python ML
COPY ml_features TO '/path/to/ml_features.csv' DELIMITER ',' CSV HEADER;