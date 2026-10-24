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
- Prices: tcgapi.dev free tier (100 requests/day, non-commercial). History may be backfilled from tcgdex/price-history; check date range, granularity and card coverage first. Keep the source behind a small interface (`get_prices(card_ids)`) so it can be swapped.
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
