 booking-platform

Монорепозиторий с двумя сервисами: `workspaces` и `events`.
Python 3.14, менеджер зависимостей — [uv](https://docs.astral.sh/uv/).

## Установка окружения

```bash
uv lock          # только при первом создании репозитория (создаёт файл uv.lock)
uv sync          # создаёт .venv, ставит зависимости строго по uv.lock
cp .env.example .env   # и поменять содержимое .env на локальные значения
```

uv сам скачает Python 3.14 по `.python-version`, если его нет.

## Проверки

Сервисы содержат одноимённые пакеты `app`, поэтому проверки запускаются
для каждого сервиса отдельно.

### workspaces

```bash
uv run pytest -o pythonpath=services/workspaces services/workspaces/tests
uv run ruff check services/workspaces
uv run ruff format --check services/workspaces
uv run mypy services/workspaces/app
```

### events

```bash
uv run pytest -o pythonpath=services/events services/events/tests
uv run ruff check services/events
uv run ruff format --check services/events
uv run mypy services/events/app
```

## Зависимости

```bash
uv add <package>             # зависимость приложения
uv add --dev <package>       # инструмент разработки
```

После изменения коммитьте `pyproject.toml` и `uv.lock` вместе.
