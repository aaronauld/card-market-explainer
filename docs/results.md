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

## Agent vs plain RAG (21 questions)

Run with `python -m src.evals.run_answers agent`. The agent (`src/agent/agent.py`) is a hand-written tool-use loop: Claude chooses when to call `get_price_summary` (the same weekly summary plain RAG gets), `search_documents` (hybrid search, top 5) and `find_cards`, for up to 8 rounds, then answers with citations. Scoring is unchanged. Citation checks count every document the agent saw in any search as "retrieved". Cost covers all of the agent's calls.

| Date | Pipeline | Questions | Fact recall | Citation recall | Bad citations | Tool calls per question | Seconds per answer | Cost per answer |
|---|---|---|---|---|---|---|---|---|
| 2026-10-29 | Plain RAG: hybrid + `claude-opus-5-5` (medium), mean of 2 runs | 21 | 0.98 (0.96-1.00) | 0.94 | 0 | — | 7.1 | $0.024 |
| 2026-10-29 | Agent: `claude-opus-5-5` (medium) with 3 tools, mean of 2 runs | 21 | 1.00 (1.00-1.00) | 0.96 (0.94-0.97) | 0 | 2.6 | 10.8 | $0.050 |

- The agent costs about 2.1× as much and is about 1.5× slower for about 2 points more citation recall, which is within run-to-run noise. Plain RAG was already near this eval's ceiling, so there was little left to gain.
- **Q-008 (Worker) was fixed in both runs.** The agent's second search, "Scarlet & Violet base set release Gardevoir ex", found the release document that plain RAG never retrieves. This is the multi-hop step (card, then the deck that plays it, then the set that released the deck's main card) that retrieval alone can't make.
- **Q-006 (Regieleki VMAX) missed in both runs, the same way.** The agent made one search ("Regieleki VMAX tournament results April 2023"), and a tournament document that mentions the Scarlet & Violet release in passing was enough to explain the move, so it stopped and never fetched the release document. In one earlier single-question test it did search again, so the step happens only sometimes.
- Q-007 scored 0.5 in the first run and 1.0 in the second. Both times it searched once, and the second time that one search happened to return both documents.
- Searches per question across both runs: one search 21 times, two 18 times, three once, four twice. The agent stops when its results feel sufficient, not when it has the primary source for each event.
- Latency includes any waits for Voyage's free-tier rate limit (3 requests per minute) when the agent embeds a new search query.
- Next experiment: add a general rule to the agent's instructions to cite the document mainly about each event, and to search for it if it hasn't been seen. Measure it on 2 runs as its own row.

### 2026-10-29: primary-source rule

One bullet was added to the agent's instructions, and nothing else changed: "For each event you rely on, cite the document that is mainly about that event, not one that only mentions it in passing. If you haven't seen that document yet, search for it." This is a general citation rule. It doesn't name any card, deck or set.

| Date | Pipeline | Questions | Fact recall | Citation recall | Bad citations | Tool calls per question | Seconds per answer | Cost per answer |
|---|---|---|---|---|---|---|---|---|
| 2026-10-29 | Agent + primary-source rule, mean of 2 runs | 21 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) | 0 | 2.86 | 11.0 | $0.057 |

- **Q-006 is fixed in both runs.** After the tournament search, the agent searched "Scarlet & Violet base set release Miraidon ex", working out on its own that Regieleki VMAX is played in Miraidon ex decks and that Miraidon ex came from Scarlet & Violet. Q-008 kept its two-search pattern.
- The extra searches went mostly where they were needed. Questions answered after one search fell from 10-11 to 7 per run, and questions with two searches rose to 11. Cost rose about 14% ($0.050 to $0.057), and latency barely changed.
- Both runs made the same searches with the same queries, so the rule also made the agent more consistent.
- Caveat: 1.00 means this eval is saturated. Only Q-006 and Q-008 were real multi-hop tests, so this shows the rule closed the known gap, not that the agent is reliable on multi-hop questions in general. Harder questions (longer chains, misleading distractor documents) are needed to tell the pipelines apart again.

## 26 questions (2026-10-29)

