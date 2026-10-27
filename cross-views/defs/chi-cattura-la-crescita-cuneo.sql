-- Chi cattura la crescita — cuneo fiscale e distribuzione IRPEF
-- Dataset: oecd_taxing_wages, irpef_comunale
-- Anni: 2015-2023
--
-- Il consumer definisce le CTE {cte_oecd}, {cte_irpef}.
-- OECD: single, no children, 100% average wage.

WITH oecd AS (
    SELECT
        anno,
        MAX(CASE WHEN misura = 'AV_TW' AND unita_label = 'Percentage of labour costs' THEN valore END) AS cuneo_pct,
        MAX(CASE WHEN misura = 'AV_ITR' AND unita_label = 'Percentage of gross wage earnings' THEN valore END) AS imposta_media_pct,
        MAX(CASE WHEN misura = 'NIAT' AND unita_label = 'National currency' THEN valore END) AS netto_eur
    FROM ({cte_oecd})
    WHERE ref_area = 'ITA'
      AND tipo_famiglia = 'S_C0'
      AND reddito_principale = 'AW100'
      AND anno BETWEEN 2015 AND 2023
    GROUP BY anno
),
irpef_raw AS (
    SELECT
        anno_di_imposta AS anno,
        SUM(reddito_complessivo_minore_o_uguale_a_zero_euro_eur) AS e_le0,
        SUM(reddito_complessivo_da_0_a_10000_euro_eur) AS e0_10,
        SUM(reddito_complessivo_da_10000_a_15000_euro_eur) AS e10_15,
        SUM(reddito_complessivo_da_15000_a_26000_euro_eur) AS e15_26,
        SUM(reddito_complessivo_da_26000_a_55000_euro_eur) AS e26_55,
        SUM(reddito_complessivo_da_55000_a_75000_euro_eur) AS e55_75,
        SUM(reddito_complessivo_da_75000_a_120000_euro_eur) AS e75_120,
        SUM(reddito_complessivo_oltre_120000_euro_eur) AS e120,
        SUM(reddito_complessivo_minore_o_uguale_a_zero_euro_freq) AS f_le0,
        SUM(reddito_complessivo_da_0_a_10000_euro_freq) AS f0_10,
        SUM(reddito_complessivo_da_10000_a_15000_euro_freq) AS f10_15,
        SUM(reddito_complessivo_da_15000_a_26000_euro_freq) AS f15_26,
        SUM(reddito_complessivo_da_26000_a_55000_euro_freq) AS f26_55,
        SUM(reddito_complessivo_da_55000_a_75000_euro_freq) AS f55_75,
        SUM(reddito_complessivo_da_75000_a_120000_euro_freq) AS f75_120,
        SUM(reddito_complessivo_oltre_120000_euro_freq) AS f120
    FROM ({cte_irpef})
    WHERE anno_di_imposta BETWEEN 2015 AND 2023
    GROUP BY anno_di_imposta
),
irpef AS (
    SELECT
        *,
        e_le0 + e0_10 + e10_15 + e15_26 + e26_55 + e55_75 + e75_120 + e120 AS totale_eur,
        f_le0 + f0_10 + f10_15 + f15_26 + f26_55 + f55_75 + f75_120 + f120 AS totale_freq
    FROM irpef_raw
)
SELECT
    o.anno,
    o.cuneo_pct,
    100 - o.cuneo_pct AS netto_su_costo_pct,
    o.imposta_media_pct,
    o.netto_eur,
    (i.e55_75 + i.e75_120 + i.e120) / NULLIF(i.totale_eur, 0) * 100 AS pct_reddito_oltre55,
    (i.f55_75 + i.f75_120 + i.f120) / NULLIF(i.totale_freq, 0) * 100 AS pct_contribuenti_oltre55,
    i.e120 / NULLIF(i.totale_eur, 0) * 100 AS pct_reddito_oltre120,
    i.f120 / NULLIF(i.totale_freq, 0) * 100 AS pct_contribuenti_oltre120
FROM oecd o
JOIN irpef i ON o.anno = i.anno
ORDER BY o.anno
