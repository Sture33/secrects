import asyncio
import datetime

from aiogram import Router, Bot, F
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext

from app.functions import generate_full_name
from app.keyboard import chooses, to_main_menu
from app.states import AnonStates
from config import CEO, mainChannel, spyChannel
from aiogram.filters import CommandStart
from aiogram.types import Message, ChatMemberUpdated, ReplyKeyboardRemove, CallbackQuery, InputMediaPhoto, \
    InputMediaVideo, InputMediaDocument

from db.main import create_new_user, check_user, can_ask_question, update_question_time, get_question_time

router = Router()


async def show_main_menu(message: Message, state: FSMContext):
    await state.set_state(AnonStates.in_choose)

    if await check_user(message.from_user.id):
        await message.answer(
            "Рады видеть вас снова.\nВы можете выбрать что отправить.",
            reply_markup=chooses
        )
    else:
        await message.answer(
            "Выберите что отправить.",
            reply_markup=chooses
        )


@router.message(F.chat.type == "private", CommandStart())
async def start(message: Message, state: FSMContext):
    await show_main_menu(message, state)

@router.message(AnonStates.in_choose)
async def gone_menu(message: Message, state: FSMContext):
    await show_main_menu(message, state)

@router.callback_query(F.data == 'only_text')
async def only_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AnonStates.only_text)
    await callback.message.edit_text('Задавйте вопрос.', reply_markup=to_main_menu)


@router.callback_query(F.data == 'not_only_text')
async def with_media(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AnonStates.with_media)
    await state.update_data(media=[], caption="")
    await callback.message.edit_text(
        'Инструкция:\nСначала отправьте фото или видео (не более 10 файлов).\nПосле этого отправьте текст сообщения.\nВ тексте обязательно укажите тег "#end" — в начале или в конце сообщения.',
        reply_markup=to_main_menu)


@router.callback_query(F.data == 'to_menu')
async def send_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_main_menu(callback.message, state)

    text = "Сообщение удаляется..."

    for i in range(len(text), 0, -2):
        await callback.message.edit_text(text[:i])
        await asyncio.sleep(0.08)

    await callback.message.delete()


@router.message(AnonStates.only_text)
async def st_message(message: Message, bot: Bot, state: FSMContext):
    if await can_ask_question(message.from_user.id):
        random_name = await generate_full_name()
        await bot.send_message(chat_id=mainChannel,
                               text=f"<blockquote>Анонимный субъект - {random_name}</blockquote>\n\n<blockquote>{message.text}</blockquote>",
                               parse_mode="HTML")
        await bot.send_message(chat_id=spyChannel,
                               text=f"{message.from_user.full_name} @{message.from_user.username}\n<blockquote>{message.text}</blockquote>",
                               parse_mode="HTML")
        await update_question_time(message.from_user.id)
        await message.answer('Отправлено!', reply_markup=to_main_menu)
        await state.set_state(AnonStates.in_choose)

    else:
        time = await get_question_time(message.from_user.id)
        if time:
            dt = datetime.datetime.utcfromtimestamp(time + 18300, ).strftime('%H:%M:%S')
            await message.answer(
                f"Вы можете отправлять не более одного вопроса каждые 5 минут.\nСледующий вопрос будет доступен в {dt}.",
                reply_markup=to_main_menu)
        await state.set_state(AnonStates.in_choose)


@router.message(AnonStates.with_media)
async def collect_media(message: Message, state: FSMContext):
    if await can_ask_question(message.from_user.id):
        random_name = await generate_full_name()
        data = await state.get_data()
        media = data.get("media", [])
        if message.photo:
            media.append(("photo", message.photo[-1].file_id))
            await state.update_data(media=media)
            await message.answer("Фото добавлено")
            return
        if message.video:
            media.append(("video", message.video.file_id))
            await state.update_data(media=media)
            await message.answer("Видео добавлено")
            return
        if message.document:
            await message.answer('Пж не отправлять доки')
        if "#end" in message.text:
            mss = message.text
            if not media:
                await message.answer("Вы ничего не отправили")
                return

            media_group = []
            media_group2 = []

            for i, (type_, file_id) in enumerate(media):
                caption = f"<blockquote>Анонимный субъект - {random_name}</blockquote>\n\n<blockquote>{mss.replace('#end', '')}</blockquote>" if i == 0 else None
                if type_ == "photo":
                    media_group.append(InputMediaPhoto(media=file_id, caption=caption, parse_mode="HTML"))
                elif type_ == "video":
                    media_group.append(InputMediaVideo(media=file_id, caption=caption, parse_mode="HTML"))
            for j, (type_, file_id) in enumerate(media):
                caption = f"{message.from_user.full_name} @{message.from_user.username}\n<blockquote>{mss.replace('#end', '')}</blockquote>" if j == 0 else None
                if type_ == "photo":
                    media_group2.append(InputMediaPhoto(media=file_id, caption=caption, parse_mode="HTML"))
                elif type_ == "video":
                    media_group2.append(InputMediaVideo(media=file_id, caption=caption, parse_mode="HTML"))
            await message.bot.send_media_group(chat_id=mainChannel, media=media_group)
            await message.bot.send_media_group(chat_id=spyChannel, media=media_group2)
            await state.clear()
            await state.set_state(AnonStates.in_choose)
            await message.answer("Пост отправлен", reply_markup=to_main_menu)
    else:
        time = await get_question_time(message.from_user.id)
        if time:
            dt = datetime.datetime.utcfromtimestamp(time + 18300, ).strftime('%H:%M:%S')
            await message.answer(
                f"Вы можете отправлять не более одного вопроса каждые 5 минут.\nСледующий вопрос будет доступен в {dt}.",
                reply_markup=to_main_menu)
            await state.set_state(AnonStates.in_choose)