Five harder questions were added: Q-022 (Regidrago VSTAR after Shrouded Fable brought Kyurem: a three-step link, with an earlier NAIC move as a timing trap), Q-023 (Regidrago V, a false premise), Q-024 (Hisuian Electrode V through a Klawf deck: a three-step link), Q-025 (Scoop Up Net with the direction wrong in the question) and Q-026 (Regidrago VSTAR's fall after Worlds: no known cause, with nearby events that tempt an invented one). The Shrouded Fable and Worlds 2024 documents gained the Kyurem and Regidrago facts these need.

Each question's **Price series** condition is now passed to the price summary in both pipelines (until now both always used `good`). Q-023 is the only question that uses another condition (`nearmint`): its `good` series has 1-9 sales a week, and the weekly medians jump around enough to look like spikes.

| Date | Pipeline | Questions | recall@1 | recall@3 | recall@5 | 1-source recall@5 | 2-source recall@5 |
|---|---|---|---|---|---|---|---|
| 2026-10-29 | Hybrid retrieval | 21 with expected docs (11 one-source, 10 two-source) | 0.62 | 0.86 | 0.95 | 1.00 | 0.90 |

| Date | Pipeline | Questions | Fact recall | Citation recall | Bad citations | Tool calls per question | Seconds per answer | Cost per answer |
|---|---|---|---|---|---|---|---|---|
| 2026-10-29 | Plain RAG: hybrid + `claude-opus-5-5` (medium), mean of 2 runs | 26 | 1.00 (1.00-1.00) | 0.95 (0.95-0.95) | 0 | — | 7.5 | $0.025 |
| 2026-10-29 | Agent + primary-source rule, mean of 2 runs | 26 | 0.99 (0.98-1.00) | 1.00 (1.00-1.00) | 0 | 3.0 | 11.5 | $0.063 |

- **The new questions didn't separate the pipelines.** Both got all five right in both runs. Plain RAG retrieved both expected documents for Q-022 and Q-024, including the Shrouded Fable release, which names Kyurem but not Regidrago. The agent found the same documents by searching for them deliberately ("Shrouded Fable set release Kyurem", "Paradox Rift set release Klawf").
- Both pipelines read the prices correctly on the false-premise and wrong-direction questions (Q-023, Q-025), and neither invented a cause for Q-026. On Q-026 the agent made 5-6 searches looking for a cause, which made it the slowest question (about 20 s).
- Plain RAG's only citation misses are still Q-006 and Q-008 (the Scarlet & Violet release, 0.5 each), which is the whole 0.95 vs 1.00 gap.
- The agent's one fact miss is Q-018 in the second run: the same judge strictness as before (the answer said no tournament, release or announcement explains it, but didn't also say reprint or ban). Left unchanged, as before.
- The agent costs 2.5x as much as plain RAG and is about 1.5x slower, for 5 points of citation recall on two questions.
- **Why harder questions weren't enough:** the corpus has only 26 documents, with a handful in any one month, so top-5 retrieval for a card and month returns most of that month's documents whether or not the link is understood. Real use would have many more documents per month (every Regional, product and article). Growing the corpus with realistic same-month distractors is the experiment that would test whether one-step retrieval breaks down and the agent's searching pays off.
- Two-source share is 10 of 26 (38%), below the 40% rule (it was 8 of 21 after Q-021). The next questions added should be two-source.

## 62-document corpus (2026-10-29)

36 real distractor documents were added for the months the questions cover (other Regionals and Special Events, Japanese and English set releases, Worlds 2024 Seniors and Juniors), so each month has several plausible documents instead of one to three. The questions and answer key are unchanged.

| Date | Retriever | Corpus | Questions | recall@1 | recall@3 | recall@5 | 1-source recall@5 | 2-source recall@5 |
|---|---|---|---|---|---|---|---|---|
| 2026-10-29 | BM25 | 62 event docs | 21 (11 one-source, 10 two-source) | 0.57 | 0.81 | 0.81 | 1.00 | 0.60 |
| 2026-10-29 | Vector (`voyage-4`, `whole_doc`) | 62 event docs | 21 (11 one-source, 10 two-source) | 0.43 | 0.62 | 0.69 | 0.91 | 0.45 |
| 2026-10-29 | Hybrid (RRF) | 62 event docs | 21 (11 one-source, 10 two-source) | 0.50 | 0.69 | 0.81 | 1.00 | 0.60 |

| Date | Pipeline | Questions | Fact recall | 2-source fact recall | Citation recall | Bad citations | Seconds per answer | Cost per answer |
|---|---|---|---|---|---|---|---|---|
| 2026-10-29 | Plain RAG: hybrid + `claude-opus-5-5` (medium), 62 docs, mean of 2 runs | 26 | 0.92 (0.91-0.92) | 0.79 | 0.81 (0.81-0.81) | 0 | 7.1 | $0.025 |

