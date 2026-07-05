#!/bin/bash
set -e

# Генерация seed data при первом запуске
python backend/seed_data/generate_all.py

# Запуск приложения
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
