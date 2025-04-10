#!/bin/bash

set -e  # Выход при ошибке

# Функция ожидания PostgreSQL
wait_for_postgres() {
  echo "Ожидание подключения к PostgreSQL на $POSTGRES_HOST:$POSTGRES_PORT..."
  until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
    sleep 1
  done
  echo "✅ PostgreSQL готов!"
}

# Ждём PostgreSQL и Redis
wait_for_postgres
echo "Ожидание Redis (простая задержка)..."
sleep 2

## Миграции
#echo "Применение миграций Alembic..."
#alembic upgrade head

# Запуск приложения
echo "Запуск uvicorn..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

