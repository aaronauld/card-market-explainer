# card-market-explainer

Explains why a Pokémon card's price moved, with cited sources. A learning-focused portfolio project for AI engineering roles. Owner: Aaron.

## What it does
Given a question like "why did Card X jump in March?", the system looks up the card's price history, retrieves documents about what happened around those dates (set announcements, reprints, tournament results, rotation or ban notices), and answers with citations.

It explains past moves. It does not predict prices or recommend purchases.

## Build order (do not skip ahead)
1. Weeks 1-8: plain RAG, written by hand with no LangChain or similar framework. Chunking, embeddings, pgvector retrieval, citations. Build the eval harness first.
2. Weeks 9-16: agentic version. The model chooses between price lookup and document search, and retries weak retrievals. Re-run the same evals and report the difference against plain RAG, including cost and latency.
3. Then: deploy on AWS, add tracing and cost tracking, CI that fails on eval regressions, README with a results table, demo video.

## Stack
Python, FastAPI, Postgres with pgvector (Docker Compose). Thin React UI later.

## Data
- Prices: historical prices come from tcgdex/price-history, cloned outside the repo (`PRICE_HISTORY_DIR` in `.env`) and loaded into the `prices` table. It covers Nov 2022 to Nov 2023 and May to Sep 2024 only; see `docs/data-notes.md` for gaps. Current prices can come from the TCGdex API (free, no key). tcgapi.dev's free tier has only 7 days of history from Mar 2025, so it is not the main source. Keep the source behind a small interface (`get_prices(card_ids)`) so it can be swapped.
- Cards: catalogue loaded from the TCGdex API into the `cards` table. Card IDs are TCGdex IDs, e.g. `swsh10-113`.
- Database: Postgres runs in Docker on host port 5433, because a local Windows Postgres uses 5432. Schema is in `src/ingest/schema.sql`.
- Embeddings: Voyage AI `voyage-4` (1024 dims) over plain HTTP in `src/retrieval/voyage.py`, key `VOYAGE_API_KEY` in `.env`. Chunks and vectors live in the `chunks` table (`strategy` column: `whole_doc` or `by_section`); load with `python -m src.ingest.load_chunks <strategy>`. Without a payment method Voyage allows 3 requests per minute, so batch texts into one request.
- Evals: `python -m src.evals.run_retrieval <bm25|vector|vector-sections|hybrid>`; record every measured run in `docs/results.md`. Hybrid (BM25 + vector with Reciprocal Rank Fusion, `src/retrieval/hybrid.py`) is the current best retriever.
- Events: dated markdown files in `data/events/` with metadata (date, source URL, type, cards or sets mentioned). Sources: official announcements, public tournament results, Bulbapedia (non-commercial licence, credit it).
- Raw price data and `.env` must never be committed. Check data licensing before publishing anything derived from a source.

## Eval design
`docs/eval-questions.md` holds labelled price spikes: card, approximate date, the real cause, and how it is known. At least 40% need two sources. Retrieval is scored by whether the right event documents come back (recall@k); answers by whether they cite the true cause.

## Working rules
- Aaron is learning: explain choices briefly, prefer simple code he can follow, and write core RAG pieces by hand.
- Do not add dependencies or frameworks without saying why.
- Do not claim results that have not been measured.
- Stay inside scope: no price-prediction features, no scraping of sites that forbid it.

## Layout
- `src/ingest/` data collection and loading
- `src/api/` FastAPI service
- `data/events/`, `data/prices/` (prices are git-ignored)
- `docs/` data notes and eval questions
- `scripts/` one-off utilities
