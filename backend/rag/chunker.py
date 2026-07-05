"""
Chunker - 4 стратегии чанкования текста.
1. Fixed: по N символов с перекрытием
2. Semantic: по параграфам
3. Recursive: рекурсивное разбиение по разделителям
4. Doc-aware: по структуре документа (заголовки, секции)
"""
from typing import List, Dict
import re


class Chunk:
    def __init__(self, text: str, metadata: Dict = None):
        self.text = text
        self.metadata = metadata or {}
        self.embedding = None


class Chunker:
    """Разбиение текста на чанки разными стратегиями."""

    STRATEGIES = ["fixed", "semantic", "recursive", "doc_aware"]

    def chunk(self, text: str, strategy: str = "fixed", **kwargs) -> List[Chunk]:
        if strategy == "fixed":
            return self._chunk_fixed(
                text,
                kwargs.get("chunk_size", 500),
                kwargs.get("overlap", 50),
            )
        elif strategy == "semantic":
            return self._chunk_semantic(text)
        elif strategy == "recursive":
            return self._chunk_recursive(text, kwargs.get("chunk_size", 500))
        elif strategy == "doc_aware":
            return self._chunk_doc_aware(text)
        else:
            return self._chunk_fixed(text, 500, 50)

    def _chunk_fixed(
        self, text: str, chunk_size: int = 500, overlap: int = 50
    ) -> List[Chunk]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(
                Chunk(text[start:end], {"strategy": "fixed", "start": start})
            )
            start += chunk_size - overlap
        return chunks

    def _chunk_semantic(self, text: str) -> List[Chunk]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        return [Chunk(p, {"strategy": "semantic"}) for p in paragraphs]

    def _chunk_recursive(
        self, text: str, chunk_size: int = 500
    ) -> List[Chunk]:
        """Рекурсивное разбиение по иерархии разделителей."""
        if len(text) <= chunk_size:
            return [Chunk(text, {"strategy": "recursive"})]

        separators = ["\n\n", "\n", ". ", "! ", "? ", ", "]
        for sep in separators:
            if sep in text:
                parts = text.split(sep)
                chunks = []
                current = ""
                for part in parts:
                    if len(current) + len(part) + len(sep) <= chunk_size:
                        if current:
                            current += sep + part
                        else:
                            current = part
                    else:
                        if current:
                            chunks.append(Chunk(current.strip(), {"strategy": "recursive"}))
                        current = part
                if current:
                    chunks.append(Chunk(current.strip(), {"strategy": "recursive"}))
                return chunks

        return self._chunk_fixed(text, chunk_size, 0)

    def _chunk_doc_aware(self, text: str) -> List[Chunk]:
        """Разбиение по структуре документа (заголовки)."""
        sections = re.split(
            r'(?=^(?:Глава|Статья|Раздел|§|\d+\.)\s)',
            text,
            flags=re.MULTILINE,
        )
        return [
            Chunk(s.strip(), {"strategy": "doc_aware"})
            for s in sections if s.strip()
        ]
