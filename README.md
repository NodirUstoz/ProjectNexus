<div align="center">

# ProjectNexus

**Комплексная SaaS-платформа управления проектами и командной работой — ваш собственный Jira / Asana под полным контролем.**

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.4-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/)

[![Docker Compose](https://img.shields.io/badge/Docker_Compose-3.9-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Nginx](https://img.shields.io/badge/Nginx-Reverse_Proxy-009639?style=for-the-badge&logo=nginx&logoColor=white)](https://nginx.org/)
[![Channels](https://img.shields.io/badge/Django_Channels-4.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://channels.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## Содержание

1. [О проекте](#1-о-проекте)
2. [Ключевые возможности](#2-ключевые-возможности)
3. [Технологический стек](#3-технологический-стек)
4. [Структура репозитория](#4-структура-репозитория)
5. [Архитектура и как это работает](#5-архитектура-и-как-это-работает)
6. [Доменная модель (крупными блоками)](#6-доменная-модель-крупными-блоками)
7. [Сервисы в Docker Compose](#7-сервисы-в-docker-compose)
8. [Быстрый старт (локально, Docker)](#8-быстрый-старт-локально-docker)
9. [Основные команды Docker Compose](#9-основные-команды-docker-compose)
10. [Ручной запуск frontend и backend](#10-ручной-запуск-frontend-и-backend)
11. [Конфигурация и переменные окружения](#11-конфигурация-и-переменные-окружения)
12. [API, WebSocket и интеграции](#12-api-websocket-и-интеграции)
13. [Мониторинг и эксплуатация](#13-мониторинг-и-эксплуатация)
14. [CI/CD](#14-cicd)
15. [Безопасность и хранение данных](#15-безопасность-и-хранение-данных)
16. [Роли компонентов в продакшене](#16-роли-компонентов-в-продакшене)
17. [Лицензия](#17-лицензия)
18. [Поддержка](#18-поддержка)

---

## 1. О проекте

**ProjectNexus** — это production-ready платформа для планирования, отслеживания и совместной работы над проектами. Система объединяет Kanban-доски, Scrum-спринты, учёт времени, диаграммы Ганта, аналитику и real-time уведомления в едином веб-интерфейсе.

Платформа рассчитана на три аудитории:

| Аудитория | Сценарий использования |
|-----------|------------------------|
| **Команды и менеджеры** | Планирование спринтов, распределение задач, контроль дедлайнов |
| **Разработчики и исполнители** | Kanban, тайм-трекинг, комментарии, вложения, live-обновления доски |
| **Интеграторы** | REST API с JWT, WebSocket-события для внешних систем |

### Что это за тип системы?

ProjectNexus — **мультисервисная распределённая платформа**, а не монолитный скрипт. Логика разделена между API-слоем, SPA-фронтендом, фоновыми воркерами и инфраструктурными сервисами.

| Аспект | Описание |
|--------|----------|
| **Продукт** | B2B/B2C SaaS для управления проектами: workspace'ы, роли, квоты, аудит активности |
| **Архитектура** | Django API (ASGI) + React SPA + Celery workers + PostgreSQL + Redis |
| **Хранилище** | PostgreSQL (метаданные и бизнес-логика) + Redis (кэш, брокер, channel layer) + media volume (файлы) |

---

## 2. Ключевые возможности

### Организация и доступ

- **Workspace'ы** — мультитенантная изоляция с ролевой моделью (Owner, Admin, Member, Viewer)
- **Команды** — группировка участников и привязка к проектам
- **Проекты** — Kanban, Scrum, гибридные типы с настраиваемыми досками и колонками

### Управление работой

- **Kanban-доски** — drag-and-drop перемещение задач между колонками
- **Scrum-спринты** — полный жизненный цикл: планирование → старт → завершение
- **Бэклог** — приоритизация и переупорядочивание задач
- **Вехи (Milestones)** — контрольные точки с привязкой задач и статусами
- **Подзадачи, метки, приоритеты** — гибкая декомпозиция и категоризация

### Визуализация и аналитика

- **Диаграмма Ганта** — временная шкала проекта с зависимостями
- **Burndown / Velocity** — метрики спринта и скорость команды
- **Дашборды** — cycle time, throughput, распределение по статусам

### Совместная работа

- **Real-time** — WebSocket-обновления доски и уведомлений без перезагрузки страницы
- **Комментарии и реакции** — обсуждение задач с полной историей изменений
- **Вложения** — загрузка файлов к задачам (drag-and-drop)
- **Документы** — папки, версии, централизованное хранилище проектной документации
- **Уведомления** — in-app и push через WebSocket (назначения, упоминания, обновления)

### Учёт времени

- **Time entries** — ручной лог времени по задачам
- **Таймеры** — старт/стоп учёта в реальном времени
- **Отчёты** — сводки по проектам, участникам и периодам

---

## 3. Технологический стек

### Backend

| Технология | Назначение |
|------------|------------|
| **Django 5.0** | ORM, админка, бизнес-логика |
| **Django REST Framework** | REST API, сериализаторы, пагинация |
| **Simple JWT** | Аутентификация access/refresh токенами |
| **Django Channels 4** | WebSocket (доски задач, уведомления) |
| **Daphne** | ASGI-сервер для HTTP + WebSocket |
| **Celery 5 + Beat** | Фоновые задачи и периодические джобы |
| **PostgreSQL 16** | Основная реляционная БД |
| **Redis 7** | Кэш, Celery broker, Channels layer |
| **WhiteNoise / django-storages** | Статика и опциональное S3-хранилище |

### Frontend

| Технология | Назначение |
|------------|------------|
| **React 18** | SPA-интерфейс |
| **Redux Toolkit** | Глобальное состояние (auth, projects, tasks, notifications) |
| **React Router v6** | Клиентская маршрутизация |
| **Axios** | HTTP-клиент с JWT interceptors |
| **Recharts** | Burndown, velocity, дашборды |
| **React Beautiful DnD** | Drag-and-drop на досках |

### Инфраструктура

| Технология | Назначение |
|------------|------------|
| **Docker Compose** | Оркестрация всех сервисов локально и в staging |
| **Nginx** | Reverse proxy, gzip, WebSocket upgrade, раздача static/media |
| **Gunicorn** | WSGI (опционально для чистого HTTP без Channels) |

---

## 4. Структура репозитория

```
ProjectNexus/
├── backend/                    # Django-приложение
│   ├── apps/
│   │   ├── accounts/           # User, Workspace, JWT auth
│   │   ├── projects/           # Project, Board, Label
│   │   ├── tasks/              # Task, Subtask, Attachments, WebSocket consumer
│   │   ├── sprints/            # Sprint, SprintGoal
│   │   ├── milestones/         # Milestone, MilestoneTask
│   │   ├── teams/              # Team, TeamMember
│   │   ├── time_tracking/      # TimeEntry, Timer
│   │   ├── documents/          # DocumentFolder, Document, Version
│   │   ├── comments/           # Comment, Reaction
│   │   ├── analytics/          # Burndown, velocity, dashboards
│   │   └── notifications/      # Notification, preferences, WS consumer
│   ├── config/
│   │   ├── settings/           # base | development | production
│   │   ├── urls.py             # Маршрутизация API
│   │   ├── routing.py          # WebSocket URLs
│   │   ├── celery.py           # Celery app
│   │   └── asgi.py             # ASGI entrypoint
│   ├── utils/                  # Пагинация, исключения
│   ├── Dockerfile
│   ├── manage.py
│   └── requirements.txt
├── frontend/                   # React SPA
│   ├── public/
│   └── src/
│       ├── api/                # API-клиенты по доменам
│       ├── components/         # UI: boards, gantt, sprints, auth...
│       ├── pages/              # Dashboard, Projects, Tasks, Reports...
│       ├── store/              # Redux slices
│       ├── hooks/              # useWebSocket, useDragAndDrop...
│       └── services/           # Axios instance, interceptors
├── nginx/
│   └── nginx.conf              # Reverse proxy конфигурация
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 5. Архитектура и как это работает

### Общая схема

```
                         ┌─────────────────┐
                         │      Nginx      │
                         │  Reverse Proxy  │
                         │   :80 / :443    │
                         └────────┬────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
       ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐
       │   React     │     │   Django    │     │  /static    │
       │  Frontend   │     │   Backend   │     │  /media     │
       │   :3000     │     │  Daphne     │     │  volumes    │
       └─────────────┘     │   :8000     │     └─────────────┘
                           └──────┬──────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
  ┌──────▼──────┐          ┌──────▼──────┐          ┌──────▼──────┐
  │ PostgreSQL  │          │    Redis    │          │   Celery    │
  │     :5432   │          │    :6379    │          │ Worker+Beat │
  └─────────────┘          └─────────────┘          └─────────────┘
```

### Поток запроса (HTTP)

1. Браузер обращается к **Nginx** (`/` → frontend, `/api/` → backend).
2. **React** отправляет REST-запросы с JWT в заголовке `Authorization`.
3. **Django REST Framework** валидирует токен, выполняет бизнес-логику, пишет в **PostgreSQL**.
4. Тяжёлые операции (email, отчёты, периодика) уходят в **Celery** через **Redis**.

### Поток real-time (WebSocket)

1. Клиент подключается к `ws://<host>/ws/tasks/<project_id>/` или `/ws/notifications/`.
2. **Nginx** проксирует upgrade на **Daphne** (ASGI).
3. **Channels** маршрутизирует соединение к соответствующему consumer.
4. События (`task.moved`, `notification.new`) рассылаются группе подписчиков через **Redis channel layer**.

---

## 6. Доменная модель (крупными блоками)

| Домен | Сущности | Ответственность |
|-------|----------|-----------------|
| **Accounts** | `User`, `Workspace`, `WorkspaceMember` | Регистрация, JWT, мультитенантность, роли |
| **Projects** | `Project`, `Board`, `BoardColumn`, `Label` | Структура проекта и Kanban-колонки |
| **Tasks** | `Task`, `Subtask`, `TaskAttachment`, `TaskHistory` | Жизненный цикл задачи, аудит изменений |
| **Sprints** | `Sprint`, `SprintGoal` | Scrum-итерации и цели спринта |
| **Milestones** | `Milestone`, `MilestoneTask` | Контрольные точки и привязка задач |
| **Teams** | `Team`, `TeamMember`, `TeamProject` | Командная организация |
| **Time** | `TimeEntry`, `Timer` | Учёт рабочего времени |
| **Documents** | `DocumentFolder`, `Document`, `DocumentVersion` | Файловое хранилище проекта |
| **Comments** | `Comment`, `CommentReaction` | Обсуждения и реакции |
| **Notifications** | `Notification`, `NotificationPreference` | Оповещения и настройки каналов |
| **Analytics** | — (агрегации поверх Tasks/Sprints) | Burndown, velocity, метрики дашборда |

---

## 7. Сервисы в Docker Compose

| Сервис | Контейнер | Порт | Описание |
|--------|-----------|------|----------|
| `db` | `nexus_db` | 5432 | PostgreSQL 16, persistent volume |
| `redis` | `nexus_redis` | 6379 | Кэш, broker, Channels |
| `backend` | `nexus_backend` | 8000 | Django + Daphne (migrate + collectstatic при старте) |
| `celery_worker` | `nexus_celery_worker` | — | Фоновые задачи (concurrency=4) |
| `celery_beat` | `nexus_celery_beat` | — | Периодические задачи (DatabaseScheduler) |
| `frontend` | `nexus_frontend` | 3000 | React dev/production server |
| `nginx` | `nexus_nginx` | 80 | Единая точка входа, WS proxy, static/media |

**Volumes:** `postgres_data`, `redis_data`, `static_files`, `media_files`

---

## 8. Быстрый старт (локально, Docker)

### Требования

- [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/) v2+
- [Git](https://git-scm.com/)
- 4+ GB RAM для комфортной работы всех контейнеров

### Запуск за 5 минут

```bash
# 1. Клонировать репозиторий
git clone https://github.com/NodirOdilov/ProjectNexus.git
cd ProjectNexus

# 2. Подготовить окружение
cp .env.example .env
# Отредактируйте SECRET_KEY, пароли БД при необходимости

# 3. Собрать и запустить стек
docker compose up --build -d

# 4. Создать суперпользователя (миграции выполняются при старте backend)
docker compose exec backend python manage.py createsuperuser
```

### Точки доступа

| Сервис | URL |
|--------|-----|
| **Веб-приложение (через Nginx)** | http://localhost |
| **Frontend напрямую** | http://localhost:3000 |
| **Backend API** | http://localhost:8000/api/ |
| **Django Admin** | http://localhost/admin/ |
| **PostgreSQL** | `localhost:5432` |
| **Redis** | `localhost:6379` |

---

## 9. Основные команды Docker Compose

```bash
# Запуск / остановка
docker compose up -d              # фоновый режим
docker compose down               # остановить и удалить контейнеры
docker compose down -v            # + удалить volumes (ОСТОРОЖНО: потеря данных БД)

# Логи
docker compose logs -f backend
docker compose logs -f celery_worker

# Django management
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec backend python manage.py shell

# Тесты
docker compose exec backend python manage.py test

# Пересборка одного сервиса
docker compose up --build backend -d
```

---

## 10. Ручной запуск frontend и backend

Используйте, когда нужна отладка без полного Docker-стека (БД и Redis всё равно потребуются).

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

export DJANGO_SETTINGS_MODULE=config.settings.development
export DATABASE_URL=postgres://nexus:nexus_secret@localhost:5432/projectnexus
export REDIS_URL=redis://localhost:6379/0
export CELERY_BROKER_URL=redis://localhost:6379/1

python manage.py migrate
python manage.py runserver          # HTTP only
# или для WebSocket:
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### Celery (отдельные терминалы)

```bash
cd backend
celery -A config worker -l info
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Frontend

```bash
cd frontend
npm install
npm run dev        # Vite dev server
# или
npm start          # CRA-совместимый скрипт, если настроен
```

> **Переменные фронтенда:** `REACT_APP_API_URL` / `VITE_API_URL` и `REACT_APP_WS_URL` / `VITE_WS_URL` — см. `.env.example`.

---

## 11. Конфигурация и переменные окружения

Скопируйте `.env.example` → `.env`. Ключевые группы настроек:

| Группа | Переменные | Описание |
|--------|------------|----------|
| **Django** | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DJANGO_SETTINGS_MODULE` | Безопасность и режим работы |
| **База данных** | `POSTGRES_*`, `DATABASE_URL` | PostgreSQL connection string |
| **Redis / Celery** | `REDIS_URL`, `CELERY_BROKER_URL` | Кэш, broker, Channels |
| **CORS** | `CORS_ALLOWED_ORIGINS` | Разрешённые origin для SPA |
| **Frontend** | `REACT_APP_API_URL`, `REACT_APP_WS_URL` | URL API и WebSocket |
| **Email** | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`... | SMTP для уведомлений |
| **JWT** | `ACCESS_TOKEN_LIFETIME`, `REFRESH_TOKEN_LIFETIME` | Время жизни токенов (минуты) |
| **Файлы** | `MAX_UPLOAD_SIZE_MB` | Лимит загрузки вложений |
| **Мониторинг** | `SENTRY_DSN` (опционально) | Error tracking в production |

### Профили настроек

| Модуль | Когда использовать |
|--------|-------------------|
| `config.settings.development` | Локальная разработка, `DEBUG=True` |
| `config.settings.production` | Продакшен: HSTS, secure cookies, WhiteNoise, SMTP |

---

## 12. API, WebSocket и интеграции

### REST API — обзор эндпоинтов

#### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/auth/register/` | Регистрация |
| `POST` | `/api/auth/login/` | Вход, выдача JWT |
| `POST` | `/api/auth/token/refresh/` | Обновление access-токена |
| `GET` | `/api/auth/me/` | Профиль текущего пользователя |

#### Workspace'ы и проекты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET/POST` | `/api/workspaces/` | Список / создание workspace |
| `GET` | `/api/workspaces/:id/` | Детали workspace |
| `POST` | `/api/workspaces/:id/invite/` | Приглашение участника |
| `GET/POST` | `/api/projects/` | Проекты в workspace |
| `GET` | `/api/projects/:id/board/` | Kanban-доска проекта |

#### Задачи и спринты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET/POST` | `/api/tasks/` | Список / создание задач |
| `PATCH` | `/api/tasks/:id/` | Обновление задачи |
| `POST` | `/api/tasks/:id/move/` | Перемещение между колонками |
| `POST` | `/api/tasks/:id/comments/` | Комментарий |
| `POST` | `/api/tasks/:id/attachments/` | Вложение |
| `GET/POST` | `/api/sprints/` | Спринты |
| `POST` | `/api/sprints/:id/start/` | Старт спринта |
| `POST` | `/api/sprints/:id/complete/` | Завершение спринта |

#### Время и аналитика

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET/POST` | `/api/time/entries/` | Записи времени |
| `GET` | `/api/time/reports/` | Отчёты по времени |
| `GET` | `/api/analytics/burndown/:sprint_id/` | Burndown-данные |
| `GET` | `/api/analytics/velocity/:project_id/` | Velocity |
| `GET` | `/api/analytics/dashboard/:project_id/` | Метрики дашборда |

### WebSocket

| Канал | URL | События |
|-------|-----|---------|
| **Доска задач** | `ws://<host>/ws/tasks/<project_id>/` | `task.created`, `task.updated`, `task.moved`, `task.deleted`, `comment.added` |
| **Уведомления** | `ws://<host>/ws/notifications/` | `notification.new`, `notification.read` |

> В production используйте `wss://` за HTTPS-терминацией Nginx.

### Аутентификация API

Все защищённые эндпоинты требуют заголовок:

```
Authorization: Bearer <access_token>
```

---

## 13. Мониторинг и эксплуатация

| Область | Рекомендация |
|---------|--------------|
| **Логи Django** | `docker compose logs -f backend`; в production — файл `logs/django.log` |
| **Celery** | Мониторинг очереди через Flower (можно добавить в compose) |
| **PostgreSQL** | Регулярные бэкапы volume `postgres_data`, `pg_dump` по расписанию |
| **Redis** | Persistence (AOF/RDB) для production; отдельный инстанс под нагрузкой |
| **Ошибки** | `SENTRY_DSN` в production settings |
| **Healthchecks** | `db` и `redis` уже имеют healthcheck в `docker-compose.yml` |

### Полезные проверки

```bash
# Состояние контейнеров
docker compose ps

# Подключение к БД
docker compose exec db psql -U nexus -d projectnexus -c "\dt"

# Redis ping
docker compose exec redis redis-cli ping
```

---

## 14. CI/CD

В репозитории CI-пайплайн подключается по мере необходимости. Рекомендуемый минимальный pipeline (GitHub Actions):

```yaml
# .github/workflows/ci.yml (шаблон)
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r backend/requirements.txt
      - run: python backend/manage.py test
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: cd frontend && npm ci && npm test
```

**Деплой:** сборка Docker-образов → registry → `docker compose -f docker-compose.prod.yml up -d` на сервере с `DJANGO_SETTINGS_MODULE=config.settings.production`.

---

## 15. Безопасность и хранение данных

| Принцип | Реализация |
|---------|------------|
| **Аутентификация** | JWT (access + refresh), email как `USERNAME_FIELD` |
| **Авторизация** | Роли на уровне workspace, project, team |
| **Транспорт** | HTTPS / WSS в production (`SECURE_SSL_REDIRECT`, HSTS) |
| **CSRF / Cookies** | Secure cookies при `DEBUG=False` |
| **Файлы** | Локальный `media` volume или S3 через `django-storages` + `boto3` |
| **Секреты** | Только через `.env` / secrets manager, никогда в git |
| **CORS** | Явный whitelist origin в production |

**Перед выкладкой в production обязательно:**

1. Сгенерировать криптостойкий `SECRET_KEY`
2. Установить `DEBUG=False` и `DJANGO_SETTINGS_MODULE=config.settings.production`
3. Ограничить `ALLOWED_HOSTS` и `CORS_ALLOWED_ORIGINS`
4. Настроить SMTP и (опционально) Sentry

---

## 16. Роли компонентов в продакшене

| Компонент | Роль | Масштабирование |
|-----------|------|-----------------|
| **Nginx** | TLS termination, static/media, rate limiting, WS proxy | Горизонтально за load balancer |
| **Daphne / Gunicorn** | Обработка HTTP API | Несколько воркеров / реплик backend |
| **Celery Worker** | Email, отчёты, тяжёлые задачи | Увеличение `--concurrency` и числа воркеров |
| **Celery Beat** | Один инстанс с DatabaseScheduler | Только один активный beat |
| **PostgreSQL** | Source of truth | Managed DB (RDS, Cloud SQL) + реплики |
| **Redis** | Cache + broker + Channels | Redis Cluster / Sentinel при росте нагрузки |
| **React build** | Статика через Nginx или CDN | Immutable assets, cache busting |

---

## 17. Лицензия

Проект распространяется под лицензией **MIT**. Вы можете свободно использовать, модифицировать и распространять код с сохранением уведомления об авторских правах.

---

## 18. Поддержка

| Канал | Действие |
|-------|----------|
| **Issues** | [GitHub Issues](https://github.com/NodirOdilov/ProjectNexus/issues) — баги и предложения |
| **Pull Requests** | Fork → feature branch → PR с описанием изменений |
| **Документация** | Этот README + inline-комментарии в `backend/config/settings/` |

### Как внести вклад

1. Сделайте fork репозитория
2. Создайте ветку: `git checkout -b feature/amazing-feature`
3. Зафиксируйте изменения: `git commit -m 'feat: add amazing feature'`
4. Отправьте ветку: `git push origin feature/amazing-feature`
5. Откройте Pull Request

---

<div align="center">

**ProjectNexus** — управляйте проектами так, как управляют лучшие команды мира.

*Сделано с вниманием к деталям, масштабируемости и developer experience.*

</div>
