# Phase 13: VPS Migration — Переезд на production-инфраструктуру

Дата: 2026-06-25

## Что сделано

- **VPS deployment** — прототип перенесён на VPS (157.22.173.65), развёрнут в `/opt/pravoagent` через SSHFS-монтирование в `ПравоАгент/VPS/`
- **Docker Compose** — 4 сервиса в production-режиме:
  - `pravoagent-app-1` — FastAPI (uvicorn, порт 8000)
  - `pravoagent-nginx-1` — nginx:alpine (reverse proxy, порты 80/443)
  - `pravoagent-qdrant-1` — qdrant/qdrant:v1.10.0 (vector database)
  - `pravoagent-redis-1` — redis:7-alpine (кэш)
- **Seed data** — сгенерирована на VPS: 3 тенанта, 6 пользователей, 8 дел, документы, 10 юрзаключений, 15 заявок, KPI за 3 месяца, 550+ audit логов
- **SSL сертификаты** — сгенерированы (самоподписанные через `docker/ssl/generate-ssl.sh`)
- **Проверка эндпоинтов** — все ключевые эндпоинты протестированы (health, kpi, landing, onboarding, auth)
- **Makefile seed fix** — исправлен путь выполнения (убран лишний `cd ПравоАгент/VPS &&`)
- **Seed passwords fix** — пароли seed-пользователей переведены с `demo_hash` на bcrypt-хэш от `demo123` для возможности логина

## Файлы (изменены)

| Файл | Изменение |
|---|---|
| `backend/seed_data/generate_all.py` | Пароли seed-пользователей заменены с `demo_hash` на bcrypt-хэш от `demo123` |
| `Makefile` | Команда `seed` исправлена: убран `cd ПравоАгент/VPS &&`, теперь `python -m backend.seed_data.generate_all` |
| `.env` | `DEBUG=false` (production-режим) |

## Проверка эндпоинтов

- `GET /health` — 200 OK (database connected, demo mode)
- `GET /api/kpi/dashboard` — возвращает метрики (RBAC: head_legal, admin)
- `GET /api/kpi/config` — 6 дефолтных метрик с target values
- `GET /landing` — 200 OK
- `GET /onboarding` — 200 OK
- `POST /api/auth/register` — работает (регистрация нового пользователя)
- `POST /api/auth/login` — возвращает JWT access + refresh токены

## Исправления после ревью

OK с первого раза. Проверено на VPS.

## Инфраструктура

- VPS: 157.22.173.65 (adminvps, OpenCLOUD)
- Docker: v29 + compose v5
- Python: 3.12.3
- nginx: системный + Docker nginx (reverse proxy)
- SSHFS: монтирование VPS `/opt/pravoagent` в локальную папку `ПравоАгент/VPS/`

## Статус чеклиста

- [x] Seed data сгенерирована на VPS
- [x] Docker Compose запущен (4 сервиса: app, nginx, qdrant, redis)
- [x] Health endpoint 200
- [x] KPI Dashboard возвращает данные
- [x] SSL сертификаты сгенерированы
- [x] nginx настроен (через Docker nginx и/или системный nginx)
- [x] Makefile seed команда исправлена
- [x] .env обновлён (DEBUG=false)
- [x] Seed passwords исправлены на bcrypt
- [x] Landing и Onboarding страницы работают
