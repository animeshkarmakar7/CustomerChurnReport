-- Executive Dashboard KPIs (MySQL syntax)
SELECT 
    -- Customer Metrics
    COUNT(*) as total_customers,
    SUM(CASE WHEN is_churned = 0 THEN 1 ELSE 0 END) as active_customers,
    SUM(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) as churned_customers,
    ROUND(AVG(CASE WHEN is_churned = 0 THEN 1 ELSE 0 END) * 100, 2) as retention_rate_pct,
    ROUND(AVG(CASE WHEN is_churned = 1 THEN 1 ELSE 0 END) * 100, 2) as churn_rate_pct,
    
    -- Revenue Metrics
    ROUND(SUM(CASE WHEN is_churned = 0 THEN monthly_charges ELSE 0 END), 2) as total_mrr,
    ROUND(AVG(CASE WHEN is_churned = 0 THEN monthly_charges END), 2) as avg_mrr_per_customer,
    ROUND(SUM(total_charges), 2) as total_revenue_all_time,
    ROUND(AVG(total_charges), 2) as avg_ltv,
    
    -- Contract Mix
    ROUND(AVG(CASE WHEN contract_type = 'Month-to-month' THEN 1 ELSE 0 END) * 100, 1) as pct_month_to_month,
    ROUND(AVG(CASE WHEN contract_type = 'One year' THEN 1 ELSE 0 END) * 100, 1) as pct_one_year,
    ROUND(AVG(CASE WHEN contract_type = 'Two year' THEN 1 ELSE 0 END) * 100, 1) as pct_two_year
    
FROM customers_cleaned;