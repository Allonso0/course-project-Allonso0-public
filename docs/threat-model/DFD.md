# DFD — Data Flow Diagram

## Контекстная диаграмма

```mermaid
flowchart TD
    USER[User / Browser] -->|F1: HTTPS API Calls| API[Reading List API]
    API -->|F2: Database Queries| DB[(SQLite/PostgreSQL)]
```

## Логическая архитектура с TB

```mermaid
flowchart LR
    subgraph CLIENT [Trust Boundary: Client]
        USER[User / Browser]
    end

    USER -->|F1: HTTPS Request| GW[API Gateway<br/>FastAPI]

    subgraph EDGE [Trust Boundary: Edge]
        GW -->|F2: Authenticated Request| AUTH[Auth Service]
        AUTH -->|F3: JWT Validation| SVC[Entries Service]
    end

    subgraph CORE [Trust Boundary: Core]
        SVC -->|F4: Data Validation| VAL[Validation Service]
        VAL -->|F5: Valid Data| SVC
        SVC -->|F6: DB Operations| DB[(Database)]
    end

    subgraph DATA [Trust Boundary: Data]
        DB
    end

    %% External Dependencies
    SVC -->|F7: Error Logging| LOG[Logging Service]
    AUTH -->|F8: Password Verification| CRYPTO[Crypto Service]
```

## Процессы

```mermaid
flowchart TD
    U[User] -->|F9: POST /login<br/>username, password| L[Login Process]
    L -->|F10: Validate Credentials| VC[Credential Validation]
    VC -->|F11: Verify Password Hash| VH[Hash Verification]
    VH -->|F12: Generate JWT| TJ[JWT Generation]
    TJ -->|F13: Return Token| U

    VC -->|F14: Log Failed Attempts| FL[Failure Logging]
    VH -->|F15: Update Login Stats| LS[Login Statistics]
```

## Описание потоков даных

| Flow ID |Описание | Канал/Протокол | Данные |
|---------|----------|-----------------|--------|
|F1 | API вызовы от клиента | HTTPS/JSON | Запросы, заголовки |
|F2 | Аутентифицированные запросы | Internal/JSON | JWT, user_id |
|F3| Валидация JWT | Internal | Token verification |
|F4| Валидация данных | Internal | Title, link, kind, status |
|F5| Валидированные данные | Internal | Clean data objects |
|F6| Операции с БД | SQL | Queries, transactions |
|F7| Логирование ошибок | Internal | Error objects, stack traces |
|F8| Верификация паролей | Internal | Hash comparison |
|F9| Запрос на аутентификацию | HTTPS/JSON | username, password |
|F10 | Проверка учетных данных | Internal | Credential validation |
|F11 | Верификация хэша пароля | Internal | Hash comparison |
|F12 | Генерация JWT токена | Internal | Token creation |
|F13 | Возврат токена клиенту | HTTPS/JSON | JWT token |
|F14 | Логирование неудачных попыток | Internal | Failed login data |
|F15 | Обновление статистики логинов | Internal | Login statistics |
