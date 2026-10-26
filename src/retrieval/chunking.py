"""Split event documents into chunks for embedding."""


def whole_doc(event):
    """One chunk per document: the title and full body, the same text BM25 indexes."""
    return [event["title"] + "\n" + event["body"]]


def by_section(event):
    """One chunk per '## ' section, each starting with the document title for context.
    The Sources section is skipped: it only says where the facts came from."""
    chunks = []
    heading, lines = None, []

    def save():
        text = "\n".join(lines).strip()
        if heading and heading != "Sources" and text:
            chunks.append(f"{event['title']}\n{heading}\n{text}")

    for line in event["body"].splitlines():
        if line.startswith("## "):
            save()                                  # finish the previous section
            heading, lines = line[3:].strip(), []   # start a new one
        elif heading:
            lines.append(line)
    save()                                          # finish the last section
    return chunks


def chunk_event(event, strategy):
    """Return chunk dicts ready to embed and store."""
    split = {"whole_doc": whole_doc, "by_section": by_section}[strategy]
    return [
        {
            "doc_id": event["id"],
            "chunk_index": i,
            "strategy": strategy,
            "doc_date": event["date"],
            "text": text,
        }
        for i, text in enumerate(split(event))
    ]
