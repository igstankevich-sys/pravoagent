.PHONY: help install run deploy stop clean

help:
	@echo "ПравоАгент - Makefile"
	@echo ""
	@echo "install     - Установка зависимостей"
	@echo "run         - Запуск через uvicorn (dev)"
	@echo "docker-up           - Запуск через Docker Compose"
	@echo "docker-down         - Остановка Docker Compose"
	@echo "docker-down-volumes - Остановка + удаление volumes (Qdrant/Redis)"
	@echo "docker-logs         - Просмотр логов Docker Compose"
	@echo "docker-ps           - Список запущенных сервисов"
	@echo "seed        - Генерация тестовых данных"
	@echo "ssl         - Генерация самоподписанных SSL сертификатов"
	@echo "deploy      - Полный деплой (ssl + docker-up + seed)"
	@echo "clean       - Очистка данных"

install:
	pip install -r requirements.txt

run:
	uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-down-volumes:
	docker compose down -v

docker-logs:
	docker compose logs -f

docker-ps:
	docker compose ps

seed:
	python -m backend.seed_data.generate_all

ssl:
	./docker/ssl/generate-ssl.sh

deploy: ssl docker-up seed
	@echo "ПравоАгент запущен на https://pravoagent.igor-stankevich.ru"

clean:
	rm -rf data/pravoagent.db data/uploads/* data/exports/*
	@echo "Данные очищены"
