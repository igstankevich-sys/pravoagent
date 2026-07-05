# Phase 13: nginx + .dockerignore + SSL

Дата: 2026-06-25

## Что сделано

- **nginx конфиг** (`docker/nginx.conf`) — upstream app:8000, HTTP→HTTPS redirect, SSL (TLSv1.2 + TLSv1.3), security headers (HSTS, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection), WebSocket поддержка (Upgrade), proxy timeouts 60s, alias для статики с кешем 7 дней
- **`.dockerignore`** — исключает из сборки .git/, __pycache__/, .env, .venv, data/, .dockerignore, Dockerfile, .cursor/, логи, node_modules, .DS_Store
- **SSL сертификаты** (`docker/ssl/cert.pem`, `docker/ssl/key.pem`) — самоподписанные (365 дней, SAN: pravoagent.igor-stankevich.ru + localhost)
- **Скрипт генерации сертификатов** (`docker/ssl/generate-ssl.sh`) — исполняемый, с openssl req + SAN config
- **docker-compose.yml** (изменён) — добавлен nginx сервис (nginx:alpine, порты 80:80 / 443:443, volumes на nginx.conf, static, ssl)
- **Makefile** (изменён) — добавлена команда `ssl` (генерация сертификатов), команда `deploy` дополнена шагом ssl → docker-up → seed

## Файлы (созданы/изменены)

- `docker/nginx.conf` (изменён) — полный конфиг с SSL, security headers, WebSocket
- `.dockerignore` (создан) — 12 правил игнорирования
- `docker/ssl/cert.pem` (создан) — самоподписанный SSL сертификат
- `docker/ssl/key.pem` (создан) — приватный ключ
- `docker/ssl/generate-ssl.sh` (создан) — исполняемый скрипт генерации
- `docker-compose.yml` (изменён) — nginx сервис
- `Makefile` (изменён) — ssl и deploy команды

## Исправления после ревью

Ревью — OK с первого раза. Все 6 критериев выполнены, замечаний нет.

## Трудности

Не возникло — задача была изолированной, конфигурация типовой для production FastAPI-приложений.

## Статус чеклиста

- [x] docker/nginx.conf: upstream, HTTPS redirect, SSL, security headers, WebSocket, static, timeouts
- [x] .dockerignore создан
- [x] docker-compose.yml: nginx сервис (nginx:alpine, 80/443, volumes)
- [x] docker/ssl/cert.pem и key.pem (самоподписанные)
- [x] docker/ssl/generate-ssl.sh (исполняемый)
- [x] Makefile: ssl и deploy команды
