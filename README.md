# card-market-explainer

Pokémon card prices sometimes jump or crash, and the reason is usually scattered across set announcements, reprint news, tournament results, and rotation or ban notices. This project answers questions like "why did Card X jump in March?" by looking up the card's price history, finding documents about what happened around those dates, and giving an answer that cites its sources. It explains past price moves; it does not predict prices or recommend purchases.

## Planned stack

- **Python and FastAPI** for the service
- **Postgres with pgvector**, run locally with Docker Compose, so document metadata, prices and embeddings live in one database and can be filtered and searched in a single query
- **Hand-written retrieval (RAG) first**, without LangChain or similar frameworks, then an agentic version that chooses between price lookup and document search. Both are compared on the same eval set, including cost and latency.
- **A thin React UI**

## Status

Phase 1 (plain RAG) is working end to end: retrieval, price lookup, answers with citations from Claude, and automatic scoring. Phase 2 (agentic version) has started: a hand-written tool-use loop in which Claude chooses when to look up prices and search documents. It is scored with the same harness.

- Local Postgres with pgvector via Docker Compose.
- Card catalogue (16,329 cards) loaded from the [TCGdex](https://tcgdex.dev) API.
- Daily TCGplayer price history (about 2.2 million rows, Nov 2022 to Sep 2024, with a gap from Dec 2023 to Apr 2024) loaded locally from [tcgdex/price-history](https://github.com/tcgdex/price-history). See [docs/data-notes.md](docs/data-notes.md) for coverage gaps and licensing.
- Eval set: 21 labelled price moves in [docs/eval-questions.md](docs/eval-questions.md), and 26 event documents in `data/events/` (9 the questions need, 17 distractors).
- Hand-written retrievers measured with the same recall@k harness: BM25 keyword search (recall@5 0.85), Voyage embeddings in pgvector (0.88) and a hybrid of both with Reciprocal Rank Fusion (0.94). See [docs/results.md](docs/results.md).
- Answers: hybrid retrieval plus a weekly price summary, explained by Claude Opus 5.5 with citations to event documents. On the 21 questions (mean of 2 runs): fact recall 0.98, citation recall 0.94, no invented citations, about 7.1 s and $0.024 per answer.
- Agent: on the same 21 questions (mean of 2 runs): fact recall 1.00, citation recall 0.96, no invented citations, 2.6 tool calls, about 10.8 s and $0.050 per answer. It made a multi-hop link plain RAG misses on one question (Q-008), but not on another (Q-006). After adding a general rule to cite the primary document for each event: citation recall 1.00 on both runs, 2.86 tool calls, about 11.0 s and $0.057 per answer.
