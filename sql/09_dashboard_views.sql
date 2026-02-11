
SET GLOBAL event_scheduler = ON;


DROP TABLE IF EXISTS mv_executive_kpis;
DROP TABLE IF EXISTS mv_feature_adoption;
DROP TABLE IF EXISTS mv_cohort_retention;


CREATE TABLE mv_executive_kpis AS
SELECT 
    CURRENT_DATE() AS report_date,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN NOT is_churned THEN 1 ELSE 0 END) AS active_customers,
    ROUND(SUM(CASE WHEN NOT is_churned THEN monthly_charges ELSE 0 END), 2) AS total_mrr,
    ROUND(AVG(CASE WHEN NOT is_churned THEN monthly_charges END), 2) AS avg_mrr,
    ROUND(AVG(CASE WHEN is_churned THEN 1 ELSE 0 END) * 100, 2) AS churn_rate_pct,
    ROUND(AVG(total_charges), 2) AS avg_ltv,
    ROUND(AVG(tenure_months), 1) AS avg_tenure_months
FROM customer_features;



CREATE TABLE mv_feature_adoption AS
SELECT 
    'Online Security' AS feature_name,
    SUM(CASE WHEN has_online_security THEN 1 ELSE 0 END) AS adopted_count,
    ROUND(AVG(CASE WHEN has_online_security THEN 1 ELSE 0 END) * 100, 2) AS adoption_rate,
    ROUND(
        SUM(CASE WHEN has_online_security AND is_churned THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN has_online_security THEN 1 ELSE 0 END), 0) * 100, 2
    ) AS churn_with_feature,
    ROUND(
        SUM(CASE WHEN NOT has_online_security AND is_churned THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN NOT has_online_security THEN 1 ELSE 0 END), 0) * 100, 2
    ) AS churn_without_feature
FROM customer_features

UNION ALL

SELECT 
    'Tech Support',
    SUM(CASE WHEN has_tech_support THEN 1 ELSE 0 END),
    ROUND(AVG(CASE WHEN has_tech_support THEN 1 ELSE 0 END) * 100, 2),
    ROUND(
        SUM(CASE WHEN has_tech_support AND is_churned THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN has_tech_support THEN 1 ELSE 0 END), 0) * 100, 2
    ),
    ROUND(
        SUM(CASE WHEN NOT has_tech_support AND is_churned THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN NOT has_tech_support THEN 1 ELSE 0 END), 0) * 100, 2
    )
FROM customer_features;

CREATE TABLE mv_cohort_retention AS
SELECT 
    tenure_segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(CASE WHEN NOT is_churned THEN 1 ELSE 0 END) * 100, 2) AS retention_rate,
    ROUND(AVG(monthly_charges), 2) AS avg_mrr,
    ROUND(AVG(total_charges), 2) AS avg_ltv
FROM customer_features
GROUP BY tenure_segment;


DELIMITER $$

CREATE PROCEDURE refresh_materialized_views()
BEGIN

    /* Refresh Executive KPIs */
    TRUNCATE TABLE mv_executive_kpis;
    INSERT INTO mv_executive_kpis
    SELECT 
        CURRENT_DATE(),
        COUNT(*),
        SUM(CASE WHEN NOT is_churned THEN 1 ELSE 0 END),
        ROUND(SUM(CASE WHEN NOT is_churned THEN monthly_charges ELSE 0 END), 2),
        ROUND(AVG(CASE WHEN NOT is_churned THEN monthly_charges END), 2),
        ROUND(AVG(CASE WHEN is_churned THEN 1 ELSE 0 END) * 100, 2),
        ROUND(AVG(total_charges), 2),
        ROUND(AVG(tenure_months), 1)
    FROM customer_features;


    /* Refresh Feature Adoption */
    TRUNCATE TABLE mv_feature_adoption;
    INSERT INTO mv_feature_adoption
    SELECT 
        'Online Security',
        SUM(CASE WHEN has_online_security THEN 1 ELSE 0 END),
        ROUND(AVG(CASE WHEN has_online_security THEN 1 ELSE 0 END) * 100, 2),
        ROUND(
            SUM(CASE WHEN has_online_security AND is_churned THEN 1 ELSE 0 END) /
            NULLIF(SUM(CASE WHEN has_online_security THEN 1 ELSE 0 END), 0) * 100, 2
        ),
        ROUND(
            SUM(CASE WHEN NOT has_online_security AND is_churned THEN 1 ELSE 0 END) /
            NULLIF(SUM(CASE WHEN NOT has_online_security THEN 1 ELSE 0 END), 0) * 100, 2
        )
    FROM customer_features

    UNION ALL

    SELECT 
        'Tech Support',
        SUM(CASE WHEN has_tech_support THEN 1 ELSE 0 END),
        ROUND(AVG(CASE WHEN has_tech_support THEN 1 ELSE 0 END) * 100, 2),
        ROUND(
            SUM(CASE WHEN has_tech_support AND is_churned THEN 1 ELSE 0 END) /
            NULLIF(SUM(CASE WHEN has_tech_support THEN 1 ELSE 0 END), 0) * 100, 2
        ),
        ROUND(
            SUM(CASE WHEN NOT has_tech_support AND is_churned THEN 1 ELSE 0 END) /
            NULLIF(SUM(CASE WHEN NOT has_tech_support THEN 1 ELSE 0 END), 0) * 100, 2
        )
    FROM customer_features;


    TRUNCATE TABLE mv_cohort_retention;
    INSERT INTO mv_cohort_retention
    SELECT 
        tenure_segment,
        COUNT(*),
        ROUND(AVG(CASE WHEN NOT is_churned THEN 1 ELSE 0 END) * 100, 2),
        ROUND(AVG(monthly_charges), 2),
        ROUND(AVG(total_charges), 2)
    FROM customer_features
    GROUP BY tenure_segment;

END$$

DELIMITER ;

CALL refresh_materialized_views();


DROP EVENT IF EXISTS daily_refresh_mv;

CREATE EVENT daily_refresh_mv
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
CALL refresh_materialized_views();
