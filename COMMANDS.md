# 🚀 VectorAI - Команды запуска

## Быстрый старт

### 🤖 AI-разработка (рекомендуется)
```bash
make ai-dev
```
**Что происходит:**
- 🔄 Запускает PostgreSQL в фоне
- ⏳ Ждет готовности базы данных (5 сек.)
- 🚀 Запускает FastAPI с hot reload
- 🌐 Запускает Nginx для проксирования

**Особенности:**
- Hot reload для изменений в коде
- Быстрый запуск без фронтенда
- Оптимизирован для итеративной разработки
- API доступен: http://localhost/api/docs

### 🚀 Полная разработка
```bash
make dev
```
**Что происходит:**
- Запускает все сервисы одновременно
- Включает PostgreSQL + FastAPI + Nginx
- Hot reload включен

### 🏭 Продакшн
```bash
make prod
```
**Что происходит:**
- 🏗️ Собирает React фронтенд
- 🚀 Запускает все сервисы в продакшн режиме
- 🌐 Настраивает Nginx с статическими файлами
- 📊 Использует оптимизированные настройки

**После запуска доступно:**
- 🌐 Фронтенд: http://localhost
- 🔧 API: http://localhost/api/docs

## Управление сервисами

### ⏹️ Остановка
```bash
make stop
```
Останавливает все запущенные контейнеры (и dev, и prod)

### 🔄 Перезапуск
```bash
make restart
```
Останавливает все сервисы и запускает продакшн

### 📊 Статус
```bash
make status
```
Показывает статус всех контейнеров

## Логи и отладка

### 📝 Логи продакшн
```bash
make logs
```

### 📝 Логи разработки
```bash
make logs-dev
```

### 🧹 Полная очистка
```bash
make clean
```
**Внимание:** Удаляет все контейнеры, volumes и неиспользуемые образы!

## Рекомендуемый workflow

### Для AI-разработки:
```bash
# Запуск для быстрой итерации
make ai-dev

# Просмотр логов в отдельном терминале
make logs-dev

# После завершения работы
make stop
```

### Для тестирования продакшн:
```bash
# Запуск продакшн окружения
make prod

# Проверка статуса
make status

# Просмотр логов
make logs

# Остановка
make stop
```

### Для деплоя:
```bash
# Очистка от предыдущих версий
make clean

# Запуск продакшн
make prod

# Проверка что все работает
make status
```

## Порты и адреса

| Сервис | Development | Production | Описание |
|--------|------------|------------|----------|
| **Frontend** | - | http://localhost | React приложение |
| **API** | http://localhost/api | http://localhost/api | FastAPI REST API |
| **API Docs** | http://localhost/api/docs | http://localhost/api/docs | Swagger документация |
| **Database** | localhost:5432 | localhost:5432 | PostgreSQL |

## Структура команд

```
🚀 VectorAI Development Commands

Development:
  make dev     - Start full development environment
  make ai-dev  - Start AI development environment with hot reload

Production:
  make prod    - Start production environment with Nginx

Control:
  make stop    - Stop all running services
  make restart - Restart all services
  make status  - Show status of all services

Utilities:
  make clean   - Stop and remove all containers
  make logs    - Show logs from all services
  make logs-dev - Show logs from development services
  make test    - Run tests (placeholder)
```

## Требования

- Docker
- Docker Compose
- Make
- Файл `.env` с настройками базы данных

## Troubleshooting

### Проблемы с запуском:
```bash
# Проверить статус
make status

# Посмотреть логи
make logs-dev  # или make logs

# Полная перезагрузка
make clean
make ai-dev
```

### База данных не готова:
```bash
# ai-dev автоматически ждет готовности БД
# Если проблемы остаются, увеличьте задержку в Makefile
```

### Порты заняты:
```bash
# Остановить все сервисы
make stop

# Проверить что порты свободны
lsof -i :80 -i :8000 -i :5432
``` 