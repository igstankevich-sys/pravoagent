# Phase 10: KPI Dashboard

Дата: 2026-06-25

## Что сделано

- **KPIService** (`services/kpi_service.py`) — расчёт метрик дашборда Head of Legal: total/open/closed cases, efficiency (по формуле `(closed_cases * 0.7 / closed_cases) * 100`), load_pct, avg_duration_days (по реальным датам из БД), team_members с нагрузкой. Google-style docstring.
- **KPI Router** (`router/kpi.py`) — `GET /api/kpi/dashboard`, RBAC (head_legal, admin), type hints -> dict.
- **KpiEntry** (`models/base.py`) — модель для хранения истории KPI (tenant_id, date, metric_name, metric_value).
- **Seed data** (`seed_data/generate_all.py`) — генерация KPI истории за 3 месяца (12 недель), 5 метрик.
- **main.py** — подключён kpi_router.

## Исправления после ревью

- **[#A]** efficiency — от хардкода к расчёту по формуле `(closed_cases * 0.7 / closed_cases) * 100`
- **[#B]** Убран `import random`, member_load при 0 дел = 0, avg_duration_days по реальным датам
- **[#C]** Google-style docstring для KPIService и get_dashboard
- **[#D]** Type hint -> dict на kpi_dashboard

## Отложено

- **Configuration Agent** — вынесен на отдельный этап (не входит в Phase 10)

## Файлы (созданы/изменены)

- `backend/services/kpi_service.py` (создан) — efficiency расчёт, Google-style docstring
- `backend/router/kpi.py` (создан) — GET /api/kpi/dashboard, -> dict
- `backend/models/base.py` (изменён) — добавлен KpiEntry
- `backend/seed_data/generate_all.py` (изменён) — генерация KPI истории
- `backend/main.py` (изменён) — подключён kpi_router

## Статус чеклиста

- [x] KPIService (efficiency, load, duration, team_members)
- [x] KPI Router (GET /api/kpi/dashboard, RBAC)
- [x] KpiEntry модель (tenant_id, date, metric_name, metric_value)
- [x] Seed data (3 месяца истории)
- [ ] Configuration Agent (отложен)
