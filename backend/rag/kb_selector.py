"""
Knowledge Base Selector - переключатель источников знаний.
Часть Part 12.3 плана.
"""
from typing import List, Dict

from backend.rag.embedder import Embedder
from backend.rag.bm25_index import BM25Index
from backend.rag.re_ranker import ReRanker


class KnowledgeBaseSelector:
    """Переключатель баз знаний с гибридным поиском."""

    SOURCES = {
        "own": {
            "type": "qdrant",
            "collection": "own_docs",
            "real": True,
            "name": "Собственная база",
        },
        "garant": {
            "type": "mock",
            "endpoint": "/api/garant",
            "real": False,
            "name": "Гарант",
        },
        "consultant": {
            "type": "mock",
            "endpoint": "/api/consultant",
            "real": False,
            "name": "Консультант+",
        },
    }

    def __init__(self, embedder=None, bm25_index=None, re_ranker=None):
        self.embedder = embedder or Embedder()
        self.bm25_index = bm25_index or BM25Index()
        self.re_ranker = re_ranker or ReRanker()
        self.documents = []  # для BM25

    def add_document(self, text: str) -> None:
        """Добавить документ в индекс BM25."""
        self.bm25_index.add_document(text)
        self.documents.append(text)

    async def search(
        self,
        query: str,
        sources: List[str] = None,
        top_k: int = 5,
    ) -> Dict:
        """Поиск по выбранным источникам."""
        if sources is None:
            sources = ["own"]

        all_results = []
        for source in sources:
            config = self.SOURCES.get(source)
            if not config:
                continue
            if config["type"] == "qdrant":
                results = await self._search_qdrant(
                    query, config["collection"], top_k
                )
            elif config["type"] == "mock":
                results = self._search_mock(query, config["name"], top_k)
            else:
                results = []
            for r in results:
                r["source"] = source
                r["source_name"] = config["name"]
            all_results.extend(results)

        if all_results:
            all_results = self.re_ranker.rerank(query, all_results)

        return {
            "query": query,
            "sources": sources,
            "results": sorted(
                all_results, key=lambda x: x.get("score", 0), reverse=True
            )[:top_k],
            "total": len(all_results),
        }

    async def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Гибридный поиск: BM25 + Vector + Re-ranker."""
        bm25_results = self.bm25_index.search(query, top_k)
        vector_results = await self._search_qdrant(query, "own_docs", top_k)

        # Слияние результатов
        seen = set()
        combined = []
        for r in bm25_results + vector_results:
            text = r.get("text", "")
            if text not in seen:
                seen.add(text)
                combined.append(r)

        combined = self.re_ranker.rerank(query, combined)
        return combined[:top_k]

    async def _search_qdrant(
        self, query: str, collection: str, top_k: int
    ) -> List[Dict]:
        """Поиск в Qdrant (заглушка для демо)."""
        return [
            {"text": f"[ДЕМО] Результат из {collection}", "score": 0.95}
        ]

    def _search_mock(
        self, query: str, source_name: str, top_k: int
    ) -> List[Dict]:
        """Поиск в мок-источнике."""
        return [
            {
                "text": f"[ДЕМО-{source_name}] Результат по запросу: {query}",
                "score": 0.85,
            }
        ]
