# **Adrobot**

Веб-приложение для создания и редактирования рекламных кампаний Keitaro.

## **Стек**

- Backend: Python, FastAPI, SQLAlchemy 2, Alembic
- Database: PostgreSQL
- Frontend: React, TypeScript, Vite
- HTTP-клиент: Axios
- Запуск: Docker Compose
- Интеграция: Keitaro API

## **Требования**

- Docker Engine
- Docker Compose
- Доступ к Keitaro API

## **Установка и запуск**

1\. Создайте файл окружения:

`cp .env.example .env`

2\. Укажите параметры подключения в `.env`:

- `DATABASE_URL`
- `KEITARO_BASE_URL`
- `KEITARO_API_KEY`

3\. Соберите и запустите базу данных и backend:

`docker compose up --build -d db backend`

4\. Примените миграции:

`docker compose exec backend alembic upgrade head`

5\. Соберите и запустите frontend:

`docker compose up --build -d frontend`

## **Адреса**

- Frontend: [http://localhost:5173](http://localhost:5173?utm_source=chatgpt.com)
- Backend API: [http://localhost:8000](http://localhost:8000?utm_source=chatgpt.com)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs?utm_source=chatgpt.com)
- Health check: [http://localhost:8000/health](http://localhost:8000/health?utm_source=chatgpt.com)

## **Возможности**

### **Создание кампании**

- Выбор оффера из каталога Keitaro.
- Получение GEO из выбранного оффера.
- Выбор домена, группы и источника трафика.
- Создание кампании и двух потоков: `Geo → Google` и `Offers`.

### **Редактирование кампании**

- Получение списка кампаний.
- Просмотр потоков и GEO-фильтров.
- Просмотр офферов и их долей.
- Добавление и удаление офферов.
- Перераспределение долей между офферами.

## **Тестирование**

Запуск backend-тестов:

`docker compose exec -T backend python -m unittest discover -s /app/tests -v`

## **Интеграция с Keitaro**

Интеграционный клиент находится в `backend/app/services/keitaro.py`.

Перед использованием реальных операций необходимо сверить URL, методы, поля запросов и форматы ответов с документацией API конкретной установки Keitaro.

API-ключ храните только в `.env`. Не публикуйте и не добавляйте этот файл в репозиторий.

## **Структура проекта**

- `backend/app/api` — HTTP endpoints.
- `backend/app/services` — бизнес-логика и интеграция Keitaro.
- `backend/app/models` — модели SQLAlchemy.
- `backend/alembic` — миграции базы данных.
- `backend/tests` — автоматические тесты.
- `frontend/src` — исходный код интерфейса.