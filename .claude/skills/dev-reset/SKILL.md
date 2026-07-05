---
name: dev-reset
description: Сброс локальной dev-БД ПравоАгент к seed-данным. Удаляет SQLite, перегенерирует seed, перезапускает uvicorn. Используй для чистого демо-состояния.
---

# dev-reset

Локально (в корне проекта `~/projects/pravoagent`):

1. Остановить запущенный uvicorn (Ctrl+C в `make run`).
2. Удалить локальную БД и артефакты:
   ```bash
   rm -f data/pravoagent.db data/pravoagent.db-wal data/pravoagent.db-shm
   rm -rf data/uploads/* data/exports/*
   ```
   (или `make clean`)
3. Перегенерировать seed:
   ```bash
   make seed    # python -m backend.seed_data.generate_all
   ```
4. Перезапустить:
   ```bash
   make run
   ```

## VPS-сброс (ОСТОРОЖНО - это прод/demo-данные для работодателя!)
Только если явно запрошено. Бэкапить перед:
```bash
ssh adminvps 'cp /opt/pravoagent/data/pravoagent.db /opt/pravoagent/data/pravoagent.db.bak.$(date +%F)'
ssh adminvps 'cd /opt/pravoagent && docker compose exec app python -m backend.seed_data.generate_all'
```
Сообщить пользователю, что VPS-данные сброшены.