- Hybrid recall@5 fell from 0.95 (26 docs) to 0.81. All of the loss is on two-source questions (0.90 to 0.60); one-source questions stayed at 1.00. The documents that drop out are set releases that don't name the card in the question: Paradox Rift (Q-005, Q-019, Q-024), Scarlet & Violet (Q-006, Q-008, Q-009) and Shrouded Fable (Q-022).
- Vector search suffered most (0.69), even losing a one-source question (Q-003). With several releases and Regionals per month, documents about the same month look alike to the embeddings.
- Plain RAG's answers fell with retrieval: fact recall 1.00 to 0.92, citation recall 0.95 to 0.81. Failures follow the missing document, not bad generation:
  - Q-019 (Dark Patch, facts 0.00 in both runs): all five retrieved documents were distractors. The answer said no provided document explains the rise, instead of inventing a cause.
  - Q-022 (Regidrago VSTAR, 0.00 and 0.33): Worlds 2024 and the NAIC trap were retrieved, but not Shrouded Fable. The answer correctly reasoned that NAIC was too early and Worlds too late, then said nothing explains the rise.
  - Q-006 (0.67 in both runs): the Silver Tempest release (a new distractor) took the place of the Scarlet & Violet release, so Miraidon ex's release isn't mentioned.
- No invented or unseen citations, and the false-premise and no-cause questions still passed. With weaker retrieval, plain RAG says "no document explains this" rather than guessing.

### Agent on 62 documents, without and with the weak-retrieval retry

The retry labels each search result `match="strong"` when both BM25 and vector search found it (fused score at least 0.025) and `match="weak"` when only one did. The agent is told to rephrase and search again when every result is weak, or none is about the card or its deck.

| Date | Pipeline | Questions | Fact recall | Citation recall | Bad citations | Tool calls per question | Seconds per answer | Cost per answer |
|---|---|---|---|---|---|---|---|---|
| 2026-10-29 | Plain RAG (same row as above), mean of 2 runs | 26 | 0.92 (0.91-0.92) | 0.81 (0.81-0.81) | 0 | — | 7.1 | $0.025 |
| 2026-10-31 | Agent + primary-source rule, no retry, mean of 2 runs | 26 | 0.99 (0.97-1.00) | 0.99 (0.98-1.00) | 0 | 2.9 | 12.1 | $0.062 |
| 2026-10-31 | Agent + primary-source rule + retry, mean of 2 runs | 26 | 1.00 (1.00-1.00) | 1.00 (1.00-1.00) | 0 | 2.9 | 11.8 | $0.064 |

- **This is the main phase 2 result.** With distractors in the corpus, the agent's citation recall is 18 points higher than plain RAG's and its fact recall about 7 points higher, for about 2.5x the cost and about 5 s more per answer. On the 26-document corpus the citation gap was only 5 points. The extra searches pay off when one-step retrieval gets crowded out.
- The agent recovers the missing documents by naming them, e.g. "Shrouded Fable set release Kyurem" (Q-022) and "Paradox Rift release Roaring Moon ex" (Q-019). Plain RAG scored 0.00-0.33 on those two questions' facts.
- **The retry made no measurable difference.** Tool calls were the same (2.9), and the search counts barely changed (8 one-search questions per retry run, against 6 and 9 without). The 1 point gap in fact and citation recall is within run-to-run noise.
- The only misses without retry were in one run: Q-007 (one search, so the Scarlet & Violet release was never seen) and Q-022 (the judge failed "four top-8 spots" for not listing the placings). Neither repeated in the other no-retry run, so they can't be credited to the retry's absence.
- **Likely reason: the weak label almost never fires.** Searching with all 26 question texts gave 130 top-5 results and none was weak. Each retriever returns its top 20 of 62 documents, so a document in the fused top 5 has nearly always been found by both. The threshold doesn't separate good matches from poor ones (the Baltimore Regional is "strong" for a Regidrago VSTAR August 2024 search). The agent's own queries weren't checked, and the "none is about the card or its deck" part of the instruction could still have an effect. So this measures a weak signal, not whether retrying is useful.
- Retry was still merged because it did no measurable harm, but this eval doesn't show that it helps. A better signal (e.g. a smaller depth, or the raw BM25 and vector scores) would be needed to test the idea properly.

