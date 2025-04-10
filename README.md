# One-time Secrets API

Сервис для **одноразового хранения и получения зашифрованных секретов**.  
Работает через FastAPI + PostgreSQL + Redis. Идеально подходит для безопасной передачи чувствительной информации — как Pastebin, но с автозачисткой и шифрованием.

## ⚙️ Стек технологий

- 🐍 Python 3.10
- 🚀 FastAPI
- 🐘 PostgreSQL
- 🔥 Redis
- 🐳 Docker + Docker Compose
- 🔐 Alembic (миграции)
- 🔁 TTL-чекер для автоматической зачистки просроченных секретов

---

## 📁 Структура проекта


```bash
    One-time-secrets/
    ├── src/
    │   ├── alembic/               # Каталог миграций Alembic
    │   │   ├── versions/          # Сгенерированные версии миграций
    │   │   ├── env.py             # Конфигурация Alembic
    │   │   └── script.py.mako     # Шаблон миграций
    │   ├── api/                   # API роуты FastAPI
    │   │   └── routers.py
    │   ├── db/                    # Работа с БД (модели, CRUD, конфиг)
    │   │   ├── config_db.py
    │   │   ├── crud.py
    │   │   └── models.py
    │   ├── redis/                 # Redis-клиент и шифрование
    │   │   ├── crypto.py
    │   │   └── redis_client.py
    │   ├── schemas/               # Pydantic-схемы
    │   │   └── secrets.py
    │   ├── tasks/                 # Фоновые задачи
    │   │   └── ttl_checker.py     # Чекер для TTL-секретов
    │   ├── main.py                # Точка входа в приложение
    │   └── middleware.py          # Пользовательские middleware
    ├── .dockerignore              # Исключения для Docker
    ├── .env                       # Переменные окружения (в .gitignore)
    ├── .gitignore                 # Исключения для Git
    ├── alembic.ini                # Настройка Alembic
    ├── docker-compose.yml         # Docker Compose конфигурация
    ├── Dockerfile                 # Dockerfile для сборки образа
    ├── README.md                  # Документация (ВЫ ТУТ)
    ├── requirements.txt           # Python-зависимости
    └── start.sh                   # Скрипт для локального запуска (опц.)
````




## 🛠 Установка и запуск

> 💡 Убедись, что установлен **Docker** и **docker-compose**.

```bash
# Клонируй репозиторий
git clone https://github.com/your-user/your-repo.git
cd your-repo

# Создай файл окружения
cp .env.example .env  # настрой его по образцу

# Собери и запусти проект
docker-compose up --build
```

После этого API будет доступен по адресу: http://localhost:8000 .

Документация Swagger: http://localhost:8000/docs

---

🛠 Переменные окружения (.env)
Пример содержимого:

```env

    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=one_time_secrets
    POSTGRES_HOST=postgres
    POSTGRES_PORT=5432
    
    REDIS_HOST=redis
    REDIS_PORT=6379
    
    SECRET_KEY=some-super-secret-key
    ENCRYPTION_KEY=32-bytes-key-in-base64
```
---

## 📡 Пример работы API

POST /secrets/ — сохранить секрет:

```json
    {
      "secret": "my super top secret",
      "ttl": 3600 // время жизни в секундах
    }
```
**Ответ:**

```json
    {
      "id": "a1b2c3d4"
    }
```
GET /secrets/{id} — получить и автоматически удалить:

```json
    {
      "secret": "my super top secret"
    }
```
---