# ПравоАгент

Multi-Agent AI Platform для юридических департаментов. Прототип для PravoTech.

FastAPI + LangGraph + HTMX/Alpine + SQLite + Qdrant + Redis. Мультитенантная,
с model-router (DeepSeek/OpenAI/Ollama), RAG, экспортом документов.

## Требования
- **Локально:** Python 3.12, git, make. (Docker опционален - только для полного локального стека.)
- **VPS:** Ubuntu 24.04, Docker 29+, docker compose v2+. Доступ по ssh-alias `adminvps`.

## Быстрый старт (локально)
```bash
cp .env.example .env          # заполнить SECRET_KEY, JWT_SECRET_KEY, DEEPSEEK_API_KEY
make install                  # venv + зависимости
make seed                     # тестовые данные в SQLite
make run                      # http://127.0.0.1:8000
```
Health: `curl http://127.0.0.1:8000/health` -> `{"status":"ok"}`.

## Основные команды (`make help` - полный список)
| Команда | Действие |
|---|---|
| `make install` | venv + зависимости |
| `make run` | uvicorn dev-сервер (--reload) |
| `make test` | pytest |
| `make lint` / `make format` | ruff |
| `make seed` | тестовые данные в локальную SQLite |
| `make deploy` | git push -> VPS -> docker compose up -d --build -> health |
| `make logs` | логи приложения на VPS |
| `make ssh` | ssh adminvps |
| `make health` | health-check VPS |
| `make prune` | чистка docker build-cache на VPS (диск!) |

## Деплой
Код разрабатывается в локальном клоне (`~/projects/pravoagent`).
`make deploy` пушит на VPS (origin = `adminvps:/opt/pravoagent`), VPS обновляет
working tree (`receive.denyCurrentBranch=updateInstead`), пересобирает контейнеры
и гоняет health-check. Один командная деплой.

Домен: `https://pravoagent.igor-stankevich.ru` (self-signed SSL, см. `make ssl` на VPS).

## Архитектура
- 15 роутеров: cases, documents, agent, auth, workspace, kb, integrations,
  settings_api_keys, observability, kpi, admin_api, landing, telegram_webhook, config_agent.
- AI: LangGraph-оркестратор + 3 роли агентов (litigation/contracts/general_dept),
  model-router с tier'ами `flash|balance|pro`, LLM Contract Layer.
- ADR: LangGraph, HTMX (не React), SQLite (demo, PostgreSQL в prod), shared DB + tenant_id,
  ключи в .env, Telegram отдельным микросервисом, экспорт python-docx + weasyprint.

Подробнее: `CLAUDE.md` (для Claude Code), `doc/changelog/` (прогресс по фазам).

## Переменные окружения
См. `.env.example`. `.env` НИКОГДА не коммитится.

## Разработка с Claude Code
Конфиг Claude Code живёт в `.claude/` (агенты, скиллы, workflow). Цикл:
`/plan` -> workflow `build-feature` -> `/verify` -> `/code-review` -> `/security-review` -> `make deploy`.
См. `CLAUDE.md` в корне.

## Статус
Прототип, `DEMO_MODE=true` (mock-ответы LLM). Фокус - переход на реальную LLM + продакшенизация.
VPS статус: `doc/VPS_STATUS.md`.
