-- Which feature combinations have lowest churn?
SELECT 
    has_tech_support,
    has_online_security,
    has_online_backup,
    COUNT(*) as customer_count,
    ROUND(AVG(CASE WHEN is_churned THEN 1.0 ELSE 0 END) * 100, 2) as churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) as avg_monthly_charges,
    ROUND(AVG(tenure_months), 1) as avg_tenure
FROM customer_features
WHERE internet_service_type != 'No'  -- Only customers with internet
GROUP BY has_tech_support, has_online_security, has_online_backup
HAVING COUNT(*) > 50  -- Only significant segments
ORDER BY churn_rate_pct;