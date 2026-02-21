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
3. Примени миграции:
   ```bash
   docker compose exec web alembic upgrade head
   ```
4. Открой сайт: `http://localhost:8000`

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
4. Создай админа (один раз):
   ```bash
   python - <<'PY'
   from app.database import SessionLocal
   from app.models import User
   from app.auth import hash_password

   db = SessionLocal()
   if not db.query(User).filter(User.username == 'admin').first():
       db.add(User(username='admin', hashed_password=hash_password('CHANGE_ME'), is_admin=True))
       db.commit()
   db.close()
   PY
   ```
5. Запусти приложение:
   ```bash
   uvicorn app.main:app --reload
   ```

## 3) Проверки
- Проверка синтаксиса Python:
  ```bash
  python -m compileall app alembic static/js
  ```
- Проверка health endpoint:
  ```bash
  curl -s http://localhost:8000/healthz
  ```

## 4) Структура проекта
- `app/` — backend-код (роуты, модели, auth, DB)
- `templates/` — Jinja-шаблоны страниц
- `static/` — CSS/JS/контент (`static/content/*.json`)
- `alembic/` — миграции БД

## 5) Примечания по безопасности
- `SECRET_KEY` обязателен и не должен быть публичным.
- Перед production обязательно поменяй пароль администратора и убери значения по умолчанию.
- Значения в `docker-compose.yml` для Postgres подходят для локальной разработки, но не для production.
- Для всех POST-форм используется CSRF-токен, но рекомендуется дополнительно настроить reverse-proxy rate limiting.
