import logging
from asyncio import create_task, sleep
from typing import List

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, KeyboardButton
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from fluent.runtime import FluentLocalization

from bot.blocklists import banned, shadowbanned
from bot.config_reader import config
from bot.filters import SupportedMediaFilter

router = Router()


async def _reply(
        message: Message,
        l10n: FluentLocalization,
        l10n_token: str):
    logging.info(f"userside:reply {l10n_token=}")
    text = l10n.format_value(f"{l10n_token}-msg")
    if l10n_token in config.photo.keys():
        await message.answer_photo(config.photo[l10n_token], caption=text, parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")


async def _notify_admin(
        message: Message,
        bot: Bot,
        l10n,
        tags: str | List[str] = None, text: str = None):
    _id_tag = [f"id{message.from_user.id}"]
    if tags is not None:
        if isinstance(tags, list):
            tags = tags + _id_tag
        elif isinstance(tags, str):
            tags = [tags] + _id_tag
    else:
        tags = _id_tag
    _tags = " ".join([f"#{s}" for s in tags])
    if text is None:
        text = message.html_text
    await bot.send_message(
        config.admin_chat_id,
        f"{text}\n\n{_tags}", parse_mode="HTML")
    create_task(_send_expiring_notification(message, l10n))


async def _send_expiring_notification(message: Message, l10n: FluentLocalization):
    """
    Отправляет "самоуничтожающееся" через 5 секунд сообщение

    :param message: сообщение, на которое бот отвечает подтверждением отправки
    :param l10n: объект локализации
    """
    msg = await message.reply(l10n.format_value("sent-confirmation"))
    if config.remove_sent_confirmation:
        await sleep(5.0)
        await msg.delete()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, l10n: FluentLocalization):
    feed_done_btn = KeyboardButton(text=l10n.format_value("feedback-done-btn"))
    feed_rule_btn = KeyboardButton(text=l10n.format_value("feedback-rules-btn"))
    problem_btn = KeyboardButton(text=l10n.format_value("problem-btn"))
    builder = ReplyKeyboardBuilder()
    builder.row(feed_done_btn)
    builder.row(feed_rule_btn)
    builder.row(problem_btn)
    await message.answer(l10n.format_value("intro"), reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, l10n: FluentLocalization):
    await message.answer(l10n.format_value("help"))


@router.message(Command(commands=["info"]))
async def cmd_info(message: Message, l10n: FluentLocalization):
    await message.answer(l10n.format_value("info"))


@router.message(F.text)
async def text_message(message: Message, bot: Bot, l10n: FluentLocalization):
    """
    Хэндлер на текстовые сообщения от пользователя

    :param message: сообщение от пользователя для админа(-ов)
    :param l10n: объект локализации
    """

    if len(message.text) > 4000:
        return await message.reply(l10n.format_value("too-long-text-error"))

    if message.from_user.id in banned:
        await message.answer(l10n.format_value("you-were-banned-error"))
    elif message.from_user.id in shadowbanned:
        return
    else:
        if message.text == l10n.format_value("feedback-rules-btn"):
            await _reply(message, l10n, "feedback-rules")
        elif message.text == l10n.format_value("feedback-done-btn"):
            await _reply(message, l10n, "feedback-done")
            await _notify_admin(message, bot, l10n, "отзыв_оставлен", text="Пользователь оставил отзыв")
        elif message.text == l10n.format_value("problem-btn"):
            await message.answer(l10n.format_value("problem-msg"), parse_mode="Markdown")

        else:
            await _notify_admin(message, bot, l10n, "Сообщение")


@router.message(SupportedMediaFilter())
async def supported_media(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на медиафайлы от пользователя.
    Поддерживаются только типы, к которым можно добавить подпись (полный список см. в регистраторе внизу)

    :param message: медиафайл от пользователя
    :param l10n: объект локализации
    """
    logging.info(f"user: {message.from_user.id} send {message.content_type}")
    if message.caption and len(message.caption) > 1000:
        return await message.reply(l10n.format_value("too-long-caption-error"))
    if message.from_user.id in banned:
        await message.answer(l10n.format_value("you-were-banned-error"))
    elif message.from_user.id in shadowbanned:
        return
    else:
        await message.copy_to(
            config.admin_chat_id,
            caption=((message.caption or "") + f"\n\n#id{message.from_user.id}"),
            parse_mode="HTML"
        )
        create_task(_send_expiring_notification(message, l10n))
