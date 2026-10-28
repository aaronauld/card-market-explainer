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

## Answers

Run with `python -m src.evals.run_answers <retriever>`. Each question goes through the full pipeline: retrieve the top 5 documents, add a weekly price summary, ask Claude for an explanation that cites documents by id. Then:

- **Fact recall**: share of the question's **Answer must mention** facts the answer states, judged by Claude (`claude-opus-5-5`, effort `low`) with a reason for every verdict.
- **Citation recall**: share of the expected event documents the answer cites (questions with expected documents only).
- **Bad citations**: citations of documents that don't exist or weren't in the prompt.
- **Latency**: time per answer (retrieval + prices + Claude), excluding the judge. **Cost**: answer calls only, at $4 / $20 per million input / output tokens.

| Date | Retriever | Model (effort) | Questions | Fact recall | 1-source | 2-source | No known cause | Citation recall | Bad citations | Seconds per answer | Cost per answer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-28 | Hybrid (BM25 + vector, RRF) | `claude-opus-5-5` (medium) | 19 | 0.95 | 0.95 | 0.93 | 1.00 (2) | 0.91 | 0 | 7.5 | $0.024 |
| 2026-10-29 | Hybrid (BM25 + vector, RRF), mean of 2 runs | `claude-opus-5-5` (medium) | 19 | 0.99 (0.97-1.00) | 1.00 | 1.00 | 0.88 (2) | 0.94 | 0 | 7.4 | $0.024 |

### 2026-10-28: first plain-RAG answer runs

- The first run (fact recall 0.89) was mostly scoring the answer key, not the system: five **Answer must mention** facts needed knowledge the documents don't contain (e.g. "it was a widely played staple"). They were rewritten, and the eval now has a rule that every fact must be derivable from the prices and documents. The row above is the second run, against the fixed key.
- One genuine failure: Q-004 (Dark Patch, Lost Origin). LAIC 2023 was retrieved first and says every Roaring Moon ex list played 4 Dark Patch, but the answer claimed no document connects Dark Patch to a deck. A generation error, not a retrieval error. The same question passed in the first run.
- One judge-strictness miss: Q-017 failed only for not saying the win was in the "Masters" division. "Masters" was then dropped from the Q-001, Q-016 and Q-017 facts; the row above predates that change.
- Two-source fact recall is flattering. Q-006 and Q-008 never retrieve the Scarlet & Violet release document (citation recall 0.5), but other documents mention the 31 March 2023 release in passing, so the facts can still be stated. Citation recall is the more honest measure of whether the intended evidence was found.
- Both no-cause questions (Q-015, Q-018) said plainly that nothing explains the move and cited nothing that claims a cause.
- No invented or unseen citations in either run.
- Answers vary between runs (Q-004 and Q-006 flipped). With 19 questions, treat differences of about 5 points or less between single runs as noise; average several runs before comparing versions.
- Saved answers and judge reasons for each run are written to `data/runs/` (git-ignored: generated output that includes figures derived from the price data).

### 2026-10-29: repeat runs (current answer key)

- Two runs against the current answer key (after the "Masters" change), compared with `python -m src.evals.compare_runs "data/runs/answers-hybrid-2026-10-29-*.json"`: fact recall 1.00 and 0.97 (mean 0.99), citation recall 0.94 in both.
- The only question that changed was Q-018 (no known cause): in one run the judge failed "no document mentions Yveltal or a deck using it" because the answer said the other documents "don't involve Yveltal" without stating it outright. The answer was correct in substance. The fact was left unchanged: it is derivable from the documents, so changing it would tune the key to the system.
- Q-004's generation error from the first run did not repeat.
- Citation recall misses are systematic, not random: Q-006 and Q-008 never retrieve the Scarlet & Violet release document.
- Plain RAG is close to this eval's ceiling on fact recall, so the agentic version can only show a difference on citation recall (Q-006, Q-008), cost and latency, or on harder questions. Adding harder, more multi-hop questions is the next step before phase 2.

## Baseline on 21 questions (2026-10-29)

Two questions were added: Q-020 (Dark Patch after Worlds 2024, two sources) and Q-021 (Earthen Vessel, a false premise: it didn't spike). This is the plain-RAG baseline the agentic version will be compared with.

| Date | Pipeline | Questions | recall@1 | recall@3 | recall@5 | 1-source recall@5 | 2-source recall@5 |
|---|---|---|---|---|---|---|---|
| 2026-10-29 | Hybrid retrieval | 18 with expected docs (10 one-source, 8 two-source) | 0.69 | 0.83 | 0.94 | 1.00 | 0.88 |

| Date | Pipeline | Questions | Fact recall | Citation recall | Bad citations | Seconds per answer | Cost per answer |
|---|---|---|---|---|---|---|---|
| 2026-10-29 | Hybrid + `claude-opus-5-5` (medium), mean of 2 runs | 21 | 0.98 (0.96-1.00) | 0.94 | 0 | 7.1 | $0.024 |

- Q-020 was answered correctly in both runs: hybrid retrieval returned both the Worlds 2024 and LAIC 2023 documents, and the answer linked them ("every published Roaring Moon ex list ran 4 Dark Patch"). Because LAIC names both Dark Patch and Roaring Moon ex, one search finds both, so it is less of a multi-hop test than intended.
- Q-021 (false premise) was handled in both runs: the answer said the rise started before Worlds and was gradual, quoting the weekly prices.
- Misses in the second run: Q-018 (the same judge strictness as before, left unchanged) and Q-009 ("the spike was brief"). The Q-009 spike lasted three days in the daily data, but the system sees weekly medians, where it looks like a peak week followed by easing, so the fact wasn't derivable. It was reworded to "the price peaked around the release and eased in the following weeks" after these runs.
- The only systematic gap is still Q-006 and Q-008 (Scarlet & Violet release never retrieved). Plain RAG is near this eval's ceiling on facts, so the comparison with the agentic version will mostly be about those two questions, cost and latency.