### 2026-10-31: can a retrieval score detect a missed document?

An offline check with no Claude calls: the 21 question texts with expected documents were run as hybrid searches on the 62-document corpus and split into searches that found every expected document (14) and searches that missed one (7). Separation is the chance that a complete search scores higher than a partial one (0.5 = chance, 1.0 = perfect).

| Signal | Separation | Range, searches that missed | Range, complete searches |
|---|---|---|---|
| Documents in both retrievers' top 5 | 0.46 | 0-3 | 0-3 |
| Top vector similarity | 0.41 | 0.21-0.43 | 0.26-0.44 |
| Top fused (RRF) score | 0.69 | about 0.03 | about 0.03 |
| Top BM25 score | 0.72 | 8.45-16.11 | 8.51-25.02 |

- No signal gives a usable threshold. The top-5 overlap and vector similarity are no better than chance, fused scores are all about 0.03, and BM25's ranges overlap heavily. Every miss is a two-source question, so BM25's separation may partly reflect question type.
- The likely reason: these misses aren't weak searches. In Q-022 the search finds Worlds 2024 with a strong match. The missing Shrouded Fable release never names Regidrago, so nothing in the scores shows it's absent.
- The agent's working retry is the model's own judgement that the evidence is incomplete, driven by the primary-source rule and "search again" instructions. That produces searches like "Shrouded Fable set release Kyurem".
- Limits: only 21 searches, using question texts rather than the agent's own queries. This doesn't rule out a score signal on other corpora.
- Decision: remove the `match="strong"` / `match="weak"` labels, since they say almost nothing about whether evidence is missing. No new score-based signal was built. The agent without labels has not been measured.

## Phase 2 final comparison: 28 questions, 62 documents (2026-10-31)

Same questions, corpus, model (`claude-opus-5-5`, medium effort) and scoring for both pipelines. This set adds two two-source questions (Q-027 Magma Basin, Q-028 Regidrago V 135), so 12 of 28 questions (43%) need two sources. It's the baseline for phase 3. The agent's final version has the primary-source rule and no strong/weak labels, and this is the first measurement of that version. Three documents also changed before these runs: Worlds 2024 (corrected to Regidrago V 135), LAIC 2023 and Paradox Rift (Entei and Iron Valiant ex facts).

| Date | Pipeline | Questions | recall@1 | recall@3 | recall@5 | 1-source recall@5 | 2-source recall@5 |
|---|---|---|---|---|---|---|---|
| 2026-10-31 | Hybrid retrieval | 23 with expected docs (11 one-source, 12 two-source) | 0.48 | 0.67 | 0.74 | 1.00 | 0.50 |

| Date | Pipeline | Questions | Fact recall | 2-source fact recall | Citation recall | Bad citations | Tool calls per question | Seconds per answer | Cost per answer |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-31 | Plain RAG, mean of 2 runs | 28 | 0.87 (0.86-0.88) | 0.71 | 0.74 (0.74-0.74) | 0 | — | 7.1 | $0.025 |
| 2026-10-31 | Agent, mean of 2 runs | 28 | 0.99 (0.98-0.99) | 0.99 | 0.99 (0.98-1.00) | 0 | 2.9 | 11.5 | $0.063 |

- **Result:** the agent's fact recall is 12 points higher and its citation recall 25 points higher, for about 2.5x the cost and 1.6x the latency (4.4 s more per answer). On one-source questions the two tie at 1.00 on facts, and almost all of the gap is on two-source questions, so plain RAG is the cheaper choice when one document is enough.
- Plain RAG's failures come from retrieval. Two-source recall@5 is 0.50, and all five documents for Q-019 and Q-027 miss. Its answers then say the documents don't explain the move, with no bad citations.
- Q-027 (Magma Basin) separates the pipelines most: plain RAG scored 0.00 on facts in both runs, the agent 1.00 in both. The agent's own query, "Magma Basin deck tournament results November 2023", finds the LAIC document that the full question text misses. In one run it stopped there, so citation recall was 0.5 even though the facts passed.
- Q-023 and Q-028 (same card name, different printings): both pipelines passed Q-023 in both runs, and the agent passed Q-028 in both. Plain RAG scored 0.50 on Q-028 because it never retrieved Shrouded Fable.
- Agent fact misses: Q-018 in one run and Q-022 in one run, both judge strictness seen before (not saying "reprint or ban"; "four top-8 spots" instead of the placings). Plain RAG also missed Q-021 in one run for not stating that there was no spike. These facts were left unchanged.
- Caveats: 28 questions is small; one question moves fact recall by about 3.6 points. The documents were written for this eval, and the distractors were chosen for the months and decks the questions cover. Treat the size of the gap as specific to this corpus. Fact recall is judged by Claude, so those scores also depend on the judge.

