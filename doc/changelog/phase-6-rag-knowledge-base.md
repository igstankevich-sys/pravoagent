# Phase 6: RAG + Knowledge Base

Дата: 2026-06-25

## Что сделано

- **Chunker** (`rag/chunker.py`) — 4 стратегии чанкования: fixed (N символов + overlap), semantic (по параграфам), recursive (рекурсивно по иерархии разделителей), doc_aware (по заголовкам Глава/Статья/Раздел/§)
- **Embedder** (`rag/embedder.py`) — создание эмбеддингов (mock — детерминированный хеш, 384-dim; E5-small заглушка)
- **BM25Index** (`rag/bm25_index.py`) — текстовый поиск BM25 с хранением raw_documents, k1/b параметры, защита от деления на 0
- **ReRanker** (`rag/re_ranker.py`) — переранжирование результатов гибридного поиска
- **KnowledgeBaseSelector** (`rag/kb_selector.py`) — переключатель источников (own/garant/consultant), гибридный поиск (BM25 + Vector + ReRanker), импорт Embedder/BM25Index/ReRanker
- **KB Router** (`router/knowledge_base.py`) — async эндпоинты `/search`, `/sources`
- **main.py** — подключён `kb_router`

## Файлы (созданы/изменены)

**Созданы:**
- `backend/rag/__init__.py` — пакет rag

**Изменены:**
- `backend/rag/chunker.py` — 4 стратегии чанкования
- `backend/rag/embedder.py` — mock-эмбеддинги, 384-dim
- `backend/rag/bm25_index.py` — BM25 с raw_documents, защита деления на 0
- `backend/rag/re_ranker.py` — переранжирование
- `backend/rag/kb_selector.py` — переключатель БЗ + гибридный поиск
- `backend/router/knowledge_base.py` — async эндпоинты
- `backend/main.py` — подключён kb_router

## Исправления после ревью

1. **[CRITICAL]** `_chunk_recursive` — рекурсивное разбиение по разделителям вместо мёртвого делегирования
2. **[CRITICAL]** Гибридный поиск — KB Selector теперь использует Embedder/BM25Index/ReRanker (добавлен `hybrid_search()`)
3. **[HIGH]** BM25Index — сохранение raw_documents, возврат текста в `search()`, защита деления на 0 при нулевой средней длине документа
4. **[HIGH]** `_chunk_doc_aware` — regex исправлен на корректный паттерн для заголовков Глава/Статья/Раздел/§
5. **[HIGH]** KB Router — переведён на async (`/search`, `/sources`)

## Трудности

- `_chunk_recursive` — рекурсивное разбиение оказалось нетривиальным: первый вариант просто делегировал другим стратегиям вместо настоящей рекурсии по иерархии разделителей. Потребовалось переписать с нуля с явным проходом по уровням.
- `_chunk_doc_aware` — корректный regex для заголовков российских НПА (Глава/Статья/Раздел/§) сложнее, чем кажется: нужно учитывать вариации пробелов, отсутствие точки, смешанный регистр. Первый паттерн не захватывал часть заголовков.
- BM25 — защита от division by zero при пустом корпусе или нулевой средней длине документа не была предусмотрена в первой реализации.
- KB Selector в первой версии не использовал Embedder/BM25Index/ReRanker — гибридный поиск был заглушкой. Потребовался полный рефакторинг `hybrid_search()` для интеграции всех трёх компонентов.
- Embedder — текущая реализация mock (хеш -> 384-dim вектор). Для production потребуется интеграция с E5-small или аналогом, но на этапе прототипа mock-режим позволяет отлаживать пайплайн поиска без внешних зависимостей.

## Статус чеклиста

- [x] 4 стратегии чанкования (fixed, semantic, recursive, doc_aware)
- [x] Embedder (mock, 384-dim)
- [x] BM25 Index (k1=1.5, b=0.75, raw_documents)
- [x] Re-ranker
- [x] Переключатель БЗ (own / garant / consultant)
- [x] Гибридный поиск (BM25 + Vector + ReRanker)
- [x] KB Router (async, /search, /sources)
