"""Keyword retrieval with BM25, written by hand as a baseline."""
import math
import re
from collections import Counter


def tokenize(text):
    """Lowercase words and numbers: 'Dark Patch (216)' -> ['dark', 'patch', '216']."""
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        """docs is a list of (doc_id, text) pairs."""
        self.k1, self.b = k1, b
        self.ids = [doc_id for doc_id, _ in docs]
        self.term_counts = [Counter(tokenize(text)) for _, text in docs]
        self.lengths = [sum(counts.values()) for counts in self.term_counts]
        self.avg_length = sum(self.lengths) / len(self.lengths)

        # how many documents contain each word
        doc_freq = Counter()
        for counts in self.term_counts:
            doc_freq.update(counts.keys())

        n = len(docs)
        self.idf = {term: math.log((n - df + 0.5) / (df + 0.5) + 1)
                    for term, df in doc_freq.items()}

    def score(self, query_terms, i):
        """BM25 score of document i for a list of query words."""
        counts, length = self.term_counts[i], self.lengths[i]
        total = 0.0
        for term in query_terms:
            tf = counts.get(term, 0)
            if tf == 0:
                continue
            length_factor = 1 - self.b + self.b * length / self.avg_length
            total += self.idf[term] * tf * \
                (self.k1 + 1) / (tf + self.k1 * length_factor)
        return total

    def search(self, query, k=5):
        """Return the top k (doc_id, score) pairs, best first."""
        terms = tokenize(query)
        scored = [(self.ids[i], self.score(terms, i))
                  for i in range(len(self.ids))]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]
