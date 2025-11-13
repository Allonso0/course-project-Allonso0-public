# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS build

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование файлов зависимостей
COPY requirements-prod.txt .

# Установка зависимостей в wheels
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip && \
    pip wheel --wheel-dir=/wheels -r requirements-prod.txt

# Финальный образ
FROM python:3.12-slim AS runtime

# Установка curl для healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Переменные окружения для Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Создание non-root пользователя
RUN groupadd -r app && useradd -r -g app app

# Создание директории для загрузок
RUN mkdir -p /app/uploads && chown -R app:app /app/uploads

# Копирование wheels из этапа build
COPY --from=build /wheels /wheels

# Установка зависимостей из wheels
RUN --mount=type=cache,target=/root/.cache \
    pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Копирование исходного кода приложения
COPY app/ ./app/
COPY pyproject.toml .

# Настройка прав доступа
RUN chown -R app:app /app

# Переключение на non-root пользователя
USER app

# Healthcheck с использованием curl (более надежный)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Открытие порта
EXPOSE 8000

# Команда запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
