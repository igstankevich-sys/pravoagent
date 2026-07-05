"""
Алиас для обратной совместимости.
Knowledge Base Selector переехал в backend/rag/kb_selector.py
"""
from backend.rag.kb_selector import KnowledgeBaseSelector

__all__ = ["KnowledgeBaseSelector"]
