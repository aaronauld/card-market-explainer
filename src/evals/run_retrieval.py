"""Measure retrieval: for each eval question, do the expected event docs come back?"""
from src.evals.questions import load_questions
from src.ingest.events import load_events
from src.retrieval.bm25 import BM25

K_VALUES = [1, 3, 5]


def recall_at_k(expected, retrieved, k):
    """Fraction of the expected doc ids found in the first k retrieved ids."""
    top = set(retrieved[:k])
    return sum(doc in top for doc in expected) / len(expected)


def average(numbers):
    return sum(numbers) / len(numbers) if numbers else 0.0


def main():
    events = load_events()
    index = BM25([(e["id"], e["title"] + "\n" + e["body"]) for e in events])
    questions = [q for q in load_questions() if q["event_docs"]]
    print(f"{len(events)} event docs, {len(questions)} questions with expected docs\n")

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


if __name__ == "__main__":
    main()
