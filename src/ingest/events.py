from datetime import date
from pathlib import Path

REQUIRED = ["date", "title", "type", "sources", "written"]


def parse_front_matter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("document must start with a --- line")

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise ValueError("front matter has no closing --- line")

    meta = {}
    current_list = None
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            if current_list is None:
                raise ValueError(f"list item outside a list: {line}")
            meta[current_list].append(stripped[2:].strip())
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if value:
            meta[key] = value
            current_list = None
        else:
            meta[key] = []        # e.g. "cards:" with items on the next lines
            current_list = key

    body = "\n".join(lines[end + 1:]).strip()
    return meta, body


def load_event(path):
    """Load one event document into a dict."""
    path = Path(path)
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))

    missing = [field for field in REQUIRED if field not in meta]
    if missing:
        raise ValueError(f"{path.name}: missing {', '.join(missing)}")

    for field in ("date", "start_date", "written"):
        if field in meta:
            meta[field] = date.fromisoformat(meta[field])

    return {"id": path.stem, **meta, "body": body}


def load_events(folder="data/events"):
    """Load every event document in a folder, oldest first."""
    events = [load_event(p) for p in Path(folder).glob("*.md")]
    return sorted(events, key=lambda e: e["date"])
