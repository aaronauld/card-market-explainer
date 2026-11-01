# card-market-explainer

Pokémon card prices sometimes jump or crash, and the reason is usually scattered across set announcements, reprint news, tournament results, and rotation or ban notices. This project answers questions like "why did Card X jump in March?" by looking up the card's price history, finding documents about what happened around those dates, and giving an answer that cites its sources. It explains past price moves; it does not predict prices or recommend purchases.

## Results

Measured on 28 labelled price moves and 62 event documents, using Claude Opus 5.5 at medium effort. Answer figures are the mean of 2 runs. Full notes are in [docs/results.md](docs/results.md).

| | Plain RAG | Agent |
|---|---|---|
| Fact recall | 0.87 | 1.00 |
| Fact recall, two-source questions | 0.71 | 1.00 |
| Citation recall | 0.74 | 1.00 |
| Invented or unseen citations | 0 | 0 |
| Seconds per answer | 7.1 | 10.7 |
| Cost per answer | $0.025 | $0.050 |

**What this shows**

- One-source questions tie at 1.00 on facts, and almost all of the gap is on two-source questions. When one document is enough, plain RAG is the cheaper choice.
- Plain RAG's misses come mostly from retrieval. Same-month documents crowd out the second source, and it then says the documents don't explain the move instead of inventing a cause. The agent recovers the missing document with a second, targeted search.
- With only 26 documents the two pipelines were nearly tied, so the gap depends on the corpus.
- Prompt caching cut the agent's cost by about 23%. Claude accounts for over 90% of its latency.
- A score-based signal for retrying weak searches didn't work: no retrieval score reliably predicted a missed document.

| Retrieval (23 questions with expected documents) | recall@1 | recall@5 | two-source recall@5 |
|---|---|---|---|
| BM25 | 0.57 | 0.78 | 0.58 |
| Hybrid (BM25 + vector) | 0.48 | 0.74 | 0.50 |

**Limits:** 28 questions is small, as one question moves fact recall by about 3.6 points. The documents and distractors were written for this eval, so the size of the gap is specific to this corpus. Fact recall is judged by Claude.

## How it works

- **Hand-written, no LangChain or similar framework:** BM25, Voyage embeddings in pgvector, Reciprocal Rank Fusion, citations, and an agent loop in which Claude chooses when to look up prices and search documents.
- **Eval harness:** recall@k for retrieval, plus fact recall and citation checks for answers, with latency and cost. Each answer saves a trace of its timed steps.
- **Service:** FastAPI and Postgres with pgvector in Docker Compose, with an API key and a daily spending limit.
- **Deployment:** private, on one AWS EC2 server reached through an SSH tunnel. See [docs/deployment.md](docs/deployment.md).
- **CI:** fails if BM25 retrieval scores fall below the saved baseline. Answer evals cost money and vary between runs, so they run by hand.

## Data

Card catalogue from the [TCGdex](https://tcgdex.dev) API. Daily TCGplayer prices (Nov 2022 to Sep 2024, with a gap from Dec 2023 to Apr 2024) from [tcgdex/price-history](https://github.com/tcgdex/price-history). Price data is only used privately until its licence text is confirmed, so there is no public demo. See [docs/data-notes.md](docs/data-notes.md).
