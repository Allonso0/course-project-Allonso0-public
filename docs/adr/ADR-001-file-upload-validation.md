# ADR-001: File Upload Validation

Дата: 19.10.2025
Статус: Accepted

## Context

Сервис обрабатывает загрузку файлов (изображения, документы). Без правильной валидации это создаёт риски:

- Атаки path traversal (../../etc/passwd)
- Загрузка исполняемых файлов (PHP shells, скрипты)
- DoS через файлы больших размеров

Текущая реализация либо отсутствует, либо доверяет метаданным от пользователя.

## Decision

Внедрить многоуровневую валидацию загрузок:

1. **Magic Bytes Verification** - проверка сигнатур файлов вместо доверия MIME-типам
2. **Size Limits** - максимальный размер 5MB для изображений
3. **Secure Filename Generation** - использовать UUID вместо оригинальных имён
4. **Path Canonicalization** - предотвращение directory traversal
5. **Symlink Protection** - проверка на символьные ссылки в пути

Конфигурация:

- Максимальный размер: 5MB
- Разрешённые типы: PNG, JPEG
- Имя файла: UUIDv4 + расширение по типу
- Базовый каталог: строго разрешённая директория

## Consequences

### Positive

- Защита от path traversal атак
- Предотвращение загрузки исполняемых файлов
- Защита от DoS через большие файлы
- Устранение зависимости от ненадёжных client headers

### Negative

- Дополнительные 2-5ms на обработку каждого файла
- Увеличение кодовой базы на ~50-100 строк
- Требует поддержки новых форматов при расширении

### Trade-offs

Баланс между безопасностью и производительностью: magic bytes проверка добавляет overhead, но критична для безопасности.

## Security Impact

- **Mitigates**: F1 (Insecure File Upload), R2 (Path Traversal) из Threat Model
- **Supports**: NFR-03 (Input Validation), NFR-04 (File Handling)
- **Residual Risk**: Новые форматы файлов потребуют обновления валидации

## Rollout Plan

1. Реализовать в модуле `app/core/file_upload.py`
2. Создать endpoint в `app/api/endpoints/uploads.py`
3. Добавить маршрут в `app/api/routes.py`
4. Протестировать в staging с различными файлами
5. Мониторинг false positives в логах

## Links

- NFR-03, NFR-04
- F1, R2 из Threat Model
- tests/test_file_upload.py::test_file_upload_validation
- app/core/file_upload.py
- app/api/endpoints/uploads.py
