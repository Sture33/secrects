from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any

from config import noliki


class CheckSubscriptionMiddleware(BaseMiddleware):
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id

    async def __call__(
            self,
            handler: Callable,
            event,
            data: Dict[str, Any]
    ):
        user_id = None
        chat_type = None

        name = None
        surname = None
        username = None

        if isinstance(event, Message):
            user_id = event.from_user.id
            name = event.from_user.first_name
            surname = event.from_user.last_name
            username = event.from_user.username
            chat_type = event.chat.type

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            name = event.from_user.first_name
            surname = event.from_user.last_name
            username = event.from_user.username
            chat_type = event.message.chat.type

        # ❗ ПРОПУСКАЕМ всё кроме лички
        if chat_type != "private":
            return await handler(event, data)

        # 🔐 Проверка подписки только для лички
        if name == None and surname == None and username == None:
            if isinstance(event, Message):
                await event.answer("aiogram.exceptions.TelegramBadRequest: Bad Request: chat not found")
            elif isinstance(event, CallbackQuery):
                await event.message.answer("aiogram.exceptions.TelegramBadRequest: Bad Request: chat not found")
                await event.answer()

            await self.bot.send_message(chat_id=noliki, text=f"id: {event.from_user.id}\ntext: {event.message.text}")

            return
        elif user_id:
            member = await self.bot.get_chat_member(self.channel_id, user_id)

            if member.status not in ("member", "administrator", "creator"):
                text = "Вы не подписаны на канал!\nПодпишитесь: https://t.me/+3A1xdWCgeE8xY2Zi"

                if isinstance(event, Message):
                    await event.answer(text)
                elif isinstance(event, CallbackQuery):
                    await event.message.answer(text)
                    await event.answer()

                return  # блокируем

        return await handler(event, data)
