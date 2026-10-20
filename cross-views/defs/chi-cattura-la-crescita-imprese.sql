-- Chi cattura la crescita — imprese e redditi dichiarati
-- Dataset: ires_redditi_regione, irpef_comunale, iva_sez_attivita
-- Anni: 2015-2024 (IRES/IRPEF), 2014-2023 (IVA)
--
-- Il consumer definisce le CTE {cte_ires}, {cte_irpef}, {cte_iva}.

WITH ires AS (
    SELECT
        anno,
        SUM(reddito_totale_eur) - SUM(perdita_totale_eur) AS ires_netto,
        SUM(n_dichiarazioni) AS dichiarazioni
    FROM ({cte_ires})
    WHERE anno BETWEEN 2015 AND 2024
    GROUP BY anno
),
irpef AS (
    SELECT
        anno_di_imposta AS anno,
        SUM(reddito_da_lavoro_dipendente_e_assimilati_eur) AS irpef_lavoro_dipendente,
        SUM(numero_contribuenti) AS contribuenti
    FROM ({cte_irpef})
    WHERE anno_di_imposta BETWEEN 2015 AND 2024
    GROUP BY anno_di_imposta
),
iva AS (
    SELECT
        anno,
        SUM(volume_affari_eur) AS fatturato,
        SUM(va_fiscale_eur) AS va_fiscale,
        SUM(acquisti_eur) AS acquisti
    FROM ({cte_iva})
    WHERE anno BETWEEN 2014 AND 2023
    GROUP BY anno
)
SELECT
    i.anno,
    i.ires_netto,
    p.irpef_lavoro_dipendente,
    i.dichiarazioni,
    p.contribuenti,
    v.fatturato,
    v.va_fiscale,
    v.acquisti,
    v.va_fiscale / NULLIF(v.fatturato, 0) * 100 AS margine_va_pct
FROM ires i
JOIN irpef p ON i.anno = p.anno
LEFT JOIN iva v ON i.anno = v.anno
ORDER BY i.anno
