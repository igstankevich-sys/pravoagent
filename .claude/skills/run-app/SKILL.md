---
name: run-app
description: Запускает ПравоАгент локально и проверяет, что он загружается. Создаёт .env из примера если нет, ставит зависимости, стартует uvicorn, проверяет /health.
---

# run-app

В корне проекта (`~/projects/pravoagent`):

1. `.env` существует?
   ```bash
   [ -f .env ] || cp .env.example .env
   ```
   Если только что создан из example - сообщить пользователю заполнить `SECRET_KEY`,
   `JWT_SECRET_KEY`, `DEEPSEEK_API_KEY` (хотя для `DEMO_MODE=true` ключи не обязательны).

2. Зависимости:
   ```bash
   make install    # venv + pip install -r requirements.txt
   ```
   Если `make install` падает на weasyprint/sentence-transformers - сообщить (системные deps).

3. БД + seed (если `data/pravoagent.db` нет):
   ```bash
   [ -f data/pravoagent.db ] || make seed
   ```

4. Запустить uvicorn в фоне и дождаться старта:
   ```bash
   make run    # в отдельном терминале/фоне; ждать "Uvicorn running on http://127.0.0.1:8000"
   ```

5. Health-check:
   ```bash
   curl -fsS http://127.0.0.1:8000/health    # ожидать {"status":"ok","database":"connected",...}
   ```

Сообщить URL (`http://127.0.0.1:8000`) и краткую сводку ключевых роутов из `backend/main.py`
(/health, /, /api/cases, /api/documents, /api/agent/chat, /auth/*, и т.д.).
