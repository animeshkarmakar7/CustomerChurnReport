-- Segment customers by Recency, Frequency (services), Monetary
WITH rfm_scores AS (
    SELECT 
        customerID,
        tenure_months,
        total_services,
        monthly_charges,
        is_churned,
        -- R Score (Tenure - higher is better)
        NTILE(5) OVER (ORDER BY tenure_months DESC) as r_score,
        -- F Score (Services - more is better)
        NTILE(5) OVER (ORDER BY total_services DESC) as f_score,
        -- M Score (Revenue - higher is better)
        NTILE(5) OVER (ORDER BY monthly_charges DESC) as m_score
    FROM customer_features
)
SELECT 
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 4 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN m_score >= 4 THEN 'High Spenders'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'At Risk'
        WHEN r_score <= 2 AND is_churned THEN 'Lost'
        WHEN f_score >= 4 THEN 'Engaged'
        ELSE 'Average'
    END as customer_segment,
    COUNT(*) as customer_count,
    ROUND(AVG(CASE WHEN is_churned THEN 1.0 ELSE 0 END) * 100, 2) as churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) as avg_mrr,
    ROUND(AVG(total_services), 2) as avg_services,
    ROUND(AVG(tenure_months), 1) as avg_tenure
FROM rfm_scores
GROUP BY customer_segment
ORDER BY customer_count DESC;