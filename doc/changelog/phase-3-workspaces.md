# Phase 3: Ролевые Workspace

Дата: 2026-06-25

## Что сделано

- **Workspace Service** (`workspace_service.py`) — конфигурация 6 ролевых workspace: litigation, contracts, general, head_legal, admin, legal_opinions. Каждый workspace содержит layout панелей (sidebar/main/right), activity bar, AI-агентов и быстрые действия.
- **Workspace Router** (`router/workspace.py`) — 7 эндпоинтов с префиксом `/app/`:
  - `GET /app/` — редирект на workspace по роли пользователя
  - `GET /app/litigation` — судебный юрист (дела, документы, интеграция КАД)
  - `GET /app/contracts` — договорник (договоры, шаблоны, контрагенты, approval)
  - `GET /app/general` — общий отдел (доверенности, нотариат, НПА, реестры)
  - `GET /app/head-legal` — Head of Legal (дашборд с KPI, статистикой, командой)
  - `GET /app/admin` — админ-панель (пользователи, тенанты, LLM, логи, health)
  - `GET /app/legal-opinions` — юридические заключения (заявки, шаблоны, статистика)
- **Base template** (`templates/base.html`) — базовый layout с подключением CSS/JS
- **6 шаблонов** в `templates/workspaces/`: litigation, contracts, general, head_legal, admin, legal_opinions — кастомный набор панелей под каждую роль
- **RBAC-контроль** — `require_role()` на каждом эндпоинте, мультиролевой доступ (admin имеет доступ ко всем workspace через roles)

## Файлы (созданы/изменены)

- `backend/router/workspace.py` (создан) — 7 эндпоинтов, Jinja2 render_workspace()
- `backend/services/workspace_service.py` (создан) — 6 workspace config + ROLE_TO_WORKSPACE маппинг
- `backend/main.py` (изменён) — подключён workspace_router
- `templates/base.html` (создан) — базовый layout
- `templates/workspaces/litigation.html` (создан) — workspace судебного юриста
- `templates/workspaces/contracts.html` (создан) — workspace договорника
- `templates/workspaces/general.html` (создан) — workspace общего отдела
- `templates/workspaces/head_legal.html` (создан) — workspace Head of Legal
- `templates/workspaces/admin.html` (создан) — админ-панель
- `templates/workspaces/legal_opinions.html` (создан) — workspace юрзаключений

## Исправления после ревью

- Добавлен `legal_opinions` в `ROLE_TO_WORKSPACE` (критический баг — эндпоинт `/app/legal-opinions` падал с 500)
- Убран dead import `sqlalchemy.func` из `workspace.py`
- `HTMLResponse` вынесен в начало файла (из inline-импорта)

## Трудности

- Ревьюер выявил критический баг: workspace `legal_opinions` не был добавлен в маппинг `ROLE_TO_WORKSPACE`, что приводило к 500 ошибке при переходе на `/app/legal-opinions`. Исправлено до мержа.

## Статус чеклиста

- [x] Workspace Service (6 конфигов с panels/activity_bar/agents/actions)
- [x] ROLE_TO_WORKSPACE маппинг (6 ролей)
- [x] 7 эндпоинтов workspace router
- [x] RBAC-контроль на каждом эндпоинте
- [x] Base template + 6 шаблонов workspace
- [x] Jinja2 render_workspace() с общим контекстом (demo_mode, app_name, app_version)
