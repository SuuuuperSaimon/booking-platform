# Booking Platform

Учебный монорепозиторий с двумя независимыми HTTP-сервисами: `workspaces` и `events`.
Каждый сервис имеет собственную базу и пользователя PostgreSQL.

Стек: Python 3.14, [uv](https://docs.astral.sh/uv/), Gunicorn, PostgreSQL 17,
psycopg, argon2-cffi, Yoyo Migrations. Приложения написаны без веб-фреймворка.

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
Адреса `8001` и `8002` являются базовыми адресами API, а не страницами сайта:
для проверки доступности открывайте `/health`. Этот маршрут не проверяет БД.
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
| Изменить Python-код одного из сервисов | Сохранить файл; Gunicorn перезагрузит приложение автоматически |
| Применить изменения зависимостей или Dockerfile | `docker compose up -d --build` |
| Применить изменения Compose или переменных `.env` | `docker compose up -d` |
| Посмотреть состояние контейнеров | `docker compose ps -a` |
| Смотреть свежие логи обоих API | `docker compose logs --since=1m -f workspaces events` |
| Посмотреть последние ошибки Workspaces | `docker compose logs --tail=100 workspaces` |
| Посмотреть логи PostgreSQL | `docker compose logs --tail=60 postgres` |
| Остановить проект и удалить контейнеры, сохранив именованный том | `docker compose down` |

В режиме разработки каталог `services/workspaces` подключён к Workspaces,
а `services/events` к Events. Подключение доступно контейнеру только для чтения.
Окружение `.venv` остаётся внутри образа и не перекрывается локальными файлами.

После изменения Python-файлов в этих каталогах не нужно запускать Docker заново.
Перезагрузка Gunicorn и ошибки импорта видны в логах. Синтаксическая ошибка может
помешать перезапуску приложения; исправьте файл и проверьте логи.

После получения изменений из Git пересобирайте образы, если изменились
`pyproject.toml`, `uv.lock`, Dockerfile или файлы за пределами подключённых
каталогов, которые нужны внутри контейнера. Изменения схемы БД применяйте
отдельной командой миграций. Обычный `docker compose restart` не применяет
новую конфигурацию Compose и не заменяет образ контейнера.

### Запуск без режима разработки

Чтобы не подключать override, явно укажите только основной файл:

```bash
docker compose -f compose.yaml up -d --build
```

В этом режиме Gunicorn работает без `--reload`, а код берётся из образа.
Изменения исходников требуют пересборки и пересоздания контейнеров.
Чтобы вернуться в режим разработки, выполните `docker compose up -d` без `-f`.
Эта команда переключает режим запуска, но не делает конфигурацию автоматически
готовой для публичного production-развёртывания.

## Миграции

Из корня репозитория выполните:

```bash
make migrate-workspaces
```

Команда применяет все новые миграции Workspaces. PostgreSQL должен быть запущен,
а база и пользователь уже созданы скриптом инициализации.
Команда не создаёт базы и пользователей. Python и Yoyo на компьютере
устанавливать не нужно.

Команда собирает актуальный образ и запускает Yoyo во временном контейнере
`workspaces`. Настройки подключения берутся из окружения сервиса, заданного
в Compose. В режиме разработки SQL-файлы из `services/workspaces/migrations`
доступны через подключённый каталог; без override они берутся из образа.
Вручную подключать каталог через `-v` не требуется. Пересоздавать работающий
HTTP-сервис для миграций не нужно. Наличие `--build` в команде Makefile
не означает, что образ нужно вручную пересобирать после каждого изменения Python.

Для выбора ревизии укажите имя файла без `.sql`:

```bash
make migrate-workspaces REVISION=001_users
```

Yoyo применит выбранную миграцию и её ещё не применённые зависимости.
Уже выполненные миграции не запускаются повторно. Выбор более ранней ревизии
не откатывает последующие миграции.

Для Events в Makefile предусмотрены `make migrate-events` и параметр `REVISION`.
Сейчас каталог `services/events/migrations` и SQL-файлы Events ещё не добавлены:
используйте эту команду после появления миграций модуля. Успешный запуск
инструмента без файлов миграций не подтверждает создание таблиц.

Yoyo и его зависимости зафиксированы в `pyproject.toml` и `uv.lock`.
Уже выполненные миграции учитываются в таблице `_yoyo_migration` и при
повторном запуске пропускаются. Остальные служебные таблицы Yoyo
(`_yoyo_log`, `_yoyo_version`, `yoyo_lock`) также не следует удалять вручную.

Для следующего изменения добавьте новый SQL-файл, например `002_workspaces.sql`,
и снова выполните `make migrate-workspaces`. В начале новой миграции укажите
зависимость от предыдущей, например `-- depends: 001_users`.
Уже применённые файлы не редактируйте. Для отката нужен отдельный файл
`<имя_миграции>.rollback.sql`; текущая `001_users.sql` обратного файла не имеет.

## Ручная проверка через Postman

Сначала запустите проект. В Postman отправьте запросы без авторизации:

| Метод | Адрес | Ожидаемый результат |
| --- | --- | --- |
| GET | `http://localhost:8001/health` | HTTP `200`, JSON `{"status":"ok"}` |
| GET | `http://localhost:8002/health` | HTTP `200`, JSON `{"status":"ok"}` |
| GET | `http://localhost:8001/unknown` | HTTP `404` |
| GET | `http://localhost:8002/unknown` | HTTP `404` |

## Автоматические проверки

Postman используется для ручных запросов. Автоматические проверки выполняются
через pytest, ruff и mypy внутри временных контейнеров.
Запуск `run` ниже заменяет команду Gunicorn командой проверки.

С `compose.override.yaml` проверки видят актуальные исходники через подключённые
каталоги: пересобирать образы после изменения только Python-кода не нужно.
После изменения зависимостей или Dockerfile сначала выполните `docker compose build`.
Без override исходники берутся из образа и после изменения кода также нужна сборка.

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

В Git хранятся `.env.example`, `compose.yaml`, `compose.override.yaml`, `Makefile`,
`docker/Dockerfile`, `docker/postgres/init.sh`, `.dockerignore`, `pyproject.toml`,
`uv.lock` и код сервисов. Общий override нужен обоим разработчикам;
не добавляйте в него личные пароли или абсолютные пути своего компьютера.
Локальный `.env` исключён через `.gitignore`.
Корневой `.dockerignore` должен исключать `.env`, `.venv` и `.git` из сборки образов.

## Если запуск не удался

- `variable is not set`: проверьте наличие корневого `.env`, заполненность значений и совпадение имён с Compose.
- Контейнер Python имеет статус `Exited`: посмотрите его логи через `docker compose logs workspaces` или `docker compose logs events`.
- `Failed to find attribute 'application'`: проверьте точку входа в `app/wsgi.py` соответствующего сервиса. Для класса `App` с методом `__call__` на уровне модуля нужен объект `application = App()`, вне класса.
- Код в контейнере не обновляется: убедитесь, что запускаете Compose без `-f compose.yaml`, чтобы подключился dev-override. После добавления или изменения override выполните `docker compose up -d`; одного `restart` недостаточно.
- Образ уже пересобран, но контейнер использует старый: выполните `docker compose up -d --no-deps --force-recreate workspaces` либо аналогичную команду для `events`. Для применения новых зависимостей одного `--reload` недостаточно.
- Сообщение `CACHED` при сборке нормально: Docker повторно использует неизменившиеся слои. Оно само по себе не означает, что работает старый код.
- Скрипт создания баз завершился ошибкой: проверьте `docker compose logs postgres`. Перезапуск уже инициализированного PostgreSQL автоматически не продолжает этот скрипт.
- Ошибка запуска `init.sh` как исполняемого файла: проверьте, что он сохранён без флага исполнения. На macOS/Linux это настраивается командой `chmod 644 docker/postgres/init.sh`; после частичной инициализации отдельно требуется завершить настройку существующего сервера.
