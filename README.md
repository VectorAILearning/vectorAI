# VectorAI

Минимальная система авторизации с FastAPI backend и React frontend.

## 🚀 Быстрый старт

### Для AI разработки
```bash
make ai-dev
cd frontend && npm run dev
```

### Для локальной разработки
```bash
make dev
```

### Для production
```bash
make prod
```

## 📋 Возможности

- ✅ **Регистрация пользователей** с email верификацией
- ✅ **Авторизация** с JWT токенами
- ✅ **Восстановление пароля** через email
- ✅ **Профиль пользователя** с возможностью редактирования
- ✅ **Современный UI** с темной/светлой темой
- ✅ **Docker deployment** для production

## 🏗️ Архитектура

### Backend
- **FastAPI** - современный Python веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - основная база данных
- **JWT** - авторизация через токены
- **Alembic** - миграции базы данных

### Frontend
- **React** + **TypeScript** - современный UI
- **Redux Toolkit** - управление состоянием
- **React Router** - маршрутизация
- **Tailwind CSS** + **DaisyUI** - стилизация

### Deployment
- **Docker** + **Docker Compose** - контейнеризация
- **Nginx** - reverse proxy и статика
- **UV** - быстрый Python package manager

## 🛠️ Команды

```bash
# Помощь
make help

# Разработка
make dev      # Полная среда разработки
make ai-dev   # Backend в Docker + frontend локально

# Production  
make prod     # Запуск production версии

# Утилиты
make clean    # Очистка контейнеров
make logs     # Просмотр логов
```

## 📁 Структура проекта

```
vectorAI/
├── backend/               # FastAPI приложение
│   ├── pyproject.toml    # Python зависимости
│   ├── uv.lock          # Блокировка зависимостей  
│   ├── .venv/           # Виртуальное окружение
│   ├── Dockerfile       # Docker сборка
│   └── app/
│       ├── api/v1/      # API роуты
│       ├── core/        # Конфигурация
│       ├── models/      # SQLAlchemy модели
│       ├── schemas/     # Pydantic схемы
│       ├── services/    # Бизнес логика
│       ├── utils/       # Утилиты
│       └── migrations/  # Alembic миграции
├── frontend/             # React приложение
│   ├── package.json     # Node.js зависимости
│   ├── Dockerfile       # Docker сборка
│   └── src/
│       ├── components/  # React компоненты
│       ├── pages/       # Страницы
│       ├── store/       # Redux store
│       └── layouts/     # Layouts
├── scripts/              # Скрипты запуска
├── nginx/               # Nginx конфигурация
├── docker-compose.yml   # Production
├── docker-compose-dev.yml # Development
└── Makefile            # Команды разработки
```

## 🔧 Переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Database
AILEARNING_POSTGRES_USER=postgres
AILEARNING_POSTGRES_PASSWORD=password
AILEARNING_POSTGRES_DB=ailearning
AILEARNING_POSTGRES_PORT=5432

# API
JWT_SECRET_KEY=your-secret-key
DOMAIN=http://localhost

# Email (для восстановления пароля)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
```

## �� API Endpoints

- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `POST /api/v1/auth/logout` - Выход
- `POST /api/v1/auth/forgot-password` - Восстановление пароля
- `POST /api/v1/auth/reset-password` - Сброс пароля
- `GET /api/v1/auth/verify-email` - Верификация email

API документация доступна по адресу: `http://localhost:8000/api/docs`

## 🎯 Следующие шаги

Система готова для расширения:
- Добавление ролей и разрешений
- Интеграция с внешними сервисами
- Добавление новых функций
- Настройка CI/CD

---

**VectorAI** - простая, но мощная основа для веб-приложений! 🚀
