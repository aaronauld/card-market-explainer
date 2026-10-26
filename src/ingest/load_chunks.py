"""Chunk event documents, embed the chunks with Voyage, and store them in pgvector."""
import sys

from src.ingest.common import connect, read_env
from src.ingest.events import load_events
from src.retrieval.chunking import chunk_event
from src.retrieval.voyage import embed


def to_pgvector(vector):
    """Format a list of floats the way pgvector reads it: '[0.1,0.2,...]'."""
    return "[" + ",".join(str(x) for x in vector) + "]"


def main(strategy):
    env = read_env()
    chunks = [c for event in load_events()
              for c in chunk_event(event, strategy)]
    print(f"{len(chunks)} chunks ({strategy}), embedding...")
    vectors = embed([c["text"] for c in chunks],
                    "document", env["VOYAGE_API_KEY"])

    with connect(env) as conn:
        conn.execute("DELETE FROM chunks WHERE strategy = %s", (strategy,))
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO chunks (doc_id, chunk_index, strategy, doc_date, text, embedding) "
                "VALUES (%s, %s, %s, %s, %s, %s::vector)",
                [
                    (c["doc_id"], c["chunk_index"], c["strategy"], c["doc_date"],
                     c["text"], to_pgvector(v))
                    for c, v in zip(chunks, vectors)
                ],
            )
        conn.commit()
    print(f"stored {len(chunks)} chunks")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "whole_doc")
