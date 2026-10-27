"""Hybrid retrieval: combine several rankings with Reciprocal Rank Fusion (RRF)."""


class HybridSearch:
    def __init__(self, retrievers, rrf_k=60, depth=20):
        """retrievers: objects with a search(query, k) method, e.g. BM25 and VectorSearch.
        depth: how many results to take from each before fusing."""
        self.retrievers = retrievers
        self.rrf_k = rrf_k
        self.depth = depth

    def prepare(self, queries):
        """Pass batch preparation on to any retriever that supports it."""
        for retriever in self.retrievers:
            if hasattr(retriever, "prepare"):
                retriever.prepare(queries)

    def search(self, query, k=5):
        """Return the top k (doc_id, fused_score) pairs, best first."""
        scores = {}
        for retriever in self.retrievers:
            results = retriever.search(query, k=self.depth)
            for rank, (doc_id, _) in enumerate(results, start=1):
                scores[doc_id] = scores.get(
                    doc_id, 0.0) + 1 / (self.rrf_k + rank)
        ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
        return ranked[:k]
