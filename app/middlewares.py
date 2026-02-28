from datetime import datetime
from aiogram import BaseMiddleware, Bot
from aiogram.types import Update, Message
from typing import Callable, Awaitable, Dict, Any

LOG_CHANNEL_ID = -1003746027572
MESSAGE_STORE = {}  # хранение логов в памяти для редактирования

class FullAuditMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:

        bot: Bot = data["bot"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Новое или отредактированное сообщение
        message: Message | None = event.message or event.edited_message
        if message:
            if message.chat.type == "channel":
                return await handler(event, data)

            chat_id = message.chat.id
            msg_id = message.message_id
            user = message.from_user

            text = message.text or message.caption or "[не текстовое сообщение]"
            status = "Отправлено" if event.message else "Изменено"

            log_text = (
                f"📩 Сообщение\n"
                f"⏱ Время: {now}\n\n"
                f"👤 {user.full_name if user else 'Unknown'} | {user.id if user else '—'}\n"
                f"💬 Chat: {message.chat.title or 'Private'}\n"
                f"🆔 Chat ID: {chat_id}\n"
                f"📨 Message ID: {msg_id}\n\n"
                f"{text}\n\n"
                f"Статус — {status}"
            )

            if event.message:
                log_msg = await bot.send_message(LOG_CHANNEL_ID, log_text)
                MESSAGE_STORE[(chat_id, msg_id)] = {
                    "log_message_id": log_msg.message_id,
                    "text": text
                }
            else:
                key = (chat_id, msg_id)
                if key in MESSAGE_STORE:
                    log_message_id = MESSAGE_STORE[key]["log_message_id"]
                    MESSAGE_STORE[key]["text"] = text
                    await bot.edit_message_text(
                        chat_id=LOG_CHANNEL_ID,
                        message_id=log_message_id,
                        text=log_text
                    )

        return await handler(event, data)