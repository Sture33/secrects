from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any

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

        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            member = await self.bot.get_chat_member(self.channel_id, user_id)

            if member.status not in ("member", "administrator", "creator"):
                text = "Вы не подписаны на канал!\nПодпишитесь: https://t.me/+3A1xdWCgeE8xY2Zi"

                if isinstance(event, Message):
                    await event.answer(text)
                elif isinstance(event, CallbackQuery):
                    await event.message.answer(text)
                    await event.answer()

                return  # ❌ блокируем дальнейшую обработку

        return await handler(event, data)