-- Create feature engineering table (MySQL)
DROP TABLE IF EXISTS customer_features;

CREATE TABLE customer_features AS
SELECT 
    c.*,
    
    -- Calculated Features
    ROUND(c.total_charges / NULLIF(c.tenure_months, 0), 2) as avg_monthly_spend,
    
    -- Feature Count (MySQL doesn't need CASE wrapping in parentheses)
    (CASE WHEN c.has_phone_service = 1 THEN 1 ELSE 0 END +
     CASE WHEN c.has_online_security = 1 THEN 1 ELSE 0 END +
     CASE WHEN c.has_online_backup = 1 THEN 1 ELSE 0 END +
     CASE WHEN c.has_device_protection = 1 THEN 1 ELSE 0 END +
     CASE WHEN c.has_tech_support = 1 THEN 1 ELSE 0 END +
     CASE WHEN c.has_streaming_tv = 1 THEN 1 ELSE 0 END +
     CASE WHEN c.has_streaming_movies = 1 THEN 1 ELSE 0 END) as total_services,
    
    -- Tenure Segments
    CASE 
        WHEN c.tenure_months = 0 THEN 'New (0 months)'
        WHEN c.tenure_months <= 12 THEN '0-12 months'
        WHEN c.tenure_months <= 24 THEN '13-24 months'
        WHEN c.tenure_months <= 48 THEN '25-48 months'
        ELSE '48+ months'
    END as tenure_segment,
    
    -- Revenue Segments
    CASE 
        WHEN c.monthly_charges < 30 THEN 'Low (<$30)'
        WHEN c.monthly_charges < 60 THEN 'Medium ($30-$60)'
        WHEN c.monthly_charges < 90 THEN 'High ($60-$90)'
        ELSE 'Premium ($90+)'
    END as revenue_segment,
    
    -- Customer Lifetime Value (projected)
    CASE 
        WHEN c.contract_type = 'Month-to-month' THEN c.monthly_charges * 12
        WHEN c.contract_type = 'One year' THEN c.monthly_charges * 24
        WHEN c.contract_type = 'Two year' THEN c.monthly_charges * 36
    END as projected_ltv,
    
    -- Engagement Score
    ROUND(
        (CASE WHEN c.has_phone_service = 1 THEN 1 ELSE 0 END +
         CASE WHEN c.has_online_security = 1 THEN 1.5 ELSE 0 END +
         CASE WHEN c.has_online_backup = 1 THEN 1 ELSE 0 END +
         CASE WHEN c.has_device_protection = 1 THEN 1 ELSE 0 END +
         CASE WHEN c.has_tech_support = 1 THEN 2 ELSE 0 END +
         CASE WHEN c.has_streaming_tv = 1 THEN 1 ELSE 0 END +
         CASE WHEN c.has_streaming_movies = 1 THEN 1 ELSE 0 END +
         CASE WHEN c.has_paperless_billing = 1 THEN 0.5 ELSE 0 END) / 10.0 * 10, 
    1) as engagement_score,
    
    -- Risk Indicators
    CASE 
        WHEN c.contract_type = 'Month-to-month' 
         AND c.tenure_months < 12 
         AND c.has_tech_support = 0 THEN 'High Risk'
        WHEN c.contract_type = 'Month-to-month' 
         AND c.tenure_months < 24 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as risk_category,
    
    -- Current timestamp (MySQL syntax)
    NOW() as feature_created_at
    
FROM customers_cleaned c;

-- Add indexes
CREATE INDEX idx_tenure_segment ON customer_features(tenure_segment);
CREATE INDEX idx_revenue_segment ON customer_features(revenue_segment);
CREATE INDEX idx_risk_category ON customer_features(risk_category);
CREATE INDEX idx_is_churned ON customer_features(is_churned);