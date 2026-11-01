"""Run every eval question through the full RAG pipeline and score the answers."""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from src.evals.questions import load_questions
from src.evals.run_retrieval import average, build_retriever
from src.evals.score_answer import check_citations, judge_facts
from src.generation.answer import answer
from src.generation.claude import Claude
from src.ingest.events import load_events
from src.agent.agent import answer_with_agent
from src.tracing import Trace

DOLLARS_PER_MILLION = {"input": 4.00, "output": 20.00,
                       "cache_read": 0.20, "cache_write": 5.00}  # claude-opus-5-5


def cost(result):
    tokens = {
        "input": result["input_tokens"],
        "output": result["output_tokens"],
        "cache_read": result.get("cache_read_tokens", 0),
        "cache_write": result.get("cache_write_tokens", 0),
    }
    return sum(tokens[kind] * DOLLARS_PER_MILLION[kind] for kind in tokens) / 1_000_000


def main(retriever_name):
    questions = load_questions()
    events = {e["id"]: e for e in load_events()}
    if retriever_name == "agent":
        pipeline, retriever = answer_with_agent, build_retriever("hybrid")
    else:
        pipeline, retriever = answer, build_retriever(retriever_name)
        if hasattr(retriever, "prepare"):
            retriever.prepare([q["question"] for q in questions])
    llm, judge = Claude(), Claude(effort="low")

    rows = []
    for q in questions:
        start = time.perf_counter()
        result = pipeline(q["question"], q["card_id"], q["variant"], q["move_date"],
                          retriever, llm, events, condition=q["condition"])
        seconds = time.perf_counter() - start

        citations = check_citations(result, q["event_docs"], set(events))
        facts = judge_facts(q["question"], result["answer"],
                            q["must_mention"], judge)
        fact_recall = sum(f["present"] for f in facts) / len(facts)

        rows.append({
            "id": q["id"], "status": q["status"], "sources_needed": q["sources_needed"],
            "has_docs": bool(q["event_docs"]), "fact_recall": fact_recall,
            "seconds": round(seconds, 1),
            "cost": cost(result),
            **citations, "facts": facts, **result,
        })
        bad = len(citations["invented"]) + len(citations["not_retrieved"])
        print(f"{q['id']}  facts={fact_recall:.2f}  citations={citations['citation_recall']}  "
              f"bad_citations={bad}  {seconds:.1f}s")

    print(f"\nfact recall: {average([r['fact_recall'] for r in rows]):.2f}")
    for status in ("confirmed", "likely", "no known cause", "false premise"):
        subset = [r["fact_recall"] for r in rows if r["status"] == status]
        print(f"  {status} ({len(subset)}): {average(subset):.2f}")
    for n in (1, 2):
        subset = [r["fact_recall"]
                  for r in rows if r["has_docs"] and r["sources_needed"] == n]
        print(f"  {n}-source ({len(subset)}): {average(subset):.2f}")
    recalls = [r["citation_recall"]
               for r in rows if r["citation_recall"] is not None]
    print(f"citation recall: {average(recalls):.2f}")
    print(
        f"bad citations: {sum(len(r['invented']) + len(r['not_retrieved']) for r in rows)}")
    calls = [len(r.get("tool_calls", [])) for r in rows]
    print(f"avg tool calls per question: {average(calls):.1f}")
    print(
        f"avg seconds per answer: {average([r['seconds'] for r in rows]):.1f}")
    all_steps = Trace()
    all_steps.spans = [span for r in rows for span in r["trace"]]
    print("time per question by step:")
    for name, step in all_steps.summary().items():
        print(f"  {name}: {step['calls'] / len(rows):.1f} calls, "
              f"{step['seconds'] / len(rows):.2f}s")
    print(f"answer cost: ${sum(r['cost'] for r in rows):.2f} total, "
          f"${average([r['cost'] for r in rows]):.3f} per question")

    out = Path("data/runs") / \
        f"answers-{retriever_name}-{datetime.now():%Y-%m-%d-%H%M}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2, default=str), encoding="utf-8")
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "hybrid")
