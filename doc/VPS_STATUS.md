# VPS Status - ПравоАгент

## Развёртывание
- **Сервер:** 157.22.173.65 (ssh-alias: `adminvps` = root@157.22.173.65)
- **Директория:** `/opt/pravoagent` (deploy-clone репозитория; origin = сам репозиторий,
  `receive.denyCurrentBranch=updateInstead` обновляет working tree при `git push`).
- **Домен:** https://pravoagent.igor-stankevich.ru (self-signed SSL, nginx reverse proxy -> :8000)
- **Запуск:** Docker Compose (services: `app`, `qdrant:v1.10.0`, `redis:7-alpine`)
- **Статус:** обновляется при каждом `make deploy` (выводит health-check)

## Команды (с локальной машины)
```bash
make deploy      # git push -> VPS -> docker compose up -d --build -> health
make logs        # логи приложения на VPS (tail -f)
make health      # health-check
make ssh         # ssh adminvps
make prune       # чистка docker build-cache (диск!)
```

## Проверка вручную
```bash
ssh adminvps 'cd /opt/pravoagent && docker compose ps'
ssh adminvps 'curl -fsS http://localhost:8000/health'    # {"status":"ok",...}
ssh adminvps 'cd /opt/pravoagent && docker compose logs --tail=200 app'
```

## Известные ограничения
- `DEMO_MODE=true` (mock-ответы LLM). Для реальной работы - заполнить `.env`
  (`DEEPSEEK_API_KEY`/`OPENAI_API_KEY`) и выставить `DEMO_MODE=false`.
- SQLite (прототип). Production - PostgreSQL.
- VPS диск ~90% заполнен (8 ГБ свободно). Регулярно `make prune`.

## Ресурсы VPS (на момент настройки)
- Ubuntu 24.04.4 LTS, 4 CPU, 7.8 ГБ RAM, диск 79 ГБ (свободно ~8 ГБ).
- Docker 29.5.0, Docker Compose v5.1.3.
- На сервере также работают другие проекты (msghub, tgcontent) - не трогать их контейнеры.

## Деплой-флоу
```
~/projects/pravoagent (локальная разработка)
   |  git push origin main
   v
adminvps:/opt/pravoagent  (working tree обновляется автоматически)
   |  docker compose up -d --build
   v
http://localhost:8000  (внутри контейнера app; nginx -> 80/443 снаружи)
```
