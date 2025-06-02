# AI Learning Platform

Платформа персонализированного обучения с использованием AI.

## Технологии

### Backend:

* Python 3.12
* FastAPI
* SQLAlchemy (async)
* PostgreSQL
* OpenAI API
* Docker & Docker Compose

### Frontend:

* React + TypeScript
* Vite
* TailwindCSS
* Docker

## Структура проекта

```
.
├── backend/
│   ├── app/
│   │   ├── core/          # Конфигурации
│   │   ├── models/        # Модели БД
│   │   ├── schemas/       # Pydantic схемы
│   │   ├── api/           # Эндпоинты API
│   │   ├── services/      # Бизнес-логика
│   │   └── migrations/    # Alembic миграции
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   ├── Dockerfile.dev     # Для разработки
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml      # Продакшн
├── docker-compose-dev.yml  # Для разработки
├── .env.example
└── README.md
```

## Требования

* Docker и Docker Compose
* Python 3.12+
* OpenAI API ключ

## Установка и запуск (продакшн)

1. Клонируйте репозиторий:

```bash
git clone <repository-url>
cd vectorAI
```

2. Заполните `.env` и `frontend/.env по примерам .env.example и frontend/.env.example`

3. Соберите и запустите проект:

```bash
docker compose up --build -d
```

## Разработка

Для локальной разработки с горячей перезагрузкой фронтенда и backend-автообновлением используйте `docker-compose-dev.yml`:

Запускаем frontend 
```bash
cd frontend
npm run dev
```
Запускаем backend
```bash
docker compose -f docker-compose-dev.yml up --build
```

* **Фронтенд:** `http://localhost:5173`
* **Бэкенд:** `http://localhost:8000`
* **Nginx** `http://localhost`

## CI/CD

CI/CD пайплайн настроен через GitLab CI:

* Автоматическая сборка и деплой происходят при пуше в ветку `dev`
* SSH-доступ по ключу используется для деплоя на сервер
* Выполняется остановка, обновление и перезапуск сервисов с помощью `docker-compose`