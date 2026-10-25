# Data notes

Notes from inspecting each price source. Fill in as checked.

## tcgapi.dev (free tier)

Checked on: 2026-10-25 (from the website only; no API key yet, no requests made)

### Date range
History starts March 2025. Nothing earlier exists, so it cannot cover the 2023-2024 eval window.

### Granularity
Daily, according to the sample response. The FAQ also mentions weekly points, so confirm with a real request.

### Card coverage
Cards with a market price of $1 or more get history.

### Format
JSON over HTTP, e.g. `GET /v1/cards/{id}/history`.

### Limits / licence
- Free tier: 100 requests/day, non-commercial use only.
- Free tier only returns 7 days of history. Hobby gets 30 days, Starter 90, Pro ($49.99/month) full history.

### Open questions
- Probably not needed: the TCGdex API (below) gives current prices for free with no key.

## tcgdex/price-history

Checked on: 2026-10-25. Shallow clone at `C:/data/tcgdex-price-history` (outside OneDrive, about 336 MB, about 15,000 files). Path is set as `PRICE_HISTORY_DIR` in `.env`.

### Date range
- 2022-11-12 to 2024-09-24.
- **No data at all from December 2023 to April 2024**, for every card.
- Usable windows: **Nov 2022 - Nov 2023** and **May - Sep 2024**.
- Repo last updated June 2025, but the newest price is from September 2024.

### Granularity
- Daily, with avg, min, max and a count (probably number of sales) per day.
- Days with no sales are missing, so thinly traded cards have big gaps.
- One-day jumps on low sale counts are common, e.g. Origin Forme Dialga V on 2023-08-21: $6.05 on 4 sales, against about $1.75 either side.

### Card coverage
- English data from TCGplayer only (`en/<set>/<number>.tcgplayer.json`).
- Sets from Base Set to Paradox Rift (`sv04`). Missing: Paldean Fates, Scarlet & Violet promos, Prize Pack cards.
- **In 10 sets (`swsh9` to `sv04`), only cards numbered 100 and up have files.** Likely a zero-padding bug (`001` vs `1`), unconfirmed. Older sets are complete.
- 18 files don't match a TCGdex card ID (e-Card holos such as `ecard2-H1`). The loader skips them.

### Format
- One JSON file per card. Under `data`, one series per `<variant>-<condition>` key, e.g. `holo-nearmint`.
- Variants: `normal`, `reverse`, `holo`. Conditions: `nearmint`, `good`, `played`, `used`, `poor`.
- **Before May 2024 every series is `good`.** The other conditions only start in May 2024, so `good` may be a catch-all before that. How these map to TCGplayer's grades (NM, LP, MP, HP, Damaged) is unknown.
- Prices look like US cents (817 = $8.17), based on matching TCGplayer's published figures. Not confirmed by the source.
- Each series also has avg, avg7 and avg28 summary fields. Not loaded, because they can be calculated from the daily rows.
- File path matches the TCGdex card ID: `en/swsh10/113` = `swsh10-113`.
- Loaded into the `prices` table as source `tcgdex-tcgplayer`: 2,218,942 rows.

### Limits / licence
- README says MIT and links a LICENSE file, but that file is not in the repo.
- Maintainers replied that the data can be used and that I should copy the licence; they will send a copy. Keep their message.
- Until the licence text arrives: use locally only, do not publish raw data or price charts built from it.
- The prices originally come from TCGplayer, which has its own terms. Check them before publishing anything derived.

### Open questions
- Is `good` before May 2024 a mix of all conditions?
- Is the count field the number of sales?
- Will the cards numbered below 100 ever be added for `swsh9` to `sv04`?

## TCGdex API (api.tcgdex.net)

Checked on: 2026-10-25

### What it gives
- Card catalogue: card ID, name, set and number for every card. Set endpoint `/v2/en/sets/{id}` returns the whole card list in one request. Rarity is only on the single-card endpoint.
- Current Cardmarket prices (EUR) on each card: avg, low, trend, plus 1, 7 and 30-day averages. TCGplayer prices were empty for the card checked.
- No API key needed. Rate limits not checked.

### How it's used
- `src/ingest/load_cards.py` loads the catalogue into the `cards` table: 16,329 cards across all 137 sets in the price history.
- Candidate for recording current prices daily from now on.

### Licence
- The card database repo (tcgdex/cards-database) is MIT.
- Prices come from Cardmarket, which has its own terms. Check before publishing.
