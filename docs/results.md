# Results

Every measured run of the eval harness gets a row here. Only numbers that were actually measured go in this file. Later rows add embedding retrieval, the agentic version, answer scores, cost and latency.

## Retrieval

Run with `python -m src.evals.run_retrieval <retriever>` (`bm25`, `vector`, `vector-sections` or `hybrid`). Recall@k is the fraction of each question's expected event documents found in the top k results, averaged over questions. Questions with no expected documents (`no known cause`) are not included.

| Date | Retriever | Corpus | Questions | recall@1 | recall@3 | recall@5 | 1-source recall@5 | 2-source recall@5 |
|---|---|---|---|---|---|---|---|---|
| 2026-10-25 | BM25 (k1=1.5, b=0.75), whole documents (title + body) | 26 event docs | 17 (10 one-source, 7 two-source) | 0.74 | 0.82 | 0.85 | 1.00 | 0.64 |
| 2026-10-27 | Vector: Voyage `voyage-4`, 1024 dims, cosine distance in pgvector, whole documents (`whole_doc`) | 26 event docs | 17 (10 one-source, 7 two-source) | 0.68 | 0.82 | 0.88 | 1.00 | 0.71 |
| 2026-10-27 | Hybrid: BM25 + vector (`whole_doc`) fused with Reciprocal Rank Fusion (k=60, top 20 from each) | 26 event docs | 17 (10 one-source, 7 two-source) | 0.74 | 0.85 | 0.94 | 1.00 | 0.86 |

## Notes

### 2026-10-25: BM25 baseline

- Keyword search found the single right document for every one-source question.
- Every miss is the **set release document** of a two-source question: Paradox Rift (Q-005, Q-019) and Scarlet & Violet (Q-006, Q-008, Q-009). The question names one card (e.g. Energy Switch) while the release document names another (Roaring Moon ex), so they share no rare words. Linking them needs a step in between ("Energy Switch is played in Roaring Moon ex decks"), which is what the agentic version should add.
- Caveats: 17 questions is small (one question moves overall recall@5 by about 3 points, and two-source recall@5 by about 7), and the event documents were written with the questions in mind, so they name the relevant cards. Real-world documents would likely make keyword search score lower.

### 2026-10-27: vector retrieval, whole documents

- Overall roughly a tie with BM25: recall@5 0.88 vs 0.85 is one question (Q-009). recall@1 is lower (0.68 vs 0.74): BM25 puts the right document first more often, because exact card names are a strong signal.
- The two retrievers miss **different** documents. For Q-005 and Q-019, BM25 misses the Paradox Rift release (it doesn't name the card) while vector search finds it but misses LAIC 2023 (the card is one word among ~200). This suggests combining them (hybrid search, e.g. Reciprocal Rank Fusion) as the next experiment.
- Both miss the Scarlet & Violet release for Q-006 and Q-008: linking the card to the release needs an in-between step (the deck that plays it), which retrieval alone doesn't do. This is the gap the agentic version should close.
- A one-off check (Q-002, Avery) showed low, bunched similarities (0.26-0.29) with set releases from the same month ranked above the right tournament document: the question is about a price move, which no document discusses, so the model falls back on "something happened in November 2023".
- Each run makes one Voyage request (all 17 questions embedded together). Without a payment method on the account, Voyage limits requests to 3 per minute.

### 2026-10-27: hybrid search (Reciprocal Rank Fusion)

- Best so far: recall@5 0.94 (BM25 0.85), two-source recall@5 0.86 (BM25 0.64), and recall@1 back to BM25's 0.74.
- Fixed exactly the questions where the two retrievers each found one document: Q-005 and Q-019 now return both LAIC 2023 and the Paradox Rift release. Q-009 stays fixed. With 17 questions this is promising rather than proven, but each gain has a clear cause.
- Still missed: Q-006 and Q-008 (Scarlet & Violet release). These need a multi-hop link (card, then the deck that plays it, then the set that released that deck's main card), which retrieval from the question alone can't make. Left for the agentic version.
- Hybrid is the retriever carried forward into answer generation.
