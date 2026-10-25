import json
import time
import psycopg
import urllib.error
import urllib.request

from pathlib import Path
from common import read_env, connect

API = "https://api.tcgdex.net/v2/en"


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def main():
    env = read_env()
    price_dir = Path(env["PRICE_HISTORY_DIR"]) / "en"
    set_ids = sorted(p.name for p in price_dir.iterdir() if p.is_dir())

    with connect(env) as conn:
        for set_id in set_ids:
            try:
                data = fetch_json(f"{API}/sets/{set_id}")
            except urllib.error.HTTPError as err:
                print(f"{set_id}: skipped ({err.code})")
                continue

            rows = [
                (card["id"], card["name"], set_id,
                 data["name"], card["localId"])
                for card in data["cards"]
            ]

            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO cards (id, name, set_id, set_name, local_id) "
                    "VALUES (%s, %s, %s, %s, %s) "
                    "ON CONFLICT (id) DO NOTHING",
                    rows,
                )

            conn.commit()
            print(f"{set_id}: {len(rows)} cards")
            time.sleep(0.2)


if __name__ == "__main__":
    main()
