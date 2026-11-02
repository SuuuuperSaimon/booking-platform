# Booking Platform

Учебный монорепозиторий с двумя независимыми HTTP-сервисами: `workspaces` и `events`.
Каждый сервис имеет собственную базу и пользователя PostgreSQL.

Стек: Python 3.14, [uv](https://docs.astral.sh/uv/), Gunicorn, PostgreSQL 17,
psycopg, argon2-cffi. Приложения написаны без веб-фреймворка.

## Требования

- Git.
- Docker с Docker Compose; на macOS подходит Docker Desktop.

Python, uv, библиотеки и Gunicorn устанавливаются внутри образов.
Устанавливать Python и uv на компьютер для описанных ниже команд не требуется.
Все команды выполняются из корня репозитория.

## Первый запуск

После получения кода репозитория создайте свою локальную конфигурацию:

```bash
cp .env.example .env
```

Проверьте и заполните значения в `.env`. Затем соберите образы и запустите сервисы:

```bash
docker compose up -d --build
```

При сборке `uv sync --locked` устанавливает зависимости по `pyproject.toml` и
`uv.lock`. Разработчикам, получившим готовые изменения из Git, повторять
`uv add gunicorn` не требуется.

При первой инициализации PostgreSQL скрипт `docker/postgres/init.sh` автоматически
создаёт обе базы и пользователей, а также настраивает права доступа.
В репозитории этот файл должен храниться без флага исполнения — режим Git `100644`.
Официальный образ PostgreSQL выполняет такой `.sh` через свой Bash.

## Адреса сервисов

| Компонент | Адрес |
| --- | --- |
| Workspaces | http://localhost:8001 |
| Events | http://localhost:8002 |
| Adminer — интерфейс управления базами | http://localhost:8080 |
| PostgreSQL из контейнеров проекта | `postgres:5432` |

На текущем этапе `GET /health` каждого API должен возвращать HTTP `200` и JSON:

```json
{"status":"ok"}
```

Неизвестный путь должен возвращать HTTP `404`.
Порт PostgreSQL в текущем Compose не опубликован на Mac; для просмотра данных
можно использовать Adminer.

## Базы и настройки подключения

Один контейнер `postgres` обслуживает две отдельные базы приложений.
Значения по умолчанию из `.env.example`:

| Назначение | База | Пользователь |
| --- | --- | --- |
| Администрирование PostgreSQL | `postgres` | `postgres` |
| Workspaces | `workspaces_db` | `workspaces_user` |
| Events | `events_db` | `events_user` |

В `.env` настройки разделены на три группы:

- `POSTGRES_ADMIN_USER`, `POSTGRES_DEFAULT_DB`, `POSTGRES_ADMIN_PASSWORD` — первоначальная настройка администратора и начальной базы.
- `WORKSPACES_DB_NAME`, `WORKSPACES_DB_USER`, `WORKSPACES_DB_PASSWORD` — база приложения Workspaces.
- `EVENTS_DB_NAME`, `EVENTS_DB_USER`, `EVENTS_DB_PASSWORD` — база приложения Events.

Compose передаёт каждому Python-сервису его значения под общими именами
`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
Данные двух приложений и их подключения остаются раздельными.

В контейнере PostgreSQL переменные `POSTGRES_USER`, `POSTGRES_DB`,
`POSTGRES_PASSWORD` читает официальный образ. Дополнительные переменные с
префиксами `WORKSPACES_` и `EVENTS_` использует наш скрипт `init.sh`.

Для входа в Adminer выберите PostgreSQL, сервер `postgres` и учётные данные
нужного пользователя из `.env`. Для административного входа используйте
`POSTGRES_ADMIN_USER`, `POSTGRES_ADMIN_PASSWORD` и `POSTGRES_DEFAULT_DB`.

Данные PostgreSQL сохраняются в именованном томе `postgres_data`.
Скрипт инициализации выполняется только для пустого хранилища.
Изменение `.env` не переименовывает уже существующие базы и не меняет пароли
созданных пользователей; такие изменения применяются отдельно через SQL.

## Ежедневная работа

| Действие | Команда |
| --- | --- |
| Запустить проект с существующими образами | `docker compose up -d` |
| Применить изменения кода, зависимостей или Dockerfile | `docker compose up -d --build` |
| Посмотреть состояние контейнеров | `docker compose ps -a` |
| Посмотреть логи Python-сервисов | `docker compose logs -f workspaces events` |
| Посмотреть логи PostgreSQL | `docker compose logs --tail=60 postgres` |
| Остановить проект и удалить контейнеры, сохранив именованный том | `docker compose down` |

Сейчас код копируется в образы при сборке. Изменения файлов на компьютере
появляются в приложениях после пересборки образов и пересоздания контейнеров.
После обновления кода через Git также используйте команду с `--build`.

## Ручная проверка через Postman

Сначала запустите проект. В Postman отправьте запросы без авторизации:

| Метод | Адрес | Ожидаемый результат |
| --- | --- | --- |
| GET | `http://localhost:8001/health` | HTTP `200`, JSON `{"status":"ok"}` |
| GET | `http://localhost:8002/health` | HTTP `200`, JSON `{"status":"ok"}` |
| GET | `http://localhost:8001/unknown` | HTTP `404` |
| GET | `http://localhost:8002/unknown` | HTTP `404` |

По мере реализации добавляйте запросы регистрации, входа и бронирования
в общую коллекцию Postman. Эти маршруты появятся после написания соответствующего кода.

## Автоматические проверки

Postman используется для ручных запросов. Автоматические проверки выполняются
через pytest, ruff и mypy внутри временных контейнеров.
Запуск `run` ниже заменяет команду Gunicorn командой проверки.

После изменения кода сначала обновите образы:

```bash
docker compose build
```

Проверки запускаются отдельно для каждого сервиса. Параметр `pythonpath`
сохранён для текущей структуры тестов с импортами локального пакета `app`.

### Workspaces

```bash
docker compose run --rm --no-deps workspaces uv run --locked pytest -o pythonpath=services/workspaces services/workspaces/tests
docker compose run --rm --no-deps workspaces uv run --locked ruff check services/workspaces
docker compose run --rm --no-deps workspaces uv run --locked ruff format --check services/workspaces
docker compose run --rm --no-deps workspaces uv run --locked mypy services/workspaces/app
```

### Events

```bash
docker compose run --rm --no-deps events uv run --locked pytest -o pythonpath=services/events services/events/tests
docker compose run --rm --no-deps events uv run --locked ruff check services/events
docker compose run --rm --no-deps events uv run --locked ruff format --check services/events
docker compose run --rm --no-deps events uv run --locked mypy services/events/app
```

Для тестов функций без HTTP и БД постоянно работающие серверы не нужны.
Для будущих интеграционных тестов PostgreSQL понадобятся отдельные тестовые базы
и настройки подключения к ним. Текущий `init.sh` создаёт только базы приложений.

## Изменение зависимостей

Эти команды выполняет разработчик, который добавляет пакет.
Замените `PACKAGE_NAME` на его название.

Зависимость приложения:

```bash
docker compose run --rm --no-deps -v "$PWD:/project" -w /project workspaces uv add --no-sync PACKAGE_NAME
```

Инструмент разработки:

```bash
docker compose run --rm --no-deps -v "$PWD:/project" -w /project workspaces uv add --dev --no-sync PACKAGE_NAME
```

Команды обновляют `pyproject.toml` и `uv.lock` в рабочей папке проекта.
После изменения зависимостей пересоберите образы:

```bash
docker compose up -d --build
```

Коммитьте `pyproject.toml` и `uv.lock` вместе. Другой разработчик получает
эти изменения через Git и пересобирает образы; повторно добавлять пакет ему не нужно.

## Файлы конфигурации в Git

В Git хранятся `.env.example`, `compose.yaml`, `docker/Dockerfile`,
`docker/postgres/init.sh`, `.dockerignore`, `pyproject.toml`, `uv.lock` и код сервисов.
Локальный `.env` исключён через `.gitignore`.
Корневой `.dockerignore` должен исключать `.env`, `.venv` и `.git` из сборки образов.

## Если запуск не удался

- `variable is not set`: проверьте наличие корневого `.env`, заполненность значений и совпадение имён с Compose.
- Контейнер Python имеет статус `Exited`: посмотрите его логи через `docker compose logs workspaces` или `docker compose logs events`.
- Скрипт создания баз завершился ошибкой: проверьте `docker compose logs postgres`. Перезапуск уже инициализированного PostgreSQL автоматически не продолжает этот скрипт.
- Ошибка запуска `init.sh` как исполняемого файла: проверьте, что он сохранён без флага исполнения. На macOS/Linux это настраивается командой `chmod 644 docker/postgres/init.sh`; после частичной инициализации отдельно требуется завершить настройку существующего сервера.
