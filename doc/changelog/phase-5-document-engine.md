# Phase 5: Document Engine + Export

Дата: 2026-06-25

## Что сделано

- **DocumentService** (`services/document_service.py`) — DocumentTemplate с 4 шаблонами (claim, lawsuit, contract, legal_opinion), Jinja2-like рендеринг через `{{key}}`, DocumentService.create_from_template(), get_document_graph()
- **ExportService** (`services/export_service.py`) — DocumentExporter: экспорт в `.docx` (python-docx), `.pdf` (weasyprint), `.txt`, `.md`
- **SharingService** (`services/sharing_service.py`) — расшаривание документов с ACL, проверка same-tenant, access_level (read/edit/comment), DocumentACL модель
- **Document Router** (`router/documents.py`) — 7 эндпоинтов: list, get, create_from_template, export, share, graph — с tenant-фильтрацией
- **DocumentACL** (`models/base.py`) — новая модель для контроля доступа к документам
- **main.py** — подключён documents_router

## Файлы (созданы/изменены)

**Созданы:**
- `backend/services/document_service.py` — DocumentTemplate (4 шаблона) + DocumentService
- `backend/services/export_service.py` — DocumentExporter (docx/pdf/txt/md)
- `backend/services/sharing_service.py` — SharingService (ACL + same-tenant check)
- `backend/router/documents.py` — 7 эндпоинтов

**Изменены:**
- `backend/models/base.py` — добавлена модель DocumentACL
- `backend/main.py` — подключён documents_router

## Исправления после ревью

1. **[HIGH]** Добавлена модель DocumentACL в `models/base.py` — отсутствовала базовая модель для ACL-записей, без неё SharingService не мог создавать записи доступа
2. **[HIGH]** SharingService: добавлена проверка same-tenant при расшаривании (владелец и получатель должны быть в одном тенанте) + создание ACL записи в БД
3. **[MEDIUM]** Tenant-фильтрация во всех эндпоинтах documents.py — каждый эндпоинт проверяет `current_user.tenant_id` перед возвратом данных

## Трудности

- WeasyPrint требует системных зависимостей (pango, cairo, gdk-pixbuf) — в контейнере необходимо устанавливать через apt. В requirements.txt добавлен только пакет, системные зависимости описаны в Dockerfile.
- python-docx не поддерживает кастомные стили заголовков через шаблоны — форматирование .docx реализовано через прямую работу с параграфами и run-ами.
- API share требует двойной проверки: владелец документа может расшаривать, но не может выдать уровень доступа выше своего. В текущей реализации владелец всегда имеет full access, что упрощает логику.

## Статус чеклиста

- [x] DocumentTemplate (4 шаблона: claim, lawsuit, contract, legal_opinion)
- [x] DocumentService (create_from_template, get_document_graph)
- [x] Экспорт в docx (python-docx)
- [x] Экспорт в pdf (weasyprint)
- [x] Экспорт в txt, md
- [x] API from-template
- [x] API export
- [x] API share с ACL
- [x] API graph
- [x] DocumentACL модель
- [x] Same-tenant проверка при шаринге
- [x] Tenant-фильтрация во всех эндпоинтах
