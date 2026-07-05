"""
BM25 Index - текстовый поиск для гибридного retrieval.
"""
from typing import List, Dict
import math
from collections import Counter
import re


class BM25Index:
    """BM25 индекс для текстового поиска."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents = []
        self.raw_documents: List[str] = []
        self.avg_doc_len = 0
        self.doc_freq = {}
        self.total_docs = 0

    def add_document(self, text: str):
        tokens = self._tokenize(text)
        self.documents.append(tokens)
        self.raw_documents.append(text)
        self.total_docs = len(self.documents)
        self.avg_doc_len = sum(len(d) for d in self.documents) / max(self.total_docs, 1)
        # Update doc frequency
        for token in set(tokens):
            self.doc_freq[token] = self.doc_freq.get(token, 0) + 1

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_tokens = self._tokenize(query)
        scores = []
        for i, doc_tokens in enumerate(self.documents):
            score = self._score(query_tokens, doc_tokens)
            scores.append((i, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [
            {
                "doc_index": i,
                "score": s,
                "text": self.raw_documents[i] if i < len(self.raw_documents) else "",
            }
            for i, s in scores[:top_k] if s > 0
        ]

    def _score(
        self, query_tokens: List[str], doc_tokens: List[str]
    ) -> float:
        score = 0
        doc_len = len(doc_tokens)
        for token in query_tokens:
            if token in self.doc_freq:
                idf = math.log(
                    1
                    + (self.total_docs - self.doc_freq[token] + 0.5)
                    / (self.doc_freq[token] + 0.5)
                )
                tf = doc_tokens.count(token)
                score += (
                    idf
                    * (tf * (self.k1 + 1))
                    / (
                        tf
                        + self.k1
                        * (1 - self.b + self.b * doc_len / self.avg_doc_len)
                    )
                )
        return score

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"[а-яёa-z]+", text.lower())
        return words
