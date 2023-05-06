from aiogram import Router, F, Bot
from aiogram.types import ContentType, CallbackQuery
from aiogram.types import Message
from fluent.runtime import FluentLocalization
from bot.config_reader import config

router = Router()


@router.message(F.reply_to_message, F.chat.id == config.admin_chat_id, F.poll)
async def unsupported_admin_reply_types(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на неподдерживаемые типы сообщений, т.е. те, которые не имеют смысла
    для копирования. Например, опросы (админ не увидит результат)

    :param message: сообщение от администратора
    :param l10n: объект локализации
    """
    await message.reply(l10n.format_value("cannot-reply-with-this-type-error"))


@router.message()
async def unsupported_types(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на неподдерживаемые типы сообщений, т.е. те, к которым нельзя добавить подпись

    :param message: сообщение от пользователя
    :param l10n: объект локализации
    """
    # Игнорируем служебные сообщения
    if message.content_type not in (
            ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER, ContentType.VIDEO_CHAT_STARTED,
            ContentType.VIDEO_CHAT_ENDED, ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
            ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED, ContentType.NEW_CHAT_PHOTO, ContentType.DELETE_CHAT_PHOTO,
            ContentType.SUCCESSFUL_PAYMENT, "proximity_alert_triggered",  # в 3.0.0b3 нет поддержка этого контент-тайпа
            ContentType.NEW_CHAT_TITLE, ContentType.PINNED_MESSAGE):
        await message.reply(l10n.format_value("unsupported-message-type-error"))
