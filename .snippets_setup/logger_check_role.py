from pybotx import Bot, IncomingMessage, IncomingMessageHandlerFunc, OutgoingMessage

from pybotx_smart_logger import smart_log


def only_subscribed_users_allowed_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=message.body,
    )


