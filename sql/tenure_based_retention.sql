-- Retention by tenure month (survival analysis)
SELECT 
    tenure_months,
    COUNT(*) as customers_at_tenure,
    SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) as churned_at_tenure,
    ROUND(AVG(CASE WHEN is_churned THEN 1.0 ELSE 0 END) * 100, 2) as churn_rate_pct,
    -- Cumulative retention
    ROUND(AVG(CASE WHEN NOT is_churned THEN 1.0 ELSE 0 END) * 100, 2) as retention_rate_pct
FROM customer_features
WHERE tenure_months > 0
GROUP BY tenure_months
ORDER BY tenure_months;