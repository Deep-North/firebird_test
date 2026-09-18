# Firebird JOIN test (pytest + firebird-driver)
## Описание
Репозиторий содержит один автотест на pytest, проверяющий семантическое различие для LEFT JOIN при размещении предиката:

* предикат в ON сохраняет строки “левой” таблицы (outer join остаётся outer join)
* предикат в WHERE отфильтровывает строки с NULL справа и фактически превращает запрос в INNER JOIN-поведение

Тесткейс: LEFT JOIN: predicate in ON vs WHERE changes result.

## Требования
* Firebird 5.0
* Python >= 3.11
* pytest
* firebird-driver

## Тест использует переменные окружения (с дефолтами):

* FB_HOST (default: localhost)
* FB_PORT (default: 3050)
* FB_USER (default: SYSDBA)
* FB_PASSWORD (default: masterkey)
* FB_CHARSET (default: UTF8)

### Пример:

```BASH
export FB_HOST=localhost
export FB_PORT=3050
export FB_USER=SYSDBA
export FB_PASSWORD=masterkey
export FB_CHARSET=UTF8
```

## Запуск тестов
```bash
# минимальный вывод
pytest -q
# подробный вывод
pytest -v
```

## Структура
* test_join_left_on_vs_where.py — тест
* фикстура fb_db создаёт временную БД в tmp_path и выполняет teardown

## Что делает фикстура fb_db
1. Setup
* создаёт уникальный файл БД во временной директории pytest
* создаёт БД через create_database(...)
* открывает соединение и отдаёт его тесту

2. Teardown
* пытается выполнить DROP DATABASE
* закрывает соединение
* удаляет файл БД (best-effort, с ретраями при необходимости)

## Примечания по DDL
В Firebird DDL (например, CREATE TABLE) транзакционен.
Поэтому после создания таблиц в тесте выполняется COMMIT, чтобы метаданные стали видимы для последующих запросов.

