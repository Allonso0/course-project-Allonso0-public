# ADR-002: RFC 7807 Error Response Standardization

Дата: 19.10.2025
Статус: Accepted

## Context

В настоящее время ошибки возвращаются в различных нестандартных форматах:

- Простые строковые сообщения
- Произвольные JSON структуры
- Иногда раскрываются ненужные детали (stack traces, paths)
- Нет correlation_id для трассировки

Это создаёт проблемы:

- Сложность дебага в проде
- Риск раскрытия чувствительной информации
- Плохой пользовательский опыт для пользователей API
- Нарушение принципа least information

## Decision

Принять стандарт RFC 7807 "Problem Details for HTTP APIs" для всех ошибок:

**Структура ответа:**

```json
{
  "type": "/errors/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "The requested resource was not found",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Реализация:

- Единый error handler middleware для всех типов исключений
- Маскирование деталей
- Обязательный correlation_id для трассировки
- Консистентные HTTP статус коды
- Content-Type: application/problem+json

Обработчики:

- ApiError - кастомные бизнес-ошибки
- RequestValidationError - ошибки валидации Pydantic
- HTTPException - стандартные HTTP ошибки
- StarletteHTTPException - 404, 405 и другие маршрутные ошибки
- Exception - глобальный обработчик неожиданных ошибок

## Consequences

### Positive

- Стандартизированный API для клиентов
- Улучшенная безопасность через маскирование деталей
- Упрощённая трассировка через correlation_id
- Соответствие индустриальным стандартам

### Negative

- Увеличение размера error responses
- Необходимость миграции существующих клиентов
- Дополнительная обработка для генерации correlation_id

### Trade-offs

Баланс между информативностью и безопасностью: в production скрываем детали, но сохраняем трассируемость.

## Security Impact

- **Mitigates**: F3 (Information Disclosure), R4 (Error Handling) из Threat Model
- **Supports**: NFR-02 (Error Handling), NFR-05 (Logging Standards)
- **Residual Risk**: Нужно следить чтобы correlation_id не содержал чувствительных данных

## Rollout Plan

1. Полная замена `app/core/errors.py`
2. Обновление обработчиков в `app/main.py`
3. Миграция существующих тестов на новый формат
4. Тестирование всех сценариев ошибок
5. Обновление документации API

## Links

- NFR-02, NFR-05
- F3, R4 из Threat Model
- tests/test_errors.py::test_rfc7807_error_format
- app/core/errors.py
- app/main.py
