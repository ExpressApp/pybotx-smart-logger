# pybotx-smart-logger

_Shows logs when you need it_


## Проблема/решение

В основном наши боты работают в закрытых контурах. Там невозможно использовать Sentry,
поэтому наш главный помощник в диагностике неполадок - логи контейнера.

Однако, если сделать логи слишком подробными, то действительно важную информацию будет
очень сложно найти. Также мы получим проблемы избыточного использования постоянной
памяти или слишком быструю ротацию логов. Но сделав логи слишком сжатыми, мы рискуем
столкнуться с ситуацией, когда их недостаточно для диагностики ошибки.

То есть хочется видеть как можно больше информации во время возникновения ошибок, и как
можно меньше - когда всё хорошо.


## Использование

Используя функцию `smart_log(log_message: str, log_item: Any = undefined)` логируете всю
информацию, которая поможет в диагностике ошибки. Если во время обработки сообщения
будет выброшено исключение, в логи попадёт:

1. Текущее сообщение от пользователя,
2. Вся залогированная с помощью `smart_log` информация,
3. Выброшенное исключение.

Если обработка сообщения завершится успешно, накопленные логи будут "выброшены".

В ботах часто используются фоновые задачи, исключения которых не могут быть перехвачены
хендлером. Для них используется `smart_logger_decorator`, позволяющий получить
аналогичное для обработки сообщений поведение.

Вы так же можете подлючить миддлварь для возможности логирования из FastAPI хендлеров. В таком случае, если во время обработки исключения будет выброшено ислючение, в логи попадет:

1. Метод
2. Урл запроса с query параметрами
3. Заголовки запроса

При необходимости, тело запроса нужно логировать в самом хендлере:
``` python
`smart_log(await request.json())`
```


## Режим отладки

Появление необходимых логов при возникновении ошибки очень удобно. Однако есть
ситуации, когда необходимо понаблюдать за нормальной работой кода. Тем более, что вызовы
`smart_log` уже расставлены. Поэтому для сообщений и фоновых задач предусмотрены функции
отладки.

`BotXSmartLoggerMiddleware` принимает пользовательскую функцию
`debug_enabled_for_message(message: Message) -> bool`, позволяющую включить режим отладки в
зависимости от входящего сообщения.

`make_smart_logger_decorator` принимает пользовательскую функцию
`debug_enabled_for_task(task_name: str) -> bool` позволяющую включить режим отладки в
зависимости от имени функции. `smart_logger_decorator` знает имя функции, которую он
оборачивает и передаёт его в `debug_enabled_for_task` в качестве аргумента.

Эти функции можно использовать для включения отладки через переменные окружения, стейт
бота, Redis, PostgreSQL и т.д. Рекомендую завести команды, которые позволят включать
режим отладки отправкой сообщения (см. пример ниже).

`FastApiSmartLoggerMiddleware` принимает аргумент `debug_enabled: bool`.


## Настройка

1. Устанавливаем библиотеку:  
```bash
poetry add pybotx-smart-logger
```

2. Подключаем мидлварь и хендлер исключений к боту. Хендлер должен быть подключен к
   типу Exception, т.е. заменяет подключенный в коробке `internal_error_handler`.

```python
from pybotx import Bot
from pybotx_smart_logger import make_smart_logger_exception_handler, BotXSmartLoggerMiddleware

from app.resources import strings

smart_logger_exception_handler = make_smart_logger_exception_handler(
    strings.BOT_INTERNAL_ERROR_TEXT
)

bot = Bot(
    collectors=...,
    bot_accounts=...,
    exception_handlers={Exception: smart_logger_exception_handler},
    middlewares=[BotXSmartLoggerMiddleware, debug_enabled_for_message=False]
)
```

3. [Опционально] Для фоновых задач создаём декоратор и запускаем фоновые задачи в при
   старте бота:

```python
import asyncio
from pybotx_smart_logger import make_smart_logger_decorator

smart_logger_decorator = make_smart_logger_decorator(lambda task_name: False)


@smart_logger_decorator
async def update_users_tasks() -> None:
    pass


async def update_background_task() -> None:
    while True:
        await update_users_tasks()
        await asyncio.sleep(60)

# Внутри функции бота `start_app`:
asyncio.create_task(update_background_task())
```

4. [Опционально] Возможность логирования из FastAPI хендлера:
В файле `app/main.py`
4.1 Подлключаем миддлварь:
``` python
from pybotx_smart_logger import FastApiSmartLoggerMiddleware
...
def get_application() -> FastAPI:
    ...
    application.middleware("http")(FastApiSmartLoggerMiddleware(debug_enabled=False))
```
4.2 Подключаем хендлер исключений:
``` python
from pybotx_smart_logger import FastApiSmartLoggerMiddleware, fastapi_exception_handler
...
def get_application() -> FastAPI:
    ...
    application.middleware("http")(FastApiSmartLoggerMiddleware(debug_enabled=False))
    application.add_exception_handler(Exception, fastapi_exception_handler)
```

## Пример команд для включения отладки

```python
@collector.command("/_debug:enable-for-huids", visible=False)
async def enable_debug_for_users(message: IncomingMessage, bot: Bot) -> None:
    try:
        huids = [UUID(huid) for huid in message.arguments]
    except ValueError:
        await bot.answer_message("Получен невалидный user_huid")
        return

    # TODO: Обновите список user_huid

    await bot.answer_message("Список user_huid для отладки обновлён")
```


```python
@collector.command("/_debug:enable-for-tasks", visible=False)
async def enable_debug_for_tasks(message: IncomingMessage, bot: Bot) -> None:
    # TODO: Обновите список имён задач

    await bot.answer_message("Список задач для отладки обновлён")
```


## Где применять

1. Проверка роли:

```python
from pybotx_smart_logger import smart_log

# TODO: Мидлварь для заполнения message.state.user

async def subscribed_users_only_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    if not message.state.user.is_subscribed:
        await bot.send(only_subscribed_users_allowed_message(message))

        return

    smart_log("This user is subscribed")

    await call_next(message, bot)
```

2. Обращение в API:

```python
from pybotx_smart_logger import smart_log

async def _perform_request(
    self,
    method: Literal["GET", "POST"],
    url: str,
    query_params: Optional[Dict[str, Any]] = None,
    body_dict: Optional[Dict[str, Any]] = None,
) -> ResponseSchema:
    smart_log("Performing request to YourAwesomeAPI")
    smart_log("Method:", method)
    smart_log("URL:", url)
    smart_log("Query parameters:", query_params)
    smart_log("Body dict:", body_dict)

    try:
        async with AsyncClient(base_url=self._base_url) as client:
            response = await client.request(
                method, url, params=query_params, json=body_dict
            )
    except HTTPError as exc:
        raise RequestToAwesomeAPIFailed from exc

    smart_log("Response text:", response.text)

    try:
        response.raise_for_status()
    except HTTPStatusError as exc:  # noqa: WPS440
        raise InvalidStatusCodeFromAwesomeAPI from exc

    return response.text
```

А также любые моменты, где что-то может пойти не так. Логируйте - не стестяйтесь.
