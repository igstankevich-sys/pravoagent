# Phase 10: Configuration Agent (отложенная часть)

Дата: 2026-06-25

## Что сделано

- **ConfigurationService** (`services/configuration_service.py`) — сервис управления настройками KPI метрик per tenant:
  - `get_kpi_config()` — получение метрик с автосозданием дефолтных при пустоте
  - `update_kpi_config()` — полная замена набора метрик
  - `toggle_kpi_metric()` — включение/выключение видимости метрики
  - `add_custom_metric()` — добавление кастомной метрики
  - `delete_kpi_metric()` — удаление метрики (только кастомные)
  - `create_default_config()` — создание 6 дефолтных метрик (efficiency, users, duration, documents, case-chart, team-table)
- **Configuration Agent Router** (`router/configuration_agent.py`) — 5 эндпоинтов с префиксом `/api/kpi`:
  - `GET /api/kpi/config` — получить конфигурацию (RBAC: head_legal, admin)
  - `PUT /api/kpi/config` — обновить конфигурацию (RBAC: head_legal, admin)
  - `POST /api/kpi/config/metric` — добавить кастомную метрику (RBAC: head_legal, admin)
  - `DELETE /api/kpi/config/metric/{config_id}` — удалить кастомную метрику (RBAC: head_legal, admin)
  - `PATCH /api/kpi/config/metric/{config_id}/toggle` — включить/выключить метрику (RBAC: head_legal, admin)
- **Модель KpiMetricConfig** (`models/base.py`) — SQLAlchemy модель с полями: tenant_id, metric_key, metric_label, metric_description, target_value, comparison, is_custom, formula, is_enabled, sort_order + UniqueConstraint(tenant_id, metric_key)
- **UI Head of Legal** (`templates/workspaces/head_legal.html`) — загрузка конфига с сервера вместо localStorage; отображение target values с иконками достижения цели
- **Seed data** (`seed_data/generate_all.py`) — генерация дефолтных KPI конфигураций для всех тенантов
- **main.py** — подключён config_agent_router

## Файлы (созданы/изменены)

- `backend/services/configuration_service.py` (создан) — ConfigurationService с 7 методами
- `backend/router/configuration_agent.py` (создан) — 5 эндпоинтов, Pydantic схемы, RBAC
- `backend/models/base.py` (изменён) — добавлена модель KpiMetricConfig + UniqueConstraint
- `backend/main.py` (изменён) — подключён config_agent_router
- `templates/workspaces/head_legal.html` (изменён) — серверная загрузка конфига, target values
- `backend/seed_data/generate_all.py` (изменён) — генерация дефолтных KPI конфигураций

## Исправления после ревью

- **[CRITICAL]** Cross-tenant vulnerability — `toggle_kpi_metric()` и `delete_kpi_metric()` не проверяли `tenant_id`. Добавлен параметр `tenant_id` и фильтр в запрос.
- **[CRITICAL]** `KpiConfigResponse.metric_description` объявлен как `str` вместо `Optional[str]` — мог вызвать 500 при None. Исправлен тип поля.
- **[MEDIUM]** Добавлен `UniqueConstraint("tenant_id", "metric_key")` в модель для предотвращения дублей метрик внутри тенанта.
- **[MEDIUM]** Приватный метод `_create_default_config` переименован в публичный `create_default_config` для вызова из seed_data.

## Трудности

- Cross-tenant защита была упущена в первой реализации на методах `toggle` и `delete` — исправлено после ревью. Это критический паттерн для всех write-эндпоинтов в мультитенантной архитектуре.

## Статус чеклиста

- [x] GET /api/kpi/config — возвращает метрики (дефолтные при пустоте)
- [x] PUT /api/kpi/config — обновление метрик
- [x] PATCH /api/kpi/config/metric/{id}/toggle — включение/выключение
- [x] DELETE /api/kpi/config/metric/{id} — удаление кастомных
- [x] POST /api/kpi/config/metric — добавление кастомных
- [x] UI загружает конфиг с сервера (убрана localStorage)
- [x] Seed data генерирует конфигурации
- [x] Cross-tenant защита на PATCH и DELETE
- [x] RBAC на всех эндпоинтах
