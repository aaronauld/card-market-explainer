"""The agent: Claude decides which tools to call, in a loop, until it writes an answer."""
from src.agent.tools import TOOLS, ToolBox
from src.generation.answer import CITATION, card_label
from src.tracing import Trace

SYSTEM = """You explain why a Pokémon trading card's price moved, using tools to look up prices and event documents.

- Get the price summary for the card in the question, then search the documents.
- If no result of a search is about the card or its deck, rephrase the query (use card, deck or set names) and search again.
- Use only what the tools return. Cite every document you rely on by its id in square brackets, e.g. [2023-11-19-laic-2023-results], and say how it connects to this card.
- For each event you rely on, cite the document that is mainly about that event, not one that only mentions it in passing. If you haven't seen that document yet, search for it.
- If nothing explains the move, say so plainly instead of guessing. If the question assumes a move the prices don't show, say so.
- Explain the past only: no predictions and no buying or selling advice.
- If every result of a search is a weak match, or none is about the card or its deck, rephrase the query (use card, deck or set names) and search again.
- Keep the final answer under 150 words."""

MAX_ROUNDS = 8


def answer_with_agent(question, card_id, variant, move_date, retriever, llm, events, condition="good"):
    """Run the agent for one question. Returns the same kind of dict as answer()."""
    toolbox = ToolBox(retriever, events, condition)
    messages = [{"role": "user", "content": (
        f"<question>\n{question}\n</question>\n\n"
        f"<card>\n{card_label(card_id)}, variant {variant}\n</card>\n\n"
        f"<move_date>\n{move_date}\n</move_date>"
    )}]
    input_tokens = output_tokens = 0
    trace = Trace()
    tool_calls = []

    for _ in range(MAX_ROUNDS):
        with trace.span("claude") as span:
            response = llm.create(SYSTEM, messages, tools=TOOLS)
            span["input_tokens"] = response.usage.input_tokens
            span["output_tokens"] = response.usage.output_tokens
        input_tokens += response.usage.input_tokens
        output_tokens += response.usage.output_tokens
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break  # Claude has written its final answer

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            tool_calls.append({"name": block.name, "input": block.input})
            try:
                with trace.span(block.name, input=block.input):
                    output = toolbox.run(block.name, block.input)
                is_error = False
            except Exception as err:
                output, is_error = f"Tool error: {err}", True
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": output, "is_error": is_error})
        messages.append({"role": "user", "content": results})

    if response.stop_reason == "tool_use":
        raise RuntimeError(
            f"agent still calling tools after {MAX_ROUNDS} rounds")

    text = "".join(
        block.text for block in response.content if block.type == "text")
    return {
        "answer": text,
        "retrieved": toolbox.seen_doc_ids,
        "cited": CITATION.findall(text),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tool_calls": tool_calls,
        "trace": trace.spans,
    }


if __name__ == "__main__":
    import sys
    from src.evals.questions import load_questions
    from src.evals.run_retrieval import build_retriever
    from src.generation.claude import Claude
    from src.ingest.events import load_events

    question_id = sys.argv[1] if len(sys.argv) > 1 else "Q-006"
    q = next(x for x in load_questions() if x["id"] == question_id)
    events = {e["id"]: e for e in load_events()}
    result = answer_with_agent(q["question"], q["card_id"], q["variant"], q["move_date"],
                               build_retriever("hybrid"), Claude(), events)
    for call in result["tool_calls"]:
        print("tool:", call["name"], call["input"])
    print("\n" + result["answer"])
    print("\nseen:  ", result["retrieved"])
    print("cited: ", result["cited"])
    print("tokens:", result["input_tokens"],
          "in,", result["output_tokens"], "out")
