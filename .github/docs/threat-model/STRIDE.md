# STRIDE — Угрозы и контроли

| Поток/Элемент | Угроза (S/T/R/I/D/E) | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|-----------|----------|---------------|-------------------|
| **F1: HTTPS Request** | **S: Spoofing** | Злоумышленник выдает себя за легитимного пользователя | JWT аутентификация, проверка токенов | NFR-01, NFR-10 | Unit-тесты аутентификации, интеграционные тесты JWT |
| **F1: HTTPS Request** | **T: Tampering** | Изменение данных запроса в transit | HTTPS/TLS, проверка целостности данных | NFR-03 | SSL/TLS сертификаты, тесты валидации данных |
| **F1: HTTPS Request** | **I: Information Disclosure** | Перехват конфиденциальных данных | HTTPS шифрование, маскирование чувствительных данных | NFR-09 | Security headers проверка, тесты маскирования логов |
| **F1: HTTPS Request** | **D: Denial of Service** | Flood запросов для недоступности сервиса | Rate limiting, WAF защита | NFR-02, NFR-11 | Нагрузочное тестирование, мониторинг метрик доступности |
| **F2: Authenticated Request** | **S: Spoofing** | Подделка JWT токена | Проверка подписи токена, валидация exp времени | NFR-10 | Тесты валидации JWT, проверка подписи токенов |
| **F2: Authenticated Request** | **E: Elevation of Privilege** | Попытка доступа к данным других пользователей | Проверка прав доступа, user_id в токене | NFR-05 | E2E тесты изоляции данных, penetration testing |
| **F3: JWT Validation** | **T: Tampering** | Модификация JWT payload | Цифровая подпись токена | NFR-10 | Тесты на модификацию JWT, проверка сигнатуры |
| **F4: Data Validation** | **T: Tampering** | Инъекция невалидных данных | Строгая валидация входных данных | NFR-03, NFR-04 | NFR валидационные тесты, SQL injection тесты |
| **F4: Data Validation** | **I: Information Disclosure** | Утечка данных через error messages | Унифицированные error responses | NFR-09 | Тесты error handling, проверка RFC7807 compliance |
| **F6: DB Operations** | **T: Tampering** | SQL injection атаки | Parameterized queries, ORM | NFR-03 | SQL injection тесты, security code review |
| **F6: DB Operations** | **I: Information Disclosure** | Несанкционированный доступ к БД | RBAC, минимальные привилегии | NFR-05 | Тесты прав доступа, аудит БД permissions |
| **F7: Error Logging** | **I: Information Disclosure** | Логирование чувствительных данных | Фильтрация sensitive data в логах | NFR-09 | Тесты логгирования, проверка отсутствия sensitive data |
| **F8: Password Verification** | **I: Information Disclosure** | Утечка хэшей паролей | Secure hashing (bcrypt), salt | NFR-01 | Unit-тесты хэширования, проверка bcrypt параметров |
| **F9: POST /login** | **S: Spoofing** | Brute-force атака на логин | Rate limiting, account lockout | NFR-02 | Интеграционные тесты rate limiting, нагрузочное тестирование |
| **F9: POST /login** | **I: Information Disclosure** | Перехват учетных данных | HTTPS, не логировать пароли | NFR-09 | Security headers проверка, аудит логов на пароли |
| **F10: Validate Credentials** | **I: Information Disclosure** | Timing attack на проверку пароля | Constant-time comparison | NFR-01 | Профилирование времени выполнения, security testing |
| **F11: Verify Password Hash** | **T: Tampering** | Подмена хэша пароля | Secure hash verification | NFR-01 | Тесты верификации хэшей, проверка salt |
| **F12: Generate JWT** | **I: Information Disclosure** | Weak JWT секреты | Strong secrets, регулярная ротация | NFR-10 | Проверка длины секретов, тесты ротации ключей |
| **F14: Log Failed Attempts** | **I: Information Disclosure** | Логи содержат IP адреса | Анонимизация логов | NFR-09 | Тесты анонимизации логов |

## Обоснование исключений

### Неприменимые угрозы

1. **Repudiation для F1-F8** - Основные потоки данных уже покрыты логированием через NFR-07
2. **Elevation of Privilege для F3, F4** - Эти процессы не связаны с правами доступа
3. **Denial of Service для внутренних потоков** - Внутренние коммуникации защищены сетевой изоляцией

## Связь с NFR из P03

Все контроли ссылаются на соответствующие NFR требования:

- **NFR-01** - Безопасность аутентификации (bcrypt, JWT)
- **NFR-02** - Защита от перебора (rate limiting)
- **NFR-03** - Валидация входных данных (SQL injection protection)
- **NFR-04** - Строгая типизация (data validation)
- **NFR-05** - Изоляция данных (authorization)
- **NFR-07** - Надежность операций (audit logging)
- **NFR-09** - Защита конфиденциальных данных (encryption, masking)
- **NFR-10** - JWT безопасность (token management)
- **NFR-11** - Доступность сервиса (DoS protection)
