-- Chi cattura la crescita — settori
-- Dataset: istat_sbs_imprese, istat_asia_imprese_addetti, inps_retribuzioni
-- Anni: 2014-2023
--
-- Il consumer definisce le CTE {cte_sbs}, {cte_asia}, {cte_inps}.

WITH sbs AS (
    SELECT
        anno,
        nace_codice AS settore_codice,
        MAX(nace) AS settore_nace,
        SUM(valore) / 1000.0 AS va_mln
    FROM ({cte_sbs})
    WHERE grain = 'nazionale'
      AND indicatore = 'Valore aggiunto al costo fattore'
      AND anno BETWEEN 2014 AND 2023
      AND nace_codice <> '0010'
    GROUP BY anno, nace_codice
),
asia AS (
    SELECT
        anno,
        nace_codice AS settore_codice,
        SUM(valore) AS addetti
    FROM ({cte_asia})
    WHERE livello = 'italia'
      AND indicatore = 'Addetti media annua'
      AND anno BETWEEN 2014 AND 2023
      AND nace_codice <> '0010'
    GROUP BY anno, nace_codice
),
inps AS (
    SELECT
        anno,
        settore_codice,
        SUM(n_lavoratori) AS n_lavoratori,
        SUM(retribuzione_totale) AS retribuzione_totale,
        SUM(settimane_retribuite) AS settimane_retribuite
    FROM ({cte_inps})
    WHERE dimensione = 'anno_settore'
      AND settore_codice IS NOT NULL
    GROUP BY anno, settore_codice
)
SELECT
    s.anno,
    s.settore_codice,
    s.settore_nace,
    s.va_mln,
    a.addetti,
    s.va_mln * 1000000.0 / NULLIF(a.addetti, 0) AS va_per_addetto,
    i.n_lavoratori,
    i.retribuzione_totale,
    i.retribuzione_totale / NULLIF(i.n_lavoratori, 0) AS retribuzione_media,
    i.retribuzione_totale / NULLIF(i.settimane_retribuite, 0) AS retribuzione_media_settimana
FROM sbs s
JOIN asia a
    ON s.anno = a.anno
   AND s.settore_codice = a.settore_codice
JOIN inps i
    ON s.anno = i.anno
   AND s.settore_codice = i.settore_codice
ORDER BY s.anno, s.settore_codice
