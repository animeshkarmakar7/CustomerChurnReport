-- Feature adoption and churn impact (MySQL)
SELECT 
    'Online Security' as feature_name,
    SUM(CASE WHEN has_online_security = 1 THEN 1 ELSE 0 END) as adopted_count,
    ROUND(AVG(CASE WHEN has_online_security = 1 THEN 1.0 ELSE 0 END) * 100, 2) as adoption_rate_pct,
    ROUND(AVG(CASE WHEN has_online_security = 1 AND is_churned = 1 THEN 1.0 
              WHEN has_online_security = 1 THEN 0 END) * 100, 2) as churn_rate_with_feature,
    ROUND(AVG(CASE WHEN COALESCE(has_online_security, 0) = 0 AND is_churned = 1 THEN 1.0 
              WHEN COALESCE(has_online_security, 0) = 0 THEN 0 END) * 100, 2) as churn_rate_without_feature,
    ROUND(AVG(CASE WHEN has_online_security = 1 THEN monthly_charges END), 2) as avg_mrr_with_feature
FROM customer_features

UNION ALL

SELECT 
    'Tech Support',
    SUM(CASE WHEN has_tech_support = 1 THEN 1 ELSE 0 END),
    ROUND(AVG(CASE WHEN has_tech_support = 1 THEN 1.0 ELSE 0 END) * 100, 2),
    ROUND(AVG(CASE WHEN has_tech_support = 1 AND is_churned = 1 THEN 1.0 
              WHEN has_tech_support = 1 THEN 0 END) * 100, 2),
    ROUND(AVG(CASE WHEN COALESCE(has_tech_support, 0) = 0 AND is_churned = 1 THEN 1.0 
              WHEN COALESCE(has_tech_support, 0) = 0 THEN 0 END) * 100, 2),
    ROUND(AVG(CASE WHEN has_tech_support = 1 THEN monthly_charges END), 2)
FROM customer_features

UNION ALL

SELECT 
    'Device Protection',
    SUM(CASE WHEN has_device_protection = 1 THEN 1 ELSE 0 END),
    ROUND(AVG(CASE WHEN has_device_protection = 1 THEN 1.0 ELSE 0 END) * 100, 2),
    ROUND(AVG(CASE WHEN has_device_protection = 1 AND is_churned = 1 THEN 1.0 
              WHEN has_device_protection = 1 THEN 0 END) * 100, 2),
    ROUND(AVG(CASE WHEN COALESCE(has_device_protection, 0) = 0 AND is_churned = 1 THEN 1.0 
              WHEN COALESCE(has_device_protection, 0) = 0 THEN 0 END) * 100, 2),
    ROUND(AVG(CASE WHEN has_device_protection = 1 THEN monthly_charges END), 2)
FROM customer_features

UNION ALL

SELECT 
    'Streaming TV',
    SUM(CASE WHEN has_streaming_tv = 1 THEN 1 ELSE 0 END),
    ROUND(AVG(CASE WHEN has_streaming_tv = 1 THEN 1.0 ELSE 0 END) * 100, 2),
    ROUND(AVG(CASE WHEN has_streaming_tv = 1 AND is_churned = 1 THEN 1.0 
              WHEN has_streaming_tv = 1 THEN 0 END) * 100, 2),
    ROUND(AVG(CASE WHEN COALESCE(has_streaming_tv, 0) = 0 AND is_churned = 1 THEN 1.0 
              WHEN COALESCE(has_streaming_tv, 0) = 0 THEN 0 END) * 100, 2),
    ROUND(AVG(CASE WHEN has_streaming_tv = 1 THEN monthly_charges END), 2)
FROM customer_features

ORDER BY churn_rate_with_feature;