import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message


async def delete_messages(bot: Bot, messages: Message | list[Message], delay: float = 2):
    """Удаляет пачку сообщений"""
    async def _del():
        await asyncio.sleep(delay)
        if not isinstance(messages, list):
            message_ids = [messages.message_id]
            chat = messages.chat.id
        else:
            message_ids = [x.message_id for x in messages]
            chat = messages[0].chat.id
        try:
            await bot.delete_messages(chat, message_ids)
        except TelegramBadRequest:
            pass

    asyncio.create_task(_del())


async def temporary_message(*, message: Message, text: str, kb=None, delay: float = 1.5):
    """Отправляет текст и удаляет его через delay"""
    async def _del():
        mess = await message.answer(text, reply_markup=kb)
        await asyncio.sleep(delay)
        try:
            await mess.delete()
        except TelegramBadRequest:
            pass

    asyncio.create_task(_del())