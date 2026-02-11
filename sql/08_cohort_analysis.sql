-- Create cohort retention analysis
WITH cohort_base AS (
    SELECT 
        customerID,
        tenure_months,
        is_churned,
        -- Assign cohort based on tenure (reverse engineer signup month)
        CASE 
            WHEN tenure_months <= 12 THEN 'Cohort 2023-Q4'
            WHEN tenure_months <= 24 THEN 'Cohort 2022-Q4'
            WHEN tenure_months <= 36 THEN 'Cohort 2021-Q4'
            WHEN tenure_months <= 48 THEN 'Cohort 2020-Q4'
            ELSE 'Cohort 2019 or Earlier'
        END as cohort
    FROM customer_features
)
SELECT 
    cohort,
    COUNT(*) AS cohort_size,
    SUM(CASE WHEN NOT is_churned THEN 1 ELSE 0 END) AS still_active,
    ROUND(
        SUM(CASE WHEN NOT is_churned THEN 1 ELSE 0 END) 
        / COUNT(*) * 100, 2
    ) AS retention_rate_pct,
    ROUND(AVG(tenure_months), 1) AS avg_tenure_months
FROM cohort_base
GROUP BY cohort
ORDER BY cohort DESC;