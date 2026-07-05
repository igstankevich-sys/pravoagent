# ПравоАгент - Multi-Agent AI Platform для юридических департаментов

## Что это
Прототип для работодателя PravoTech. Платформа для юридического департамента:
мультиагентная AI-система (Litigation / Contracts / General dept), встроенная в
полный цикл - от заявки до судебного акта, от черновика до подписанного договора.
Мультитенантная (tenant_id), с model-router (DeepSeek/OpenAI/Ollama), RAG, экспортом.

## Стек
- **Backend:** FastAPI (async) + Python 3.12, Pydantic v2 / pydantic-settings, SQLAlchemy 2.0.
- **AI:** LangGraph (оркестратор) + langchain, model-router с tier'ами `flash|balance|pro`
  (DeepSeek / OpenAI / Ollama), sentence-transformers для эмбеддингов.
- **UI:** HTMX + Alpine.js + Jinja2 (НЕ React). Серверный рендеринг.
- **Data:** SQLite (WAL) для прототипа. Qdrant v1.10.0 (векторы). Redis 7 (кеш/очереди).
- **Экспорт:** python-docx (.docx), weasyprint (.pdf).
- **Интеграции:** Telegram-бот (отдельный микросервис + webhook).
- **Инфра:** Docker Compose на VPS (Ubuntu 24.04). ssh-alias `adminvps` (root@157.22.173.65).

## Структура
```
backend/
  main.py              # FastAPI app, 15 роутеров
  config.py            # Settings (pydantic-settings, .env)
  database.py
  models/              # SQLAlchemy + Pydantic
  router/              # cases, documents, agent, auth, workspace, kb,
                       # integrations, settings_api_keys, observability,
                       # kpi, admin_api, landing, telegram_webhook, config_agent
  services/            # export, sharing, budget, action_logger, telegram, ...
  agents/
    litigation/        # claim, lawsuit, court_calendar
    contracts/         # contract_draft, contract_review
    general_dept/      # legal_opinion
    orchestrator.py    # LangGraph
    model_router.py    # flash/balance/pro
    llm_contract.py    # LLM Contract Layer
    rules/             # prompts, checklists, memory
  rag/                 # embedder, chunker, re_ranker, bm25_index, kb_selector
  seed_data/           # generate_all
  eval/
templates/             # Jinja2
static/css/            # tokens.css (design tokens), components/, layouts/
docker/Dockerfile
docker-compose.yml
Makefile
doc/changelog/         # прогресс по фазам (см. ниже)
```

## Дорожная карта и текущее состояние
Прогресс по фазам 2-13 зафиксирован в `doc/changelog/` (panel-auth, workspaces,
ai-agents, document-engine, rag, integrations, admin-panel, config-agent, kpi,
observability, onboarding, nginx/docker/vps-migration, landing-deploy).
**Текущий фокус:** переход из `DEMO_MODE` (mock-ответы LLM) на реальную LLM и
продакшенизация. Полный изначальный план - в родительском репо
`Вакансии/ПравоАгент/План_прототипа.md`.

## Команды (см. Makefile)
```
make install     # venv + зависимости
make run         # uvicorn --reload (локально)
make test        # pytest
make lint        # ruff check
make format      # ruff format
make seed        # тестовые данные в локальную SQLite
make deploy      # git push -> VPS -> docker compose up -d --build -> health
make logs        # логи приложения на VPS
make ssh         # ssh adminvps
make health      # health-check VPS
make prune       # чистка docker-кеша на VPS (диск!)
```

## Переменные окружения (`.env`, НЕ коммитить)
См. `.env.example`. Ключевые: `DEMO_MODE` (true=mock LLM), `SECRET_KEY`,
`JWT_SECRET_KEY` (обязательно сменить!), `DATABASE_URL`, `QDRANT_HOST/PORT`,
`REDIS_URL`, `DEEPSEEK_API_KEY`/`OPENAI_API_KEY`, `DEFAULT_MODEL_TIER`.

## Жёсткие правила
- **Код правится только в локальном клоне** (`~/projects/pravoagent`). VPS `/opt/pravoagent` -
  deploy-клон (pull через `git push` + `receive.denyCurrentBranch=updateInstead`).
- **Мультитенантность (ADR-004):** каждый запрос к tenant-данным фильтруется по `tenant_id`
  из сессии, НЕ из body. Нарушение = критическая уязвимость.
- `.env`, `data/*.db`, `static/uploads/`, `data/exports/` - НИКОГДА в git.
- **Дизайн (enterprise, не "AI-vibe"):** цвета ТОЛЬКО из `static/css/tokens.css`
  (`--color-primary: #8c26ea`, `--color-secondary: #eeff2d`). Не хардкодить hex.
  Panel system как IDE. Доступность (aria-), адаптив (CSS Grid).
- Заглушки (`raise NotImplementedError`, mock_*, `...`-тела) - только с пометкой
  "FLAGGING FOR REVIEW" и планом закрытия.

## Цикл разработки (серьёзный, не "на коленке")
1. **plan** - `/plan` или EnterPlanMode: архитектура без кода
2. **build** - workflow `build-feature` (backend-dev + frontend-dev параллельно)
3. **verify** - `/verify` (end-to-end прогон)
4. **review** - `/code-review` (всегда) + `/security-review` (обязательно для tenant-data/auth/agent)
5. **deploy** - `make deploy` (только после verify + review)

## Где что искать
- Архитектурные решения: см. doc/changelog/ + родительский `.cursor/rules/adr-pravoagent.mdc`
- Дизайн-токены: `static/css/tokens.css`
- Прогресс по фазам: `doc/changelog/`
- Статус VPS: `doc/VPS_STATUS.md`
