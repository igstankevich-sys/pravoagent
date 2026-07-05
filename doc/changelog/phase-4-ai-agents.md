# Phase 4: AI Agents (LangGraph)

Дата: 2026-06-25

## Что сделано

- **LangGraph Orchestrator** (`agents/orchestrator.py`) — StateGraph с 4 узлами (route, select_model, hitl, llm_generate), keyword-based routing (litigation/contracts/general_dept), Human-in-the-loop через AuditLog (неблокирующий), обёртка Orchestrator
- **Model Router** (`agents/model_router.py`) — 3-tier: flash/balance/pro, авто-выбор по сложности, fallback при ошибках, статистика использования, оценка стоимости запроса
- **LLM Contract Layer** (`agents/llm_contract.py`) — LLMConfig + LLMContract с кэшированием ответов (TTL), exponential retry (3 попытки), mock-режим для демо, структурированное логирование
- **6 специализированных агентов:**
  - `litigation/claim_agent.py` — ClaimAgent (анализ претензий)
  - `litigation/lawsuit_agent.py` — LawsuitAgent (сопровождение судебных дел)
  - `litigation/court_calendar.py` — CourtCalendar (календарь заседаний)
  - `contracts/contract_draft.py` — ContractDraftAgent (проектирование договоров)
  - `contracts/contract_review.py` — ContractReviewAgent (ревью договоров)
  - `general_dept/legal_opinion_agent.py` — LegalOpinionAgent (юридические заключения)
- **Agent API** (`router/agent.py`) — POST /api/agent/chat через оркестратор, с AuditLog для HITL-кейсов
- **main.py** (изменён) — подключён `agent_router` (строка 22: `from backend.router.agent import router as agent_router`, строка 57: `app.include_router(agent_router)`)
- **docker-compose.yml** (изменён) — контекст сборки исправлен с `./` на `./ПравоАгент/VPS`
- **requirements.txt** (изменён) — добавлены `langgraph>=0.2.0`, `langchain>=0.3.0`

## Файлы (созданы/изменены)

- `backend/agents/__init__.py` (создан) — пакет agents
- `backend/agents/orchestrator.py` (создан) — LangGraph StateGraph, 4 узла, routing, HITL
- `backend/agents/model_router.py` (создан) — 3-tier model router
- `backend/agents/llm_contract.py` (создан) — LLM contract layer (cache, retry, mock)
- `backend/agents/litigation/__init__.py` (создан)
- `backend/agents/litigation/claim_agent.py` (создан)
- `backend/agents/litigation/lawsuit_agent.py` (создан)
- `backend/agents/litigation/court_calendar.py` (создан)
- `backend/agents/contracts/__init__.py` (создан)
- `backend/agents/contracts/contract_draft.py` (создан)
- `backend/agents/contracts/contract_review.py` (создан)
- `backend/agents/general_dept/__init__.py` (создан)
- `backend/agents/general_dept/legal_opinion_agent.py` (создан)
- `backend/router/agent.py` (создан) — POST /api/agent/chat
- `backend/main.py` (изменён) — подключён agent_router
- `docker-compose.yml` (изменён) — контекст сборки
- `requirements.txt` (изменён) — langgraph, langchain

## Исправления после ревью (критические)

1. **HITL TypeError** — `AuditLog()` получал параметр `created_at`, но модель ожидает `timestamp`. Исправлено: `created_at` -> `timestamp` во всех вызовах `AuditLog()`.
2. **Мёртвые агенты в mock-режиме** — узлы `claim_agent`, `lawsuit_agent`, `court_calendar`, `contract_draft`, `contract_review`, `legal_opinion_agent` не вызывались в `llm_generate_node` — в mock-режиме возвращался placeholder. Добавлены корректные импорты и вызовы всех 6 агентов.
3. **docker-compose context** — путь сборки указывал на корень (`./`), но Dockerfile лежит в `ПравоАгент/VPS/docker/Dockerfile`. Исправлен context на `./ПравоАгент/VPS`.

## Трудности

- LangGraph — первый опыт с StateGraph и conditional edges в проекте; потребовалось время на отладку графа с 4 узлами
- HITL через неблокирующий AuditLog — компромисс: вместо real-time approval (сложно без WebSocket/SSE) запись в лог с последующей возможностью approve/reject
- 6 агентов имеют однотипную структуру (prompt + mock-response), что упрощает код, но требует централизованного шаблона при добавлении новых
- Agent API не защищён middleware (rate limit, CORS) — будет добавлен в фазе деплоя

## Статус чеклиста

- [x] LangGraph StateGraph (4 узла, conditional edges)
- [x] Keyword-based routing (3 агента + default general_dept)
- [x] Human-in-the-loop (AuditLog, неблокирующий)
- [x] Model Router (3-tier: flash/balance/pro)
- [x] LLM Contract Layer (cache, retry, mock, log)
- [x] 6 специализированных агентов (Claim, Lawsuit, CourtCalendar, ContractDraft, ContractReview, LegalOpinion)
- [x] API endpoint POST /api/agent/chat
- [x] Docker-compose с правильным контекстом
- [x] Демо-режим (mock responses через агентов)
