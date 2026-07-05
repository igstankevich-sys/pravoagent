#!/bin/bash
# Генерация самоподписанных SSL сертификатов для демо-режима
# В production - заменить на Let's Encrypt

mkdir -p "$(dirname "$0")"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$(dirname "$0")/key.pem" \
    -out "$(dirname "$0")/cert.pem" \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=PravoAgent/CN=pravoagent.igor-stankevich.ru" \
    -addext "subjectAltName=DNS:pravoagent.igor-stankevich.ru,DNS:localhost"

echo "SSL certificates generated: $(dirname "$0")/"
