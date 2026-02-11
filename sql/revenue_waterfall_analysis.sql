-- MRR waterfall: New, Expansion, Contraction, Churn
SELECT 
    'Starting MRR (Active)' as category,
    ROUND(SUM(CASE WHEN NOT is_churned THEN monthly_charges ELSE 0 END), 2) as amount,
    1 as sort_order
FROM customer_features

UNION ALL

SELECT 
    'Churned MRR',
    -1 * ROUND(SUM(CASE WHEN is_churned THEN monthly_charges ELSE 0 END), 2),
    2
FROM customer_features

UNION ALL

SELECT 
    'Ending MRR',
    ROUND(SUM(CASE WHEN NOT is_churned THEN monthly_charges ELSE 0 END) - 
          SUM(CASE WHEN is_churned THEN monthly_charges ELSE 0 END), 2),
    3
FROM customer_features

ORDER BY sort_order;