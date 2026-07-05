# Phase 9: Admin Panel + Budget Control

Дата: 2026-06-25

## Что сделано

- **Admin Router** (`router/admin.py`) — 8 эндпоинтов: users, tenants, audit-logs, health, llm-usage, update_budget, toggle_tenant, toggle_user. Все с `-> dict`, type hints, `Depends(get_db)`. Audit-логирование на трёх мутирующих эндпоинтах.
- **BudgetController** (`services/budget_controller.py`) — проверка лимитов тенанта на основе consumed_tokens / token_limit. Три порога алерта: 80% (warning), 90% (critical), 100% (hard limit — блокировка). Переименован `estimated_cost` в `estimated_tokens`.
- **Model Router** (`agents/model_router.py`) — интеграция BudgetController через метод `can_process()`: перед вызовом LLM проверяется, не превышен ли лимит тенанта.
- **ActionLogger** (`services/action_logger.py`) — логирование админских действий (update_budget, toggle_tenant, toggle_user) с user_id, action, details, timestamp.
- **Auth Service** (`services/auth_service.py`) — проверка `is_active` у пользователя в `require_role()`.
- **Admin workspace** (`workspaces/admin.html`) — шаблон админ-панели.

## Файлы (созданы/изменены)

- `backend/router/admin.py` (создан) — 8 эндпоинтов с audit-логированием, `-> dict`, `Depends(get_db)`, total count
- `backend/services/budget_controller.py` (создан) — трёхпороговый контроль бюджета, hard limit, `estimated_tokens`
- `backend/agents/model_router.py` (изменён) — `can_process()` с BudgetController
- `backend/services/auth_service.py` (изменён) — `is_active` check в `require_role()`
- `backend/main.py` (изменён) — подключён `admin_api_router`

## Исправления после ревью

1. **[CRITICAL]** BudgetController подключён к Model Router через метод `can_process()` — ранее лимиты никак не влияли на вызов LLM.
2. **[CRITICAL]** Hard limit при 100% использовании токенов — вызов LLM блокируется, возвращается 403.
3. **[MEDIUM]** Audit-логирование добавлено на все три мутирующих админ-эндпоинта (update_budget, toggle_tenant, toggle_user).
4. **[MEDIUM]** Type hints `-> dict` добавлены на все 8 эндпоинтов admin router.
5. **[MEDIUM]** `Depends(get_db)` добавлен в `/health`.
6. **[MEDIUM]** `total` count добавлен в пагинированные списки (users, tenants, audit-logs).
7. **[LOW]** Проверка `is_active` добавлена в `require_role()` в auth_service.

## Трудности

- Ревьюер отметил, что без интеграции BudgetController в Model Router лимиты бюджета были декоративными — реальной блокировки при превышении не происходило. Исправлено добавлением `can_process()`.
- Hard limit пришлось реализовывать как исключение в рантайме, а не на уровне middleware, чтобы сохранить контекст тенанта.
- Audit-логирование потребовало согласования формата action details между тремя разными эндпоинтами (update_budget — числовые значения, toggle — булевы статусы).

## Статус чеклиста

- [x] Admin Router (8 эндпоинтов, auth, RBAC)
- [x] Budget Controller (лимиты, алерты 80/90/100, hard limit)
- [x] Model Router интеграция с BudgetController
- [x] Audit логирование админских действий
- [x] Type hints на всех эндпоинтах
- [x] Depends(get_db) в health
- [x] Total count в пагинации
- [x] Проверка is_active в require_role