## Where the time and money go (2026-11-01)

Each step of an answer is now timed and saved in the run file as a trace (`src/tracing.py`), and `run_answers` prints a per-step summary. One run of each pipeline on the 28 questions and 62 documents. Fact and citation scores from these runs match the baseline within noise (plain RAG 0.86 and 0.74, agent 0.98 and 1.00).

| Per question | Plain RAG | Agent |
|---|---|---|
| Seconds per answer | 7.0 | 10.9 |
| Claude: calls | 1.0 | 2.9 |
| Claude: seconds | 6.92 | 10.05 |
| Search: calls | 1.0 | 1.9 |
| Search: seconds | 0.05 | 0.84 |
| Price lookup: seconds | 0.02 | 0.02 |
| Input tokens | 3,113 | 12,368 |
| Output tokens | 648 | 756 |
| Input cost | $0.013 | $0.049 |
| Output cost | $0.013 | $0.015 |
| Total answer cost | $0.025 | $0.065 |

- **Latency is almost all Claude:** about 99% of plain RAG's time and 92% of the agent's. Of the agent's extra 3.9 s, about 3.1 s is extra Claude time and about 0.8 s is search.
- **The agent's extra cost is almost all input tokens.** It reads about 4x as many (12,368 vs 3,113) but writes only about 17% more. Every round resends the whole conversation, including every document already returned. Input is about three quarters of its cost.
- **No Voyage rate-limit wait showed up in this run:** the slowest of 54 agent searches took 1.07 s. Earlier runs weren't traced, so this doesn't show they had none.
- **Plain RAG's search time is understated.** Its query embeddings are made in one batch before the timer starts, so its search takes 0.05 s, while each agent search takes a median of 0.44 s including its embedding request. This difference is under 0.5 s per question, so it doesn't change the comparison.
- The agent's final Claude call averages 5.62 s and 463 output tokens. Its earlier calls together average 4.44 s and 292 output tokens per question.

## Prompt caching for the agent (2026-11-01)

The agent's API call now sets top-level automatic caching (`cache_control: {"type": "ephemeral"}`, 5-minute lifetime). Plain RAG is unchanged. Cost now charges uncached input at $4, cache reads at $0.20, cache writes at $5 and output at $20 per million tokens. Two runs on the 28 questions and 62 documents, compared with the uncached traced run above.

| Per question | Agent, no caching (1 run) | Agent, caching (mean of 2 runs) |
|---|---|---|
| Fact recall | 0.98 | 1.00 |
| Citation recall | 1.00 | 1.00 |
| Seconds per answer | 10.9 | 10.7 |
| Uncached input tokens | 12,368 | 8 |
| Cache read tokens | — | 5,557 |
| Cache write tokens | — | 6,722 |
| Output tokens | 756 | 750 |
| Input cost (uncached, read and write) | $0.049 | $0.035 |
| Output cost | $0.015 | $0.015 |
| **Total answer cost** | **$0.065** | **$0.050** |

- **Caching cut the agent's cost by about 23%,** from $0.065 to $0.050 per answer, or about 2x plain RAG instead of 2.6x. The cache was working as designed: each call read what earlier calls wrote.
- Input cost fell only about 30% even though reads are 95% cheaper than normal input. With about 3 calls per question, most tokens are read once or twice, and over half are writes at the higher $5 rate, including the last call's new content, which is never read back. Longer loops should gain more; this wasn't measured.
- Latency and accuracy show no change beyond run-to-run noise.
- **Correction:** the two caching runs printed $0.065 per question because of a bug in that version, where output tokens were counted twice in the answer's totals. The figures above are recomputed from the saved traces, which were not affected. The bug is fixed.
- Each question's first call read nothing from the cache, so the tools and system prompt (part of the roughly 1,250 tokens first written) aren't shared between questions. An explicit breakpoint after the system prompt might save a little more; not tested.
