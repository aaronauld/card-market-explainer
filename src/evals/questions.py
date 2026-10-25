"""Read eval questions from docs/eval-questions.md."""
import re
from datetime import date
from pathlib import Path

FIELD = re.compile(r"^- \*\*(.+?):\*\*\s*(.*)$")   # "- **Name:** value"
BACKTICKS = re.compile(r"`([^`]+)`")               # text inside `...`


def parse_entry(heading, lines):
    """Turn one '### Q-...' block into a dict."""
    fields = {}
    for line in lines:
        match = FIELD.match(line)          # indented note lines don't match
        if match:
            fields[match.group(1).lower()] = match.group(2).strip()

    qid, title = heading.split(":", 1)
    variant, condition = [p.strip()
                          for p in fields["price series"].split(",")[:2]]

    return {
        "id": qid.strip(),
        "title": title.strip(),
        "status": fields["status"],
        "question": fields["question"],
        "card_id": BACKTICKS.findall(fields["card id"])[0],
        "variant": variant,
        # "good (also visible...)" -> "good"
        "condition": condition.split()[0],
        "move_date": date.fromisoformat(fields["date of move"][:10]),
        "must_mention": [p.strip() for p in fields["answer must mention"].split(";") if p.strip()],
        "sources_needed": int(fields["sources needed"][0]),
        "event_docs": BACKTICKS.findall(fields.get("event docs", "")),
    }


def load_questions(path="docs/eval-questions.md"):
    """Load every entry under '## Entries' (not the template or candidates)."""
    text = Path(path).read_text(encoding="utf-8")
    entries = text.split("\n## Entries", 1)[1].split("\n## ", 1)[0]
    blocks = re.split(r"^### ", entries, flags=re.MULTILINE)[1:]
    return [parse_entry(block.splitlines()[0], block.splitlines()[1:]) for block in blocks]
