WITH weekly AS (
    SELECT card_id, variant,
           date_trunc('week', day)::date AS week,
           round(percentile_cont(0.5) WITHIN GROUP (ORDER BY avg_cents)) AS median_cents,
           sum(sale_count) AS sales
    FROM prices
    WHERE condition = 'good'
    GROUP BY card_id, variant, week
),
compared AS (
    SELECT card_id, variant, week, median_cents, sales,
           avg(median_cents) OVER w_before AS before_cents,
           count(*)          OVER w_before AS weeks_before,
           sum(sales)        OVER w_before AS sales_before,
           min(median_cents) OVER w_after  AS after_cents,
           count(*)          OVER w_after  AS weeks_after,
           sum(sales)        OVER w_after  AS sales_after
    FROM weekly
    WINDOW
        w_before AS (PARTITION BY card_id, variant ORDER BY week
                     RANGE BETWEEN INTERVAL '28 days' PRECEDING AND INTERVAL '7 days' PRECEDING),
        w_after  AS (PARTITION BY card_id, variant ORDER BY week
                     RANGE BETWEEN CURRENT ROW AND INTERVAL '7 days' FOLLOWING)
),
spikes AS (
    SELECT *, after_cents / before_cents AS ratio
    FROM compared
    WHERE weeks_before >= 3            -- baseline built from at least 3 of the 4 weeks
      AND weeks_after = 2              -- both this week and next week have sales
      AND sales_before >= 10           -- enough sales to trust the baseline
      AND sales_after >= 10            -- enough sales to trust the jump
      AND before_cents >= 200          -- ignore cards under $2
      AND after_cents >= 1.5 * before_cents   -- at least doubled, and stayed doubled
),
best_per_card AS (
    SELECT DISTINCT ON (card_id, variant) *
    FROM spikes
    ORDER BY card_id, variant, ratio DESC
)
SELECT b.card_id, c.name, c.set_name, b.variant, b.week,
       round(b.before_cents) AS before_cents, b.after_cents,
       round(b.ratio::numeric, 1) AS ratio, b.sales_after
FROM best_per_card b
JOIN cards c ON c.id = b.card_id
ORDER BY b.ratio DESC
LIMIT 30;