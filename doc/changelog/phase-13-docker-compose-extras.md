# Phase 13: Qdrant + Redis в docker-compose

Дата: 2026-06-25

## Что сделано

### Qdrant (vector DB)
- Сервис `qdrant` в docker-compose (qdrant/qdrant:v1.10.0, порты 6333 REST + 6334 gRPC)
- Persistent volume `qdrant_data` для хранения векторов
- Проброшен порт gRPC 6334 (QDRANT__SERVICE__GRPC_PORT)

### Redis (кэш)
- Сервис `redis` в docker-compose (redis:7-alpine, порт 6379)
- Persistent volume `redis_data` для сохранения кэша

### Интеграция с app
- `app.depends_on`: qdrant, redis (порядок запуска)
- `app.environment`: QDRANT_HOST=qdrant, QDRANT_PORT=6333, REDIS_URL=redis://redis:6379/0

### Makefile
- `docker-down-volumes` — остановка + удаление volumes (docker compose down -v)
- `docker-logs` — просмотр логов (docker compose logs -f)
- `docker-ps` — список сервисов (docker compose ps)

### .env
- Добавлены: QDRANT_HOST=qdrant, QDRANT_PORT=6333, REDIS_URL=redis://redis:6379/0

## Файлы (изменены)

- `docker-compose.yml` — добавлены сервисы qdrant, redis + volumes + depends_on + environment
- `Makefile` — добавлены docker-down-volumes, docker-logs, docker-ps
- `.env` — добавлены QDRANT_HOST, QDRANT_PORT, REDIS_URL

## Исправления после ревью

- **OK с первого раза** — все 8 критериев чеклиста выполнены без замечаний

## Статус чеклиста

- [x] docker-compose.yml: qdrant сервис (v1.10.0, порты 6333/6334, volume)
- [x] docker-compose.yml: redis сервис (7-alpine, порт 6379, volume)
- [x] app.depends_on: qdrant, redis
- [x] app.environment: QDRANT_HOST, QDRANT_PORT, REDIS_URL
- [x] Makefile: docker-down-volumes, docker-logs, docker-ps
- [x] .env: QDRANT_HOST, QDRANT_PORT, REDIS_URL
- [x] YAML валидный
