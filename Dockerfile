# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev postgresql-client curl && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

# Указываем порт
EXPOSE 8000

# Добавляем права на выполнение скрипта
RUN chmod +x start.sh

# Стартуем через shell-скрипт (будет ждать БД)
CMD ["./start.sh"]
