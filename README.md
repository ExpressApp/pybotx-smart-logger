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

Используя функцию `smart_log(log_message: str, *args: Any, **kwargs: Any)` логируете всю
информацию, которая поможет в диагностике ошибки. Если во время обработки сообщения
будет выброшено исключение, в логи попадёт:

1. Текущее сообщение от пользователя,
2. Вся залогированная с помощью `smart_log` информация,
3. Выброшенное исключение.

Если обработка сообщения завершится успешно, накопленные логи будут "выброшены".

## Настройка

1. Устанавливаем библиотеку:  
```bash
poetry add pybotx-smart-logger
```

2. Подключим мидлварь для логирования входящих сообщений:

**middlewares/smart_logger.py**
```python #logger_init_middleware
async def smart_logger_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    async with wrap_smart_logger(
        log_source="Incoming message",
        context_func=lambda: format_raw_command(message.raw_command),
        debug=True,
    ):
        await call_next(message, bot)
```

**bot.py**
```python #logger_init_bot
Bot(
    collectors=[collector],
    bot_accounts=[BOT_CREDENTIALS],
    middlewares=[
        smart_logger_middleware,
    ],
)
```
3. Для того чтобы логировать какие-то другие части приложения, необходимо обернуть в контекстный менджер:
```python #logger_common_use
async def handler() -> None:
    async with wrap_smart_logger(
        log_source="Request to Server",
        context_func=lambda: str(kwargs),
        debug=False,
    ):
        await make_request(**kwargs)
```

4.  Также можно использовать smart_logger для логирования запросов к FastAPI приложению:
```python #logger_fastapi_use
app = FastAPI()


@app.middleware("http")
async def smart_logger_middleware(request: Request, call_next: Callable) -> None:
    async with wrap_smart_logger(
        log_source="Incoming request",
        context_func=lambda: pformat_str_request(request),
        debug=DEBUG,
    ):
        return await call_next(request)
```
`log_source` определяет источник логов. `context_func` - пользовательская функция для форматирования логов.

## Пример команд для включения отладки

```python #logger_debug_enable
@collector.command("/_debug:enable-for-huids", visible=False)
async def enable_debug_for_users(message: IncomingMessage, bot: Bot) -> None:
    try:
        huids = [UUID(huid) for huid in message.arguments]
    except ValueError:
        await bot.answer_message("Получен невалидный user_huid")
        return

    # TODO: Обновите список user_huid

    await bot.answer_message(f"Список user_huid для отладки обновлён {huids}")
```


```python #logger_debug_enable_command
@collector.command("/_debug:enable-for-tasks", visible=False)
async def enable_debug_for_tasks(message: IncomingMessage, bot: Bot) -> None:
    # TODO: Обновите список имён задач

    await bot.answer_message("Список задач для отладки обновлён")
```


## Где применять

1. Проверка роли:

```python #logger_check_role
# TODO: Мидлварь для заполнения message.state.user


async def subscribed_users_only_middleware(
    message: IncomingMessage,
    bot: Bot,
    call_next: IncomingMessageHandlerFunc,
) -> None:
    if not message.state.user.is_subscribed:
        await bot.send(message=only_subscribed_users_allowed_message(message))

        return

    smart_log("This user is subscribed")

    await call_next(message, bot)
```

2. Обращение в API:

```python #logger_api_call
async def _perform_request(
    method: Literal["GET", "POST"],
    url: str,
    query_params: Optional[Dict[str, Any]] = None,
    body_dict: Optional[Dict[str, Any]] = None,
) -> str:
    smart_log("Performing request to YourAwesomeAPI")
    smart_log("Method:", method)
    smart_log("URL:", url)
    smart_log("Query parameters:", query_params)
    smart_log("Body dict:", body_dict)

    try:
        async with AsyncClient(base_url=base_url) as client:
            response = await client.request(
                method,
                url,
                params=query_params,
                json=body_dict,
            )
    except HTTPError as exc:
        raise RequestToAwesomeAPIError from exc

    smart_log("Response text:", response.text)

    try:
        response.raise_for_status()
    except HTTPStatusError as exc:  # noqa: WPS440
        raise InvalidStatusCodeFromAwesomeAPIError from exc

    return response.text
```

А также любые моменты, где что-то может пойти не так. Логируйте - не стестяйтесь.
