"""Answer a price question: retrieve documents, add prices, ask Claude, collect citations."""
import re

from src.generation.claude import Claude
from src.ingest.common import connect, read_env
from src.ingest.events import load_events
from src.prices import price_context

SYSTEM = """You explain why a Pokémon trading card's price moved, using only the weekly prices and documents provided.

- Describe the move from the weekly prices: when it started and roughly how large it was.
- Explain the cause using the documents. Cite every document you rely on by its id in square brackets, e.g. [2023-11-19-laic-2023-results].
- Only use a document if it plausibly connects to this card (it names the card, or a deck or set the card is used with) and its date fits the move. Say what the connection is.
- If no document explains the move, say so plainly instead of guessing.
- Explain the past only: no predictions and no buying or selling advice.
- Keep the answer under 150 words."""

CITATION = re.compile(r"\[(\d{4}-\d{2}-\d{2}-[a-z0-9.-]+)\]")


def card_label(card_id):
    """'Avery (Chilling Reign, 187), id swsh6-187' from the cards table."""
    with connect(read_env()) as conn:
        row = conn.execute(
            "SELECT name, set_name, local_id FROM cards WHERE id = %s", (
                card_id,)
        ).fetchone()
    return f"{row[0]} ({row[1]}, {row[2]}), id {card_id}" if row else card_id


def build_prompt(question, card, prices, documents):
    """Wrap each input in its own tag so the model can tell them apart."""
    parts = [
        f"<question>\n{question}\n</question>",
        f"<card>\n{card}\n</card>",
        f"<weekly_prices>\n{prices}\n</weekly_prices>",
        "<documents>",
    ]
    for doc in documents:
        parts.append(
            f'<document id="{doc["id"]}" date="{doc["date"]}">\n{doc["body"]}\n</document>')
    parts.append("</documents>")
    return "\n\n".join(parts)


def answer(question, card_id, variant, move_date, retriever, llm, events, k=5):
    """Run the whole pipeline for one question. Returns a dict for the harness."""
    doc_ids = [doc_id for doc_id, _ in retriever.search(question, k=k)]
    prompt = build_prompt(
        question,
        card_label(card_id),
        price_context(card_id, variant, move_date),
        [events[doc_id] for doc_id in doc_ids],
    )
    text, usage = llm.ask(SYSTEM, prompt)
    return {
        "answer": text,
        "retrieved": doc_ids,
        "cited": CITATION.findall(text),
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
    }


if __name__ == "__main__":
    import sys
    from src.evals.questions import load_questions
    from src.evals.run_retrieval import build_retriever

    question_id = sys.argv[1] if len(sys.argv) > 1 else "Q-002"
    q = next(x for x in load_questions() if x["id"] == question_id)
    events = {e["id"]: e for e in load_events()}
    result = answer(q["question"], q["card_id"], q["variant"], q["move_date"],
                    build_retriever("hybrid"), Claude(), events)
    print(result["answer"])
    print("\nretrieved:", result["retrieved"])
    print("cited:    ", result["cited"])
    print("tokens:   ", result["input_tokens"],
          "in,", result["output_tokens"], "out")
