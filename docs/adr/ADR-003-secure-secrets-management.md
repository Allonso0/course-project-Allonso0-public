# ADR-003: Secure Secrets Management

Дата: 19.10.2025
Статус: Accepted

## Context

Сервис требует доступа к чувствительным данным (API keys, database credentials, JWT secrets).

Текущие проблемы:

- Секреты могут попадать в код/репозиторий
- Нет ротации секретов
- Раскрытие в логах при ошибках
- Сложность управления разными окружениями

Риски:

- Компрометация секретов через git history
- Утечки через error messages
- Отсутствие audit trail для доступа

## Decision

Внедрить многоуровневую стратегию управления секретами:

1. **Источники секретов**: Environment Variables + Vault (в будущем)
2. **Валидация при старте**: проверка наличия обязательных секретов
3. **Маскирование в логах**: автоматическое скрытие секретов
4. **Ротация**: поддержка multiple keys для graceful rotation

**Конфигурация:**

- Обязательные переменные: `APP_JWT_SECRET`, `APP_DATABASE_URL`, `APP_API_KEY`
- Опциональные: `APP_VAULT_ADDR`, `APP_VAULT_TOKEN` для будущей миграции
- Префикс: `APP_` для consistency

**Реализация:**

- Класс `SecretsManager` для централизованного доступа
- Валидация при инициализации приложения
- Middleware для маскирования в логах
- Поддержка тестовой среды

## Consequences

### Positive

- Предотвращение accidental exposure
- Централизованное управление конфигурацией
- Подготовка к миграции на Vault/KMS
- Улучшенная security posture

### Negative

- Усложнение setup для development
- Дополнительная валидация при запуске
- Необходимость документации для env variables

### Trade-offs

Баланс между security и developer experience: строгая валидация улучшает security, но требует больше конфигурации.

## Security Impact

- **Mitigates**: F2 (Secrets Exposure), R3 (Credential Leak) из Threat Model
- **Supports**: NFR-05 (Secrets Management), NFR-06 (Audit)
- **Residual Risk**: Environment variables менее secure чем dedicated secrets storage

## Test Environment Considerations

В тестовой среде:

- Обязательные секреты автоматически получают тестовые значения
- Валидация секретов пропускается
- Маскирование в логах отключено
- Тесты запускаются без ручной настройки переменных окружения

## Rollout Plan

1. Реализовать SecretsManager в `app/core/secrets.py`
2. Интегрировать инициализацию в `app/main.py`
3. Настроить тестовые переменные в `tests/conftest.py`
4. Создать `.env.example` для документации
5. Постепенная миграция существующих секретов

## Links

- NFR-05, NFR-06
- F2, R3 из Threat Model
- tests/test_secrets.py::test_secret_validation
- app/core/secrets.py
- app/main.py (инициализация)
- tests/conftest.py (тестовые переменные)
- .env.example (документация)
