# card-market-explainer

Pokémon card prices sometimes jump or crash, and the reason is usually scattered across set announcements, reprint news, tournament results, and rotation or ban notices. This project answers questions like "why did Card X jump in March?" by looking up the card's price history, finding documents about what happened around those dates, and giving an answer that cites its sources. It explains past price moves; it does not predict prices or recommend purchases.

## Planned stack

- **Python and FastAPI** for the service
- **Postgres with pgvector**, run locally with Docker Compose, so document metadata, prices and embeddings live in one database and can be filtered and searched in a single query
- **Hand-written retrieval (RAG) first**, without LangChain or similar frameworks, then an agentic version that chooses between price lookup and document search. Both are compared on the same eval set, including cost and latency.
- **A thin React UI**

## Status

Setup in progress: local Postgres with pgvector via Docker Compose, plus project docs and an eval question template. No retrieval or model code yet.
