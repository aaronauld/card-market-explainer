"""Tools the agent can call: the definitions Claude sees, and the code that runs them."""
from datetime import date

from src.ingest.common import connect, read_env
from src.prices import price_context

TOOLS = [
    {
        "name": "search_documents",
        "description": (
            "Search the event documents (tournament results, set releases, rotation and ban "
            "announcements). Returns the 5 most relevant, each with its id and date. Search again "
            "with a different query if the first results don't explain the move, for example for "
            "the deck a card is played in, or the set that deck's main card came from."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for, in plain words."}
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "get_price_summary",
        "description": (
            "Weekly median prices and sale counts for one card, from 6 weeks before to 4 weeks "
            "after a date. Use it for the card in the question, or for related cards."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "card_id": {"type": "string", "description": "TCGdex card id, e.g. 'swsh6-187'."},
                "variant": {"type": "string", "enum": ["normal", "reverse", "holo"]},
                "around_date": {"type": "string", "description": "Date to centre on, as YYYY-MM-DD."},
            },
            "required": ["card_id", "variant", "around_date"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "find_cards",
        "description": "Look up cards by name. Returns up to 20 matching card ids with their set and number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Card name or part of it, e.g. 'Miraidon ex'."}
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


class ToolBox:
    """Runs the tools, and remembers every document the model has been shown."""

    def __init__(self, retriever, events, condition="good"):
        self.retriever = retriever
        self.events = events
        self.seen_doc_ids = []
        self.condition = condition

    def run(self, name, args):
        if name == "search_documents":
            return self.search_documents(args["query"])
        if name == "get_price_summary":
            return price_context(args["card_id"], args["variant"],
                                 date.fromisoformat(args["around_date"]),
                                 condition=self.condition)
        if name == "find_cards":
            return self.find_cards(args["name"])
        raise ValueError(f"unknown tool: {name}")

    def search_documents(self, query):
        doc_ids = [doc_id for doc_id, _ in self.retriever.search(query, k=5)]
        parts = []
        for doc_id in doc_ids:
            if doc_id not in self.seen_doc_ids:
                self.seen_doc_ids.append(doc_id)
            doc = self.events[doc_id]
            parts.append(
                f'<document id="{doc_id}" date="{doc["date"]}">\n{doc["body"]}\n</document>')
        return "\n\n".join(parts)

    def find_cards(self, name):
        with connect(read_env()) as conn:
            rows = conn.execute(
                "SELECT id, name, set_name, local_id FROM cards "
                "WHERE name ILIKE %s ORDER BY id LIMIT 20",
                (f"%{name}%",),
            ).fetchall()
        if not rows:
            return "No cards found."
        return "\n".join(f"{card_id}: {card} ({set_name}, {number})"
                         for card_id, card, set_name, number in rows)
