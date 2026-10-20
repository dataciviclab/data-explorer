-- Chi cattura la crescita — settori (v2)
-- Dataset: istat_sbs_imprese (mart_sbs_settore), eurostat_gva_nuts3
-- Anni: 2014-2024
--
-- Il consumer definisce le CTE {cte_sbs} (mart settoriale SBS) e {cte_gva}
-- (GVA Eurostat, CP_MEUR + PYP_MEUR per NACE).
--
-- Unità: VA e costo del lavoro per ora in euro; quote in percentuale.
-- I valori reali usano un deflatore GVA a catena, 2014=100, calcolato
-- dall'aggregato NACE più vicino alla sezione SBS.

WITH sbs AS (
    SELECT * FROM ({cte_sbs})
),
gva_raw AS (
    SELECT
        year AS anno,
        nace_r2,
        MAX(CASE WHEN unit = 'CP_MEUR' THEN value END) AS cp,
        MAX(CASE WHEN unit = 'PYP_MEUR' THEN value END) AS pyp
    FROM ({cte_gva})
    WHERE geo = 'IT'
      AND year BETWEEN 2014 AND 2024
      AND nace_r2 IN ('B-E', 'C', 'F', 'G-I', 'J', 'L', 'M_N', 'O-Q', 'R-U')
    GROUP BY year, nace_r2
),
gva_chain AS (
    SELECT
        anno,
        nace_r2,
        EXP(
            SUM(LN(cp / pyp)) OVER (
                PARTITION BY nace_r2
                ORDER BY anno
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            )
        ) AS chain
    FROM gva_raw
    WHERE cp > 0 AND pyp > 0
),
gva_defl AS (
    SELECT
        anno,
        nace_r2,
        chain / FIRST_VALUE(chain) OVER (
            PARTITION BY nace_r2 ORDER BY anno
        ) * 100 AS deflatore
    FROM gva_chain
),
mapping(nace_codice, gva_nace) AS (
    SELECT * FROM (VALUES
        ('B', 'B-E'),
        ('C', 'C'),
        ('D', 'B-E'),
        ('E', 'B-E'),
        ('F', 'F'),
        ('G', 'G-I'),
        ('H', 'G-I'),
        ('I', 'G-I'),
        ('J', 'J'),
        ('L', 'L'),
        ('M', 'M_N'),
        ('N', 'M_N'),
        ('P', 'O-Q'),
        ('Q', 'O-Q'),
        ('R', 'R-U'),
        ('S', 'R-U')
    ) AS t(nace_codice, gva_nace)
)
SELECT
    s.anno,
    s.nace_codice,
    s.nace,
    s.va_mila_eur,
    s.va_per_ora_eur,
    s.costo_lavoro_per_ora_eur,
    s.salario_per_ora_eur,
    s.quota_lavoro_pct,
    s.gos_su_va_pct,
    s.investimenti_su_va_pct,
    d.deflatore,
    s.va_per_ora_eur / (d.deflatore / 100.0) AS va_per_ora_reale,
    s.costo_lavoro_per_ora_eur / (d.deflatore / 100.0) AS costo_lavoro_per_ora_reale,
    s.salario_per_ora_eur / (d.deflatore / 100.0) AS salario_per_ora_reale
FROM sbs s
LEFT JOIN mapping m ON s.nace_codice = m.nace_codice
LEFT JOIN gva_defl d
    ON s.anno = d.anno
   AND m.gva_nace = d.nace_r2
ORDER BY s.anno, s.nace_codice
