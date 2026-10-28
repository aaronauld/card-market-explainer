"""Price lookups behind one small interface, so the data source can be swapped later."""
from src.ingest.common import connect, read_env
from datetime import timedelta
from statistics import median

SOURCE = "tcgdex-tcgplayer"


def get_prices(card_ids, start, end, condition="good"):
    """Daily prices for the given cards between two dates (inclusive).
    Returns {card_id: [(day, variant, avg_cents, sale_count), ...]}, oldest first."""
    result = {card_id: [] for card_id in card_ids}
    with connect(read_env()) as conn:
        rows = conn.execute(
            "SELECT card_id, day, variant, avg_cents, sale_count FROM prices "
            "WHERE card_id = ANY(%s) AND day BETWEEN %s AND %s "
            "AND condition = %s AND source = %s "
            "ORDER BY card_id, day, variant",
            (list(card_ids), start, end, condition, SOURCE),
        ).fetchall()
    for card_id, day, variant, avg_cents, sale_count in rows:
        result[card_id].append((day, variant, avg_cents, sale_count))
    return result


def weekly_summary(rows, variant):
    """Turn daily rows into one line per week: median price and total sales."""
    weeks = {}
    for day, row_variant, avg_cents, sale_count in rows:
        if row_variant != variant:
            continue
        monday = day - timedelta(days=day.weekday())
        weeks.setdefault(monday, []).append((avg_cents, sale_count or 0))

    if not weeks:
        return "No price data for this card in this period."

    lines = []
    for monday in sorted(weeks):
        prices = [price for price, _ in weeks[monday]]
        sales = sum(count for _, count in weeks[monday])
        lines.append(
            f"Week of {monday}: median ${median(prices) / 100:.2f} ({sales} sales)")
    return "\n".join(lines)


def price_context(card_id, variant, around, weeks_before=6, weeks_after=4, condition="good"):
    """Weekly price summary for one card around a date, ready to put in a prompt."""
    start = around - timedelta(weeks=weeks_before)
    end = around + timedelta(weeks=weeks_after)
    rows = get_prices([card_id], start, end, condition)[card_id]
    return weekly_summary(rows, variant)
