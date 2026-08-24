-- Previsione vs Consuntivo per Missione di spesa
-- Datasets: bdap_spese_stato (previsione), bdap_pagamenti_stato (consuntivo)
-- Join key: missione (normalizzata lowercase) + anno
-- Period: 2014–2024 (overlap dei due dataset)
--
-- Il consumer define le CTE {cte_spese} e {cte_pagamenti} prima di questo blocco.

WITH previsione AS (
    SELECT
        esercizio_finanziario AS anno,
        LOWER(missione) AS missione,
        SUM(previsioni_definitive_cp) AS previsto
    FROM ({cte_spese})
    GROUP BY 1, 2
),
consuntivo AS (
    SELECT
        esercizio_finanziario AS anno,
        LOWER(missione) AS missione,
        SUM(totale_pagato) AS pagato
    FROM ({cte_pagamenti})
    GROUP BY 1, 2
)
SELECT
    p.anno,
    p.missione,
    p.previsto,
    c.pagato,
    CASE WHEN p.previsto > 0 THEN c.pagato / p.previsto ELSE NULL END AS tasso_esecuzione
FROM previsione p
LEFT JOIN consuntivo c
    ON p.anno = c.anno AND p.missione = c.missione
WHERE p.anno >= 2014
ORDER BY p.anno DESC, p.previsto DESC
