"""
Embedder - создание эмбеддингов для текстов.
В демо-режиме - простая хеш-функция. В production - E5-small через ONNX.
"""
import hashlib
import numpy as np
from typing import List


class Embedder:
    """Создание эмбеддингов текста."""

    def __init__(self, model_name: str = "mock"):
        self.model_name = model_name
        self.dimension = 384 if model_name == "mock" else 384

    def embed(self, text: str) -> List[float]:
        """Создание эмбеддинга для одного текста."""
        if self.model_name == "mock":
            # Детерминированный эмбеддинг на основе хеша (для демо)
            hash_bytes = hashlib.md5(text.encode()).digest()
            seed = int.from_bytes(hash_bytes[:4], "big")
            rng = np.random.RandomState(seed)
            vector = rng.randn(self.dimension).astype(np.float32)
            vector = vector / np.linalg.norm(vector)
            return vector.tolist()
        else:
            # Здесь будет вызов sentence-transformers
            raise NotImplementedError("Real embedding model not configured")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Создание эмбеддингов для нескольких текстов."""
        return [self.embed(t) for t in texts]
