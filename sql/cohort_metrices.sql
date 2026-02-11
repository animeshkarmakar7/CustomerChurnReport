-- Compare cohort metrics
SELECT 
    tenure_segment,
    COUNT(*) as customers,
    ROUND(AVG(CASE WHEN is_churned THEN 1.0 ELSE 0 END) * 100, 2) as churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) as avg_mrr,
    ROUND(AVG(total_charges), 2) as avg_ltv,
    ROUND(AVG(total_services), 2) as avg_services,
    ROUND(AVG(CASE WHEN contract_type != 'Month-to-month' THEN 1.0 ELSE 0 END) * 100, 1) as pct_annual_contract
FROM customer_features
GROUP BY tenure_segment
ORDER BY 
    CASE tenure_segment
        WHEN 'New (0 months)' THEN 1
        WHEN '0-12 months' THEN 2
        WHEN '13-24 months' THEN 3
        WHEN '25-48 months' THEN 4
        WHEN '48+ months' THEN 5
    END;