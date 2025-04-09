#!/bin/bash

# Ждем, пока БД и redis поднимутся
echo "⌛ Ожидание PostgreSQL и Redis..."
sleep 5

# Стартуем приложение
echo "🚀 Запуск uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
