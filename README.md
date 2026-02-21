# Personal Site (FastAPI)

Личный сайт-портфолио на FastAPI + Jinja2 с мультиязычным контентом (`ru/en`) и PostgreSQL.

## Stack
- FastAPI
- SQLAlchemy
- Alembic
- Jinja2 templates
- Docker / docker-compose

## 1) Быстрый запуск (Docker)
1. Создай `.env` в корне:
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/personal_site
   SECRET_KEY=change-me-in-production
   ```
2. Подними контейнеры:
   ```bash
   docker compose up --build
   ```
3. Открой сайт: `http://localhost:8000`

## 2) Локальный запуск (без Docker)
1. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Задай переменные окружения:
   ```bash
   export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/personal_site"
   export SECRET_KEY="local-dev-secret"
   ```
3. Примени миграции:
   ```bash
   alembic upgrade head
   ```
4. Запусти приложение:
   ```bash
   uvicorn app.main:app --reload
   ```

## 3) Проверки
- Проверка синтаксиса Python:
  ```bash
  python -m compileall app alembic static/js
  ```
- Smoke-import приложения:
  ```bash
  DATABASE_URL=sqlite:///./test.db SECRET_KEY=test-secret python - <<'PY'
  from app.main import app
  print(app.title)
  PY
  ```

## 4) Структура проекта
- `app/` — backend-код (роуты, модели, auth, DB)
- `templates/` — Jinja-шаблоны страниц
- `static/` — CSS/JS/контент (`static/content/*.json`)
- `alembic/` — миграции БД

## 5) Примечания по безопасности
- `SECRET_KEY` обязателен и не должен быть публичным.
- Значения в `docker-compose.yml` для Postgres подходят для локальной разработки, но не для production.
