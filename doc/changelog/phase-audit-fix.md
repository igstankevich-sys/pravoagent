# Phase: Audit Fix — Full Interactivity & Bug Fixes

Дата: 2026-06-25

## Что найдено на аудите

Аудит прототипа ПравоАгент выявил 10 проблем:

1. **3 workspace шаблона были 100% статическим HTML** — `contracts.html`, `general.html`, `legal_opinions.html` — ноль JavaScript, ноль API-вызовов, ноль интерактивности
2. **AI-чат был фейковым** — все workspace содержали хардкодные сообщения вместо реальных вызовов `/api/agent/chat`
3. **index.html содержал хардкодные данные** — таблица дел, дерево сайдов, пагинация — всё статическое
4. **Проблемы инфраструктуры** — healthcheck в docker-compose через `curl` без гарантии его наличия; Dockerfile использовал `CMD` вместо `ENTRYPOINT`; корневой docker-compose.yml не содержал qdrant/redis
5. **BUG #1 (CRITICAL)** — `legal_opinions.html` ссылался на имена шаблонов (`opinion_standard` и др.), которых не было в `DocumentService.TEMPLATES`
6. **BUG #2 (HIGH)** — `index.html` ссылка агента вела на `/api/agent/chat?agent_type=litigation` вместо `/app/litigation`
7. **BUG #3 (HIGH)** — `legal_opinions.html` вызывал `openAiChat()`, которая не была определена
8. **BUG #4 (HIGH)** — `general.html` функция `shareDocument()` использовала `parseInt('')`, порождая NaN в JSON
9. **BUG #5 (MEDIUM)** — `index.html` кнопки пагинации были статическими, дропдауны фильтров — без обработчиков
10. **BUG #6 (MEDIUM)** — `contracts.html` flow согласования целиком был клиентским mock'ом

## Что сделано

### Созданы файлы

- `static/js/chat-widget.js` — переиспользуемый класс ChatWidget для AI-чата во всех workspace (подключение к `/api/agent/chat`, typing indicator, Bearer token auth, обработка ошибок)

### Изменены файлы

- `templates/workspaces/contracts.html` — полная JS-интерактивность: таблица договоров из API, кнопки approve/send, AI-чат, модалки create/export/share, approval flow
- `templates/workspaces/general.html` — полная JS-интерактивность: таблица документов из API, фильтрация карточек секций, AI-чат, модалки create/export/share, sidebar из API
- `templates/workspaces/legal_opinions.html` — полная JS-интерактивность: таблица заключений из API, реальная статистика, AI-чат, модалки create/detail
- `templates/index.html` — хардкодные данные заменены на реальные API-вызовы (таблица дел, статистика, дерево сайдов); карточки агентов ведут в workspace; фильтры работают; пагинация динамическая
- `templates/base.html` — добавлен скрипт `chat-widget.js`
- `backend/services/document_service.py` — добавлены 5 шаблонов заключений: `opinion_standard`, `opinion_detailed`, `opinion_contract`, `opinion_court`, `opinion_memo`
- `backend/router/observability.py` — добавлен POST-эндпоинт `/api/observability/action-logs`
- `docker-compose.yml` (ПравоАгент/VPS/) — healthcheck исправлен: `curl -f http://localhost` заменён на `python3 -c "..."`
- `docker/Dockerfile` — `CMD` заменён на `ENTRYPOINT`, seed data запускается корректно
- `docker-compose.yml` (корневой) — добавлены сервисы qdrant и redis

## Исправленные баги

| # | Серьёзность | Описание | Статус |
|---|------------|----------|--------|
| 1 | CRITICAL | `legal_opinions.html` ссылался на несуществующие шаблоны | Исправлено: добавлены 5 шаблонов в `document_service.py` |
| 2 | HIGH | Ссылка агента на `/api/agent/chat` вместо `/app/litigation` | Исправлено: путь заменён на workspace URL |
| 3 | HIGH | `openAiChat()` не определена в `legal_opinions.html` | Исправлено: добавлено определение функции через `ChatWidget` |
| 4 | HIGH | `parseInt('')` даёт NaN в JSON (`general.html`) | Исправлено: добавлена валидация `userId` |
| 5 | MEDIUM | Пагинация статическая, фильтры без обработчиков (`index.html`) | Исправлено: динамическая пагинация, onchange-обработчики фильтров |
| 6 | MEDIUM | Approval flow целиком клиентский mock (`contracts.html`) | Исправлено: flow привязан к выбранному договору, API-логирование через POST `/api/observability/action-logs`, добавлено состояние "Выберите договор" |

## Трудности

- Потребовалось 2 раунда параллельных Worker'ов (6 + 3): первый раунд — устранение основных проблем, второй — доработка по замечаниям ревьюера
- BUG #1 (CRITICAL) не был очевиден до тестирования шаблонов legal_opinions — потребовал внимательного прогона сценария создания заключения
- BUG #3 (HIGH) — `openAiChat()` была в inline-скрипте на одной странице, но отсутствовала в `legal_opinions.html`, что требовало синхронизации при добавлении `chat-widget.js`
- Работа параллельных Worker'ов усложнила отслеживание пересечений изменений (особенно в `legal_opinions.html`, который правили 3 разных Worker'a)

## Статус чеклиста

- [x] contracts.html — полная интерактивность (таблица, approve/send, AI-чат, модалки)
- [x] general.html — полная интерактивность (таблица, фильтры, AI-чат, модалки)
- [x] legal_opinions.html — полная интерактивность (таблица, статистика, AI-чат, модалки)
- [x] index.html — реальные API-данные, динамическая пагинация, фильтры
- [x] chat-widget.js — переиспользуемый AI-чат во всех workspace
- [x] BUG #1 (CRITICAL) — шаблоны заключений добавлены
- [x] BUG #2 (HIGH) — ссылка агента исправлена
- [x] BUG #3 (HIGH) — openAiChat определена
- [x] BUG #4 (HIGH) — shareDocument валидация userId
- [x] BUG #5 (MEDIUM) — пагинация/фильтры динамические
- [x] BUG #6 (MEDIUM) — approval flow с API-логированием
- [x] Инфраструктура — healthcheck (python вместо curl), ENTRYPOINT, qdrant/redis сервисы
