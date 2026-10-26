# card-market-explainer

Pokémon card prices sometimes jump or crash, and the reason is usually scattered across set announcements, reprint news, tournament results, and rotation or ban notices. This project answers questions like "why did Card X jump in March?" by looking up the card's price history, finding documents about what happened around those dates, and giving an answer that cites its sources. It explains past price moves; it does not predict prices or recommend purchases.

## Planned stack

- **Python and FastAPI** for the service
- **Postgres with pgvector**, run locally with Docker Compose, so document metadata, prices and embeddings live in one database and can be filtered and searched in a single query
- **Hand-written retrieval (RAG) first**, without LangChain or similar frameworks, then an agentic version that chooses between price lookup and document search. Both are compared on the same eval set, including cost and latency.
- **A thin React UI**

## Status

Phase 1 (plain RAG) in progress. Retrieval is built and measured; answer generation is next.

- Local Postgres with pgvector via Docker Compose.
- Card catalogue (16,329 cards) loaded from the [TCGdex](https://tcgdex.dev) API.
- Daily TCGplayer price history (about 2.2 million rows, Nov 2022 to Sep 2024, with a gap from Dec 2023 to Apr 2024) loaded locally from [tcgdex/price-history](https://github.com/tcgdex/price-history). See [docs/data-notes.md](docs/data-notes.md) for coverage gaps and licensing.
- Eval set: 19 labelled price moves in [docs/eval-questions.md](docs/eval-questions.md), and 26 event documents in `data/events/` (9 the questions need, 17 distractors).
- Two hand-written retrievers measured with the same recall@k harness: BM25 keyword search and Voyage embeddings in pgvector. Both reach recall@5 of about 0.85-0.88 but miss different documents; see [docs/results.md](docs/results.md).
