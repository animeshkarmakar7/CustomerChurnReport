-- Identify high-risk, high-value customers for intervention
SELECT 
    customerID,
    monthly_charges,
    total_services,
    tenure_months,
    contract_type,
    risk_category,
    engagement_score,
    projected_ltv,
    -- Calculate risk score (0-100)
    ROUND(
        (CASE WHEN contract_type = 'Month-to-month' THEN 40 ELSE 10 END +
         CASE WHEN tenure_months < 12 THEN 30 ELSE 5 END +
         CASE WHEN NOT has_tech_support THEN 20 ELSE 0 END +
         CASE WHEN total_services < 3 THEN 10 ELSE 0 END)
    , 0) as risk_score,
    -- Revenue at risk
    ROUND(monthly_charges * 12, 2) as annual_revenue_at_risk
FROM customer_features
WHERE NOT is_churned
  AND monthly_charges > 60  -- High-value customers
  AND (
      contract_type = 'Month-to-month' OR
      tenure_months < 12 OR
      NOT has_tech_support
  )
ORDER BY risk_score DESC, monthly_charges DESC
LIMIT 100;