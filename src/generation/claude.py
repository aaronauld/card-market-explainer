"""Call Claude through the official Anthropic SDK."""
import anthropic
import json

from src.ingest.common import read_env

MODEL = "claude-opus-5-5"

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


class Claude:
    def __init__(self, model=MODEL, effort="medium"):
        self.model = model
        self.effort = effort
        self.client = anthropic.Anthropic(
            api_key=read_env()["ANTHROPIC_API_KEY"])

    def ask(self, system, prompt, max_tokens=16000, schema=None):
        """Send one message. Returns (answer_text, usage).
        If a JSON schema is given, the reply is guaranteed to match it."""
        output_config = {"effort": self.effort}
        if schema:
            output_config["format"] = {
                "type": "json_schema", "schema": schema}
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            output_config=output_config,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        if response.stop_reason == "refusal":
            raise RuntimeError(
                f"Claude declined the request: {response.stop_details}")
        if response.stop_reason == "max_tokens":
            raise RuntimeError("Answer was cut off: raise max_tokens")

        text = "".join(
            block.text for block in response.content if block.type == "text")
        return text, response.usage

    def ask_json(self, system, prompt, schema):
        """Like ask, but returns the reply parsed into Python (dicts and lists)."""
        text, usage = self.ask(system, prompt, schema=schema)
        return json.loads(text), usage

    def create(self, system, messages, tools=None, max_tokens=16000):
        """One API call with a full message list. Returns the raw response (used by the agent)."""
        extra = {"tools": tools} if tools else {}
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            cache_control={"type": "ephemeral"},
            output_config={"effort": self.effort},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            **extra,
        )
        if response.stop_reason == "refusal":
            raise RuntimeError(
                f"Claude declined the request: {response.stop_details}")
        if response.stop_reason == "max_tokens":
            raise RuntimeError("Response was cut off: raise max_tokens")
        return response
