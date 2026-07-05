"""
Re-ranker - переранжирование результатов поиска.
"""
from typing import List, Dict


class ReRanker:
    """Переранжирование результатов поиска."""

    def rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """Переранжирование (в демо - без изменений)."""
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)
