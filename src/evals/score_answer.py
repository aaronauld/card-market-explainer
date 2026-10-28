"""Score one generated answer: citation checks in code, fact checks by an LLM judge."""

JUDGE_SYSTEM = """You grade an answer against a checklist of facts.
For each fact, decide whether the answer states it. A paraphrase counts. A fact the answer only hints at, contradicts, or marks as unknown does not count.
Judge only from the answer's text, not from your own knowledge."""

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "facts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fact": {"type": "string"},
                    "present": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
                "required": ["fact", "present", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["facts"],
    "additionalProperties": False,
}


def check_citations(result, expected_docs, known_doc_ids):
    """Checks that need no model: are the citations real, and are they the right ones?"""
    cited = set(result["cited"])
    expected = set(expected_docs)
    return {
        "invented": sorted(cited - known_doc_ids),
        "not_retrieved": sorted(cited - set(result["retrieved"])),
        "citation_recall": len(cited & expected) / len(expected) if expected else None,
        "cited_count": len(cited),
    }


def judge_facts(question, answer_text, facts, judge):
    """Ask the judge which 'Answer must mention' facts the answer states."""
    checklist = "\n".join(f"{i}. {fact}" for i,
                          fact in enumerate(facts, start=1))
    prompt = (
        f"<question>\n{question}\n</question>\n\n"
        f"<answer>\n{answer_text}\n</answer>\n\n"
        f"<facts>\n{checklist}\n</facts>"
    )
    graded, _ = judge.ask_json(JUDGE_SYSTEM, prompt, JUDGE_SCHEMA)
    return graded["facts"]


if __name__ == "__main__":
    import sys
    from src.evals.questions import load_questions
    from src.evals.run_retrieval import build_retriever
    from src.generation.answer import answer
    from src.generation.claude import Claude
    from src.ingest.events import load_events

    question_id = sys.argv[1] if len(sys.argv) > 1 else "Q-006"
    q = next(x for x in load_questions() if x["id"] == question_id)
    events = {e["id"]: e for e in load_events()}

    result = answer(q["question"], q["card_id"], q["variant"], q["move_date"],
                    build_retriever("hybrid"), Claude(), events)
    print(result["answer"], "\n")
    print("citations:", check_citations(result, q["event_docs"], set(events)))
    for fact in judge_facts(q["question"], result["answer"], q["must_mention"], Claude(effort="low")):
        print(("PASS " if fact["present"] else "FAIL ") +
              fact["fact"], "-", fact["reason"])
