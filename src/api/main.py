"""HTTP service: ask why a card's price moved, get an answer with citations."""
from datetime import date
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agent.agent import answer_with_agent
from src.evals.run_retrieval import build_retriever
from src.generation.claude import Claude, cost
from src.ingest.events import load_events
from src.ingest.common import connect, read_env

app = FastAPI(title="card-market-explainer")

# Loaded once at startup, because they're slow to build and every request can share them.
retriever = build_retriever("hybrid")
events = {e["id"]: e for e in load_events()}
llm = Claude()


class ExplainRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    card_id: str
    variant: Literal["normal", "reverse", "holo"]
    move_date: date
    condition: Literal["good", "nearmint"] = "good"


def card_exists(card_id):
    with connect(read_env()) as conn:
        row = conn.execute(
            "SELECT 1 FROM cards WHERE id = %s", (card_id,)).fetchone()
    return row is not None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/explain")
def explain(request: ExplainRequest):
    if not card_exists(request.card_id):
        raise HTTPException(
            status_code=404, detail=f"Unknown card id: {request.card_id}")
    result = answer_with_agent(
        request.question, request.card_id, request.variant, request.move_date,
        retriever, llm, events, condition=request.condition)
    return {
        "answer": result["answer"],
        "cited": result["cited"],
        "tool_calls": result["tool_calls"],
        "cost_dollars": round(cost(result), 4),
        "trace": result["trace"],
    }
