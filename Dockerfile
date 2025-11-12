FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаём директорию для логов
RUN mkdir -p /app/log

# Запускаем main.py напрямую
CMD ["python", "main.py"]