---
name: deploy
description: Деплой ПравоАгент на VPS одной командой. Пушит текущую ветку, обновляет working tree на VPS, пересобирает контейнеры, гоняет health-check. Используй когда изменения готовы к VPS.
---

# deploy

Команда: `make deploy` (предпочтительно). Эквивалентные шаги вручную:

1. Локально: закоммитить + запушить (если есть незакоммиченные изменения).
   ```bash
   [ -n "$(git status --porcelain)" ] && git add -A && git commit -m "deploy: $(date +%FT%T)"
   git push origin main
   ```
2. На VPS (origin = `adminvps:/opt/pravoagent`, `receive.denyCurrentBranch=updateInstead` обновит working tree):
   ```bash
   ssh adminvps 'cd /opt/pravoagent && docker compose up -d --build'
   ```
3. Health-check:
   ```bash
   ssh adminvps 'curl -fsS http://localhost:8000/health'   # ожидать {"status":"ok"}
   ```

## При провале health-check
```bash
ssh adminvps 'cd /opt/pravoagent && docker compose logs --tail=200 app'
```
Сообщить ошибку пользователю, НЕ пытаться "исправить" вслепую на VPS без диагностики.

## Условия
- Рабочая директория: локальный клон `~/projects/pravoagent`.
- Ветка: `main` (или убедиться, что VPS на той же ветке).
- ОБЯЗАТЕЛЬНО до деплоя: `/verify` + `/code-review` (+ `/security-review` если затронуты tenant-data/auth/agent).
- На VPS мало места (8 ГБ): при `no space left` - `make prune` и повторить.

## Никогда
- Не деплоить с незакоммиченными заглушками/TODO (нарушает конвенции).
- Не править файлы напрямую на VPS (`/opt/pravoagent`) - только через git push.
- Не запускать `docker compose down -v` (удалит volumes Qdrant/Redis).
