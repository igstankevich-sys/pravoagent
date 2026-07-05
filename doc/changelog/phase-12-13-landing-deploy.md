# Phase 12 + 13: Landing, Onboarding и Deploy

Дата: 2026-06-25

## Что сделано

### Phase 12 — Landing + Onboarding

- **Landing Router** (`router/landing.py`) — эндпоинты `GET /landing` и `GET /onboarding`
- **Landing Template** (`templates/landing.html`) — hero-секция с УТП ПравоАгент, features (5 карточек), architecture diagram, роли (4 карточки), CTA, demo-badge, spot-эффекты
- **Onboarding Template** (`templates/onboarding.html`) — 4-шаговый welcome-тур с прогресс-баром и навигацией (Previous/Next/Finish)
- **Landing CSS** (`static/landing.css`) — полный набор стилей: :root с CSS-переменными, навигация, hero с градиентом, секции, spot-эффекты, адаптивность
- **Landing JS** (`static/landing.js`) — файл-заглушка для будущих скриптов
- **Demo Banner** (`templates/base.html`) — баннер "ДЕМО-РЕЖИМ: Это прототип — часть портфолио кандидата Станкевича Игоря" на всех страницах
- **main.py** — подключён `landing_router`

### Phase 13 — Deploy

- **Dockerfile** (`docker/Dockerfile`) — сборка Python-образа на slim-bookworm, установка зависимостей, копирование кода, healthcheck
- **Docker Compose** (`docker-compose.yml`) — сервис app с контекстом `./ПравоАгент/VPS`, volumes, env, порт 8000
- **requirements.txt** — финальный список всех зависимостей (fastapi, uvicorn, sqlalchemy, langgraph, qdrant-client, openai, redis и др.), удалена мёртвая зависимость pandoc
- **Makefile** — полный набор команд: help, install, run, seed (`cd ПравоАгент/VPS && python -m backend.seed_data.generate_all`), docker-up, docker-down, deploy
- **.env** — конфигурация окружения: JWT, DB, API keys (OpenAI, Qdrant, Telegram), demo-mode

## Файлы (созданы/изменены)

**Созданы:**
- `backend/router/landing.py` — 2 эндпоинта (/landing, /onboarding)
- `templates/landing.html` — лэндинг с hero, features, architecture, roles, CTA
- `templates/onboarding.html` — 4-шаговый welcome-тур
- `static/landing.css` — стили лэндинга с :root, spot-эффектами, адаптивностью
- `static/landing.js` — файл-заглушка
- `docker/Dockerfile` — сборка образа

**Изменены:**
- `static/landing.css` — добавлены недостающие CSS-переменные (:root с --radius-full, --transition-fast, --transition-base)
- `Makefile` — исправлен путь seed на `cd ПравоАгент/VPS && python -m backend.seed_data.generate_all`
- `requirements.txt` — удалён pandoc
- `docker-compose.yml` — контекст изменён на `./ПравоАгент/VPS` (исправление Phase 4)
- `backend/main.py` — подключён landing_router

## Исправления после ревью

1. **[CRITICAL]** `static/landing.css` — отсутствовал блок `:root` с CSS-переменными (`--radius-full`, `--transition-fast`, `--transition-base`), что приводило к некорректному отображению скруглений и анимаций. Добавлен блок `:root` с полным набором токенов.
2. **[CRITICAL]** `Makefile` — команда `seed` указывала неверный путь `backend/seed_data/`, что приводило к `ModuleNotFoundError`. Исправлено на `cd ПравоАгент/VPS && python -m backend.seed_data.generate_all`.
3. **[MEDIUM]** `static/landing.js` — файл отсутствовал, хотя был указан в `landing.html`. Создан файл-заглушка во избежание 404.
4. **[MEDIUM]** `requirements.txt` — содержал мёртвую зависимость `pandoc`, не используемую в проекте. Удалена.

## Трудности

- Ревьюер обнаружил критический баг в `landing.css` — отсутствие `:root` с CSS-переменными делало стили неработоспособными. Проблема возникла из-за того, что Worker при копировании кода из плана пропустил блок `:root`, сосредоточившись на селекторах `.landing-hero`, `.landing-features` и т.д.
- Makefile seed указывал относительный путь от корня репозитория, а не от `ПравоАгент/VPS`, из-за чего команда падала с ошибкой импорта. Исправлено после ревью.
- Docker Compose использовал контекст `.` вместо `./ПравоАгент/VPS` (ошибка из Phase 4), исправлено в рамках Phase 13.

## Отложено

- Онбординг с 6 шагами и видео-туром (расширение onboarding)
- Qdrant + Redis в docker-compose
- nginx + .dockerignore

## Статус чеклиста

- [x] Landing page (hero, features, architecture, roles, CTA)
- [x] Demo-banner на всех страницах
- [x] Landing CSS + JS
- [x] Onboarding (welcome-тур)
- [x] Dockerfile
- [x] Docker Compose
- [x] requirements.txt (чистые зависимости)
- [x] Makefile (help, install, run, seed, docker-up, docker-down, deploy)
