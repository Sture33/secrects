import datetime

from aiogram import Router, Bot, F
from aiogram.enums import ChatMemberStatus

from app.functions import generate_full_name
from config import CEO, mainChannel, spyChannel
from aiogram.filters import CommandStart
from aiogram.types import Message, ChatMemberUpdated

from db.main import create_new_user, check_user, can_ask_question, update_question_time, get_question_time

router = Router()

async def is_subscribed(bot: Bot, user_id):
    member = await bot.get_chat_member(mainChannel, user_id)
    return member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)

@router.message(F.chat.type == "private", CommandStart())
async def start(message: Message, bot: Bot):
    if await is_subscribed(bot, message.from_user.id):
        if await check_user(message.from_user.id):
            await message.answer("Рады видеть вас снова.\nВы можете задать свой вопрос.")
        else:
            await message.answer("Вы можете задать свой вопрос.")
            await create_new_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                                  message.from_user.username)
    else:
        await message.answer('Вы не подписаны на наш канал\nПожалуйста сначало подпишитесь\nhttps://t.me/+3A1xdWCgeE8xY2Zi')

@router.message(F.chat.type == 'private')
async def st_message(message: Message, bot: Bot):
    if await is_subscribed(bot, message.from_user.id):
        if await can_ask_question(message.from_user.id):
            random_name = await generate_full_name()
            await bot.send_message(chat_id=mainChannel,
                                    text=f"<blockquote>Анонимный субъект - {random_name}</blockquote>\n\n<blockquote>{message.text}</blockquote>",
                                    parse_mode="HTML")
            await update_question_time(message.from_user.id)
            await bot.send_message(chat_id=spyChannel, text=f"{message.from_user.full_name} @{message.from_user.username}\n<blockquote>{message.text}</blockquote>", parse_mode="HTML")
            await message.answer('Отправлено!')
        else:
            time = await get_question_time(message.from_user.id)
            if time:
                dt = datetime.datetime.utcfromtimestamp(time + 18300, ).strftime('%H:%M:%S')
                await message.answer(f"Вы можете отправлять не более одного вопроса каждые 5 минут.\nСледующий вопрос будет доступен в {dt}.")
    else:
        await message.answer('Вы не подписаны на наш канал\nПожалуйста сначало подпишитесь\nhttps://t.me/+3A1xdWCgeE8xY2Zi')