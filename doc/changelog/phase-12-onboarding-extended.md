# Phase 12: Расширенный онбординг (отложенная часть)

Дата: 2026-06-25

## Что сделано

- **Онбординг (6 шагов)** (`templates/onboarding.html`) — расширен с 4 до 6 шагов с полноценной навигацией Previous/Next/Finish/Skip:
  - Шаг 1: Добро пожаловать (приветствие, УТП платформы, кнопка "Начать")
  - Шаг 2: Выберите свою роль (6 карточек ролей с иконками и описанием)
  - Шаг 3: Знакомство с интерфейсом (видео-тур заглушка, описание layout workspace)
  - Шаг 4: AI-агенты (описание агентов для каждой роли — судебный юрист, договорник, общий отдел, Head of Legal, админ)
  - Шаг 5: Быстрый старт (3 стартовых сценария: создать дело, договор, доверенность)
  - Шаг 6: Готово к работе (поздравление, чек-лист, кнопка перехода в приложение)
- **Видео-тур заглушка** — placeholder с ▶, подпись "Демо-видео", модальное окно с iframe placeholder
- **Форма регистрации** (`templates/auth/register.html`) — добавлены поля:
  - `company_name` (Компания)
  - `phone` (Телефон)
  - `role` (выбор роли из 6 вариантов: litigation, contracts, general, head_legal, admin, legal_opinions)
  - Модальное окно подтверждения email с вводом 6-значного кода
- **Email Verification Service** (`backend/services/email_verification.py` — новый) — генерация 6-значного кода, проверка кода, expiry 15 минут, demo-режим: код "000000"
- **Auth Service** (`backend/services/auth_service.py`) — `register_user()` обновлён: принимает `company_name`, `phone`, автоматически создаёт код верификации
- **Auth Router** (`backend/router/auth.py`) — новые эндпоинты:
  - `POST /api/auth/verify-email` — верификация 6-значного кода
  - `POST /api/auth/resend-code` — повторная отправка кода
- **Модели** (`backend/models/base.py`) — добавлены:
  - `User`: поля `company_name`, `phone`, `email_verified`
  - Модель `EmailVerification` (user_id, code, expires_at, verified)

## Файлы (созданы/изменены)

- `templates/onboarding.html` (изменён) — 6 шагов + видео-тур заглушка
- `templates/auth/register.html` (изменён) — company_name, phone, role, модалка подтверждения email
- `backend/models/base.py` (изменён) — User дополнен, добавлен EmailVerification
- `backend/services/email_verification.py` (создан) — сервис генерации/проверки кода
- `backend/services/auth_service.py` (изменён) — register_user() принимает новые поля
- `backend/router/auth.py` (изменён) — POST /api/auth/verify-email, POST /api/auth/resend-code

## Исправления после ревью

- Ревью прошло с первого раза — **OK**. Критических замечаний нет.

## Статус чеклиста

- [x] Онбординг — 6 шагов с навигацией Previous/Next/Finish/Skip
- [x] Видео-тур заглушка (placeholder с ▶, модальное окно)
- [x] Форма регистрации: company_name, phone, role (6 вариантов)
- [x] POST /api/auth/register принимает company_name, phone
- [x] POST /api/auth/verify-email — верификация кода
- [x] POST /api/auth/resend-code — повторная отправка
- [x] Модель EmailVerification (user_id, code, expires_at, verified)
- [x] Модель User дополнена: company_name, phone, email_verified
- [x] Demo-mode: код "000000"
- [x] email_verification.py сервис (генерация, проверка, expiry 15 мин)
