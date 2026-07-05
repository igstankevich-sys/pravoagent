# ПравоАгент - Makefile
#
# ЛОКАЛЬНАЯ РАЗРАБОТКА:  install, run, test, lint, format, seed
# ДЕПЛОЙ (локаль -> VPS): deploy, logs, ssh, health, prune
# НА VPS (когда на сервере): docker-up, docker-down, docker-ps, docker-logs, ssl

PYTHON ?= python3
PORT   ?= 8000
VPS    := adminvps
REMOTE := /opt/pravoagent

.PHONY: help install run test lint format seed \
        deploy logs ssh health ps-remote prune \
        docker-up docker-down docker-down-volumes docker-ps docker-logs ssl clean

help: ## Этот список команд
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ============ ЛОКАЛЬНАЯ РАЗРАБОТКА ============

install: ## Создать venv и поставить зависимости
	$(PYTHON) -m venv .venv 2>/dev/null || true
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

run: ## uvicorn dev-сервер (--reload) на :$(PORT)
	$(PYTHON) -m uvicorn backend.main:app --reload --host 0.0.0.0 --port $(PORT)

test: ## pytest
	$(PYTHON) -m pytest -q

lint: ## ruff check
	$(PYTHON) -m ruff check .

format: ## ruff format
	$(PYTHON) -m ruff format .

seed: ## Залить тестовые данные в локальную SQLite
	$(PYTHON) -m backend.seed_data.generate_all

# ============ ДЕПЛОЙ (локаль -> VPS) ============
# origin = adminvps:/opt/pravoagent, receive.denyCurrentBranch=updateInstead
# обновляет working tree на VPS при git push.

deploy: ## git push -> VPS auto-pull -> docker compose up -d --build -> health
	@bash -c 'if [ -n "$$(git status --porcelain)" ]; then git add -A && git commit -m "deploy: $$(date +%FT%T)"; fi'
	git push origin main
	ssh $(VPS) 'cd $(REMOTE) && docker compose up -d --build'
	@echo "Жду health-check..."
	@sleep 6
	ssh $(VPS) 'curl -fsS http://localhost:8000/health' && echo " -> deployed"

logs: ## Логи приложения на VPS (tail -f)
	ssh $(VPS) 'cd $(REMOTE) && docker compose logs -f --tail=200 app'

ssh: ## SSH на VPS
	ssh $(VPS)

health: ## Health-check приложения на VPS
	ssh $(VPS) 'curl -fsS http://localhost:8000/health' && echo

ps-remote: ## Статус контейнеров на VPS
	ssh $(VPS) 'cd $(REMOTE) && docker compose ps'

prune: ## Очистить docker build-cache и dangling images на VPS (диск!)
	ssh $(VPS) 'docker builder prune -af && docker image prune -f'

# ============ НА VPS (запускать, будучи на сервере) ============

docker-up: ## [на VPS] docker compose up -d --build
	docker compose up -d --build

docker-down: ## [на VPS] docker compose down
	docker compose down

docker-down-volumes: ## [на VPS] docker compose down -v (УДАЛЯЕТ volumes Qdrant/Redis!)
	docker compose down -v

docker-ps: ## [на VPS] список сервисов
	docker compose ps

docker-logs: ## [на VPS] логи всех сервисов
	docker compose logs -f

ssl: ## [на VPS] сгенерировать self-signed SSL
	./docker/ssl/generate-ssl.sh

clean: ## Очистить локальные данные (SQLite/uploads/exports)
	rm -rf data/pravoagent.db data/uploads/* data/exports/*
	@echo "Локальные данные очищены"
