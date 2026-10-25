# Results

Every measured run of the eval harness gets a row here. Only numbers that were actually measured go in this file. Later rows add embedding retrieval, the agentic version, answer scores, cost and latency.

## Retrieval

Run with `python -m src.evals.run_retrieval`. Recall@k is the fraction of each question's expected event documents found in the top k results, averaged over questions. Questions with no expected documents (`no known cause`) are not included.

| Date | Retriever | Corpus | Questions | recall@1 | recall@3 | recall@5 | 1-source recall@5 | 2-source recall@5 |
|---|---|---|---|---|---|---|---|---|
| 2026-10-25 | BM25 (k1=1.5, b=0.75), whole documents (title + body) | 26 event docs | 17 (10 one-source, 7 two-source) | 0.74 | 0.82 | 0.85 | 1.00 | 0.64 |

## Notes

### 2026-10-25: BM25 baseline

- Keyword search found the single right document for every one-source question.
- Every miss is the **set release document** of a two-source question: Paradox Rift (Q-005, Q-019) and Scarlet & Violet (Q-006, Q-008, Q-009). The question names one card (e.g. Energy Switch) while the release document names another (Roaring Moon ex), so they share no rare words. Linking them needs a step in between ("Energy Switch is played in Roaring Moon ex decks"), which is what the agentic version should add.
- Caveats: 17 questions is small (one question moves recall@5 by about 6 points), and the event documents were written with the questions in mind, so they name the relevant cards. Real-world documents would likely make keyword search score lower.
