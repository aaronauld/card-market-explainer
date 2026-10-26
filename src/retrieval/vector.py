"""Embedding retrieval: find the chunks closest to a question in pgvector."""
from src.ingest.common import connect, read_env
from src.retrieval.voyage import embed


def to_pgvector(vector):
    return "[" + ",".join(str(x) for x in vector) + "]"


class VectorSearch:
    def __init__(self, strategy="whole_doc"):
        self.strategy = strategy
        self.env = read_env()
        self.conn = connect(self.env)
        self.query_cache = {}

    def prepare(self, queries):
        """Embed many questions in one API request and remember their vectors."""
        vectors = embed(queries, "query", self.env["VOYAGE_API_KEY"])
        self.query_cache.update(zip(queries, vectors))

    def search(self, query, k=5):
        """Return the top k (doc_id, similarity) pairs, best first.
        A document's similarity is that of its closest chunk."""
        if query not in self.query_cache:
            self.query_cache[query] = embed(
                [query], "query", self.env["VOYAGE_API_KEY"])[0]
        query_vector = self.query_cache[query]
        rows = self.conn.execute(
            "SELECT doc_id, min(embedding <=> %s::vector) AS distance "
            "FROM chunks WHERE strategy = %s "
            "GROUP BY doc_id ORDER BY distance LIMIT %s",
            (to_pgvector(query_vector), self.strategy, k),
        ).fetchall()
        return [(doc_id, 1 - distance) for doc_id, distance in rows]
