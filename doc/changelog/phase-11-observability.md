# Phase 11: Observability + Audit Log

Дата: 2026-06-25

## Что сделано

- **Observability Router** (`router/observability.py`) — 3 эндпоинта: `GET /api/observability/audit-logs` (с фильтрацией action, user_id, tenant-scoped), `GET /api/observability/stats` (total_logs, unique_users, action_counts), `POST /api/observability/evals/run`. RBAC: admin + head_legal для audit-logs и stats, admin для evals.
- **ActionLogger** (`services/action_logger.py`) — сервис логирования всех действий пользователей. Параметры: user_id, user_name, role, action, entity_type, entity_id, details, tenant_id, ip_address, session_id. Google-style docstring.
- **EvalSuite** (`eval/eval_suite.py`) — 3 теста (accuracy, completeness, harmlessness), run_all с корректной очисткой self.results и подсчётом passed по собственной метрике каждого теста.
- **AuditLog модель** (`models/base.py`) — поля: timestamp, user_id, user_name, tenant_id, role, action, entity_type, entity_id, details, ip_address, session_id.
- **main.py** — подключён observability_router.

## Исправления после ревью

1. **[CRITICAL]** ActionLogger — добавлены параметры user_name, role, ip_address, session_id (изначально отсутствовали)
2. **[CRITICAL]** Response audit-logs — добавлены поля role, tenant_id, ip_address, session_id (не возвращались клиенту)
3. **[CRITICAL]** EvalSuite.run_all — self.results = [] в начале (защита от накопления результатов между вызовами)
4. **[CRITICAL]** EvalSuite.run_all — passed считает по собственной метрике каждого теста (раньше был общий threshold)
5. **[CRITICAL]** Tenant-scoped фильтрация для head_legal в get_audit_logs и get_stats (head_legal видит только свои tenant_id)

## Файлы (созданы/изменены)

- `backend/services/action_logger.py` (создан) — сервис логирования с Google-style docstring
- `backend/router/observability.py` (создан) — 3 эндпоинта observability
- `backend/eval/eval_suite.py` (создан) — EvalSuite с accuracy, completeness, harmlessness
- `backend/models/base.py` (изменён) — добавлена AuditLog модель
- `backend/main.py` (изменён) — подключён observability_router

## Статус чеклиста

- [x] Observability Router (audit-logs, stats, evals)
- [x] ActionLogger (все поля: user_name, role, ip_address, session_id)
- [x] EvalSuite (accuracy, completeness, harmlessness, корректный подсчёт)
- [x] Tenant-scoped доступ для head_legal
- [x] RBAC (admin + head_legal для audit, admin для evals)
- [x] AuditLog модель (все поля)
