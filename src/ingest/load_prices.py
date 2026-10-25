from datetime import date
from pathlib import Path
import json

from common import connect, read_env


SOURCE = "tcgdex-tcqplayer"


def rows_for_file(card_id, path):
    data = json.loads(path.read_text(encoding="utf-8"))["data"]
    rows = []
    for key, series in data.items():
        variant, condition = key.rsplit("-", 1)
        for day, price in series["history"].items():
            rows.append((
                card_id, SOURCE, variant, condition, date.fromisoformat(day),
                price["avg"], price.get("min"), price.get(
                    "max"), price.get("count"),
            ))
    return rows


def main():
    env = read_env()
    price_dir = Path(env["PRICE_HISTORY_DIR"]) / "en"

    with connect(env) as conn:
        known_ids = {row[0] for row in conn.execute("SELECT id FROM cards")}
        skipped = 0

        for set_dir in sorted(p for p in price_dir.iterdir() if p.is_dir()):
            set_rows = []
            for path in sorted(set_dir.glob("*.tcgplayer.json")):
                number = path.name.removesuffix(".tcgplayer.json")
                card_id = f"{set_dir.name}-{number}"
                if card_id not in known_ids:
                    skipped += 1
                    continue
                set_rows.extend(rows_for_file(card_id, path))

            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO prices (card_id, source, variant, condition, day, "
                    "avg_cents, min_cents, max_cents, sale_count) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT DO NOTHING",
                    set_rows,
                )
            conn.commit()
            print(f"{set_dir.name}: {len(set_rows)} rows")

        print(f"Skipped {skipped} files with no matching card")


if __name__ == "__main__":
    main()
