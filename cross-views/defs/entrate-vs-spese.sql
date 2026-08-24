-- Entrate vs Spese dello Stato — il bilancio aggregato
-- Datasets: bdap_entrate_stato, bdap_spese_stato
-- Join key: anno (aggregazione macro)
-- Period: 2008–2024
--
-- Il consumer define le CTE {cte_entrate} e {cte_spese} prima di questo blocco.

WITH entrate AS (
    SELECT
        esercizio_finanziario AS anno,
        SUM(previsioni_definitive_cp) AS totale_entrate
    FROM ({cte_entrate})
    GROUP BY 1
),
spese AS (
    SELECT
        esercizio_finanziario AS anno,
        SUM(previsioni_definitive_cp) AS totale_spese
    FROM ({cte_spese})
    GROUP BY 1
)
SELECT
    e.anno,
    e.totale_entrate,
    s.totale_spese,
    e.totale_entrate - s.totale_spese AS saldo,
    CASE WHEN e.totale_entrate > 0 THEN s.totale_spese / e.totale_entrate ELSE NULL END AS rapporto_spese_entrate
FROM entrate e
JOIN spese s ON e.anno = s.anno
ORDER BY e.anno
