-- Chi cattura la crescita — macro
-- Dataset: eurostat_nama10_gdp, eurostat_labour_productivity_nuts3, eurostat_emp_nuts3
-- Anni: 1995-2024 (NAMA), 2000-2024 (produttività e occupazione)
--
-- Il consumer definisce le CTE {cte_nama}, {cte_prod}, {cte_emp}.

WITH nama AS (
    SELECT
        year AS anno,
        MAX(CASE WHEN na_item = 'D1' AND unit = 'CP_MEUR' THEN value END) AS d1,
        MAX(CASE WHEN na_item = 'D11' AND unit = 'CP_MEUR' THEN value END) AS d11,
        MAX(CASE WHEN na_item = 'B2A3G' AND unit = 'CP_MEUR' THEN value END) AS b2a3g,
        MAX(CASE WHEN na_item = 'B1G' AND unit = 'CP_MEUR' THEN value END) AS b1g,
        MAX(CASE WHEN na_item = 'B1GQ' AND unit = 'PD20_EUR' THEN value END) AS deflatore
    FROM ({cte_nama})
    WHERE geo = 'IT'
      AND year BETWEEN 1995 AND 2024
      AND (
          (na_item IN ('D1', 'D11', 'B2A3G', 'B1G') AND unit = 'CP_MEUR')
          OR (na_item = 'B1GQ' AND unit = 'PD20_EUR')
      )
    GROUP BY year
),
prod AS (
    SELECT
        year AS anno,
        MAX(value) AS prod_nominale
    FROM ({cte_prod})
    WHERE geo = 'IT'
      AND na_item = 'NLPR_PER'
      AND unit = 'EUR'
    GROUP BY year
),
emp AS (
    SELECT
        year AS anno,
        MAX(value) AS dipendenti_migliaia
    FROM ({cte_emp})
    WHERE geo = 'IT'
      AND nace_r2 = 'TOTAL'
      AND wstatus = 'SAL'
      AND unit = 'THS'
    GROUP BY year
)
SELECT
    n.anno,
    n.d1,
    n.d11,
    n.b2a3g,
    n.b1g,
    n.deflatore,
    n.d1 / NULLIF(n.b1g, 0) * 100 AS quota_lavoro_pct,
    n.b2a3g / NULLIF(n.b1g, 0) * 100 AS quota_capitale_pct,
    n.d11 * 1000 / NULLIF(e.dipendenti_migliaia, 0) AS salari_per_dipendente,
    n.d1 * 1000 / NULLIF(e.dipendenti_migliaia, 0) AS redditi_per_dipendente,
    p.prod_nominale,
    n.d11 * 1000 / NULLIF(e.dipendenti_migliaia, 0) / (n.deflatore / 100.0) AS salari_reali,
    n.d1 * 1000 / NULLIF(e.dipendenti_migliaia, 0) / (n.deflatore / 100.0) AS redditi_reali,
    p.prod_nominale / (n.deflatore / 100.0) AS produttivita_reale
FROM nama n
LEFT JOIN emp e ON n.anno = e.anno
LEFT JOIN prod p ON n.anno = p.anno
ORDER BY n.anno
