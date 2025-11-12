FROM python:3.12-slim
RUN adduser --disabled-password --gecos '' --uid 1001 botuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R botuser:botuser /app

USER botuser
CMD ["python", "main.py"]