"""Measure retrieval: for each eval question, do the expected event docs come back?"""
import sys
from src.retrieval.vector import VectorSearch

from src.evals.questions import load_questions
from src.ingest.events import load_events
from src.retrieval.bm25 import BM25
from src.retrieval.hybrid import HybridSearch

K_VALUES = [1, 3, 5]


def recall_at_k(expected, retrieved, k):
    """Fraction of the expected doc ids found in the first k retrieved ids."""
    top = set(retrieved[:k])
    return sum(doc in top for doc in expected) / len(expected)


def average(numbers):
    return sum(numbers) / len(numbers) if numbers else 0.0


def build_retriever(name):
    """Return an object with a search(query, k) method."""
    if name == "bm25":
        events = load_events()
        return BM25([(e["id"], e["title"] + "\n" + e["body"]) for e in events])
    if name == "vector":
        return VectorSearch("whole_doc")
    if name == "vector-sections":
        return VectorSearch("by_section")
    if name == "hybrid":
        return HybridSearch([build_retriever("bm25"), build_retriever("vector")])
    raise ValueError(
        f"unknown retriever: {name} (use bm25, vector or vector-sections)")


def main(name):
    index = build_retriever(name)
    questions = [q for q in load_questions() if q["event_docs"]]
    if hasattr(index, "prepare"):
        index.prepare([q["question"] for q in questions])
    print(
        f"retriever: {name}, {len(questions)} questions with expected docs\n")

    results = []
    for q in questions:
        retrieved = [doc_id for doc_id, _ in index.search(
            q["question"], k=max(K_VALUES))]
        scores = {k: recall_at_k(q["event_docs"], retrieved, k)
                  for k in K_VALUES}
        missed = [doc for doc in q["event_docs"] if doc not in retrieved]
        results.append((q, scores))
        status = "ok" if not missed else "missed " + ", ".join(missed)
        print(
            f"{q['id']}  sources={q['sources_needed']}  recall@5={scores[5]:.2f}  {status}")

    print()
    for k in K_VALUES:
        print(f"recall@{k}: {average([s[k] for _, s in results]):.2f}")

    print()
    for n in (1, 2):
        subset = [s[5] for q, s in results if q["sources_needed"] == n]
        print(
            f"recall@5 for {n}-source questions ({len(subset)}): {average(subset):.2f}")

        subset_scores = {n: average([s[5] for q, s in results if q["sources_needed"] == n])
                         for n in (1, 2)}
    return {
        **{f"recall@{k}": average([s[k] for _, s in results]) for k in K_VALUES},
        "1-source recall@5": subset_scores[1],
        "2-source recall@5": subset_scores[2],
    }


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "bm25")
