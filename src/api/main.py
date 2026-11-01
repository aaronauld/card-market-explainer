"""HTTP service: ask why a card's price moved, get an answer with citations."""
import secrets
import threading

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader

from datetime import date
from typing import Literal

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

settings = read_env()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

spend_lock = threading.Lock()
spend = {"day": None, "dollars": 0.0}


def require_api_key(key=Depends(api_key_header)):
    """Refuse the request unless it has the right key. No key configured means nobody gets in."""
    expected = settings.get("API_KEY")
    if not expected or not key or not secrets.compare_digest(key.encode(), expected.encode()):
        raise HTTPException(
            status_code=401, detail="Invalid or missing API key")


def check_budget():
    """Refuse the request if today's spending has reached the limit."""
    limit = float(settings.get("MAX_DAILY_DOLLARS", 0))
    with spend_lock:
        if spend["day"] != date.today():
            spend.update(day=date.today(), dollars=0.0)
        if spend["dollars"] >= limit:
            raise HTTPException(
                status_code=429, detail="Daily spending limit reached")


def record_spend(dollars):
    with spend_lock:
        spend["dollars"] += dollars


def card_exists(card_id):
    with connect(read_env()) as conn:
        row = conn.execute(
            "SELECT 1 FROM cards WHERE id = %s", (card_id,)).fetchone()
    return row is not None


class ExplainRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    card_id: str
    variant: Literal["normal", "reverse", "holo"]
    move_date: date
    condition: Literal["good", "nearmint"] = "good"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/explain", dependencies=[Depends(require_api_key), Depends(check_budget)])
def explain(request: ExplainRequest):
    if not card_exists(request.card_id):
        raise HTTPException(
            status_code=404, detail=f"Unknown card id: {request.card_id}")
    result = answer_with_agent(
        request.question, request.card_id, request.variant, request.move_date,
        retriever, llm, events, condition=request.condition)
    answer_cost = cost(result)
    record_spend(answer_cost)
    return {
        "answer": result["answer"],
        "cited": result["cited"],
        "tool_calls": result["tool_calls"],
        "cost_dollars": round(answer_cost, 4),
        "trace": result["trace"],
    }
