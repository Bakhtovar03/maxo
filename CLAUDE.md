# CLAUDE.md

This file provides guidance to AI models (Claude Code, Cursor, Copilot, and others) when working with code in this repository.

## Обзор

maxo - асинхронный фреймворк для разработки ботов в max.ru. Портирован из aiogram, адаптирован под Max API. Python 3.12+.

## Команды

```bash
uv sync --group dev          # установить зависимости
just lint                    # ruff + codespell + bandit + slotscheck
just mypy                    # проверка типов
just test                    # pytest --cov src
just test-all                # nox (Python 3.12, 3.13, 3.14)
just all                     # lint + mypy + test-all
pytest tests/path/test_file.py::test_name -v   # один тест
```

## Архитектура

```text
src/maxo/
  bot/         - клиент бота и методы API
  routing/     - Dispatcher, Router, Handler, Filter, Middleware, сигналы
  dialogs/     - диалоговая система (порт aiogram_dialog): Window, Dialog, виджеты
  fsm/         - конечный автомат: State, StatesGroup, Storage
  transport/   - long-polling и webhook транспорт
  types/       - AUTO-GENERATED типы из Max API (не редактировать вручную)
  enums/       - AUTO-GENERATED перечисления (не редактировать вручную)
  integrations/ - dishka, magic_filter
  utils/       - билдеры, фасады, хелперы, форматирование
```

Ключевые паттерны:
- Router с вложенными роутерами, middleware, фильтрами
- FSM context + storage (Memory, Redis)
- Dialogs: высокоуровневая UI-абстракция поверх FSM
- Сериализация через adaptix
- Транспорт: long-polling или webhook (aiohttp/FastAPI)

## Правила оформления кода

- Только короткое тире `-`. Длинное `—`, среднее `–` и прочие нестандартные тире запрещены.
- Не добавлять `Co-Authored-By` в коммиты.
- Все docstrings на русском языке.
- В тестах не использовать длинные декоративные разделители (`# ########`, `# ----------` и т.п.).
- Коммиты: conventional commits (`fix:`, `feat:`, `docs:`, `chore:`), допускается русский язык в сообщении.
- Строки до 88 символов, двойные кавычки, отступы 4 пробела.
- Строгая типизация: mypy strict, все публичные API типизированы.
- `@dataclass(slots=True)` для дата-классов.

## Тесты

- pytest + pytest-asyncio (strict mode), coverage через `--cov=src`
- Async тесты: `@pytest.mark.asyncio`
- Моки: `unittest.mock.AsyncMock`, `MagicMock`
- Фикстуры в `conftest.py` или в самом файле теста
- В тестах не требуются type annotations и docstrings (отключено в ruff)
- Тесты диалогов: `BotClient`, `MockMessageManager`, `JsonMemoryStorage`, локаторы кнопок
