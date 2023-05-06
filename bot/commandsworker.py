from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from fluent.runtime import FluentLocalization

from bot.config_reader import config


async def set_bot_commands(bot: Bot, l10n: FluentLocalization):
    usercommands = [
        # BotCommand(command="bonus", description=l10n.format_value("feedback-done-menu")),
        # BotCommand(command="rules", description=l10n.format_value("feedback-rules-menu")),
        # BotCommand(command="info", description="Небольшая информаци о нас"),
        # BotCommand(command="help", description="Справка по использованию бота"),

    ]
    await bot.set_my_commands(usercommands, scope=BotCommandScopeDefault())

    admin_commands = [
        BotCommand(command="who", description="Получение информации о пользователе"),
        BotCommand(command="ban", description="Заблокировать пользователя"),
        BotCommand(command="shadowban", description="Скрытно заблокировать пользователя"),
        BotCommand(command="unban", description="Разблокировать пользователя"),
        BotCommand(command="list_banned", description="Список заблокированных"),
    ]
    await bot.set_my_commands(
        admin_commands,
        scope=BotCommandScopeChat(chat_id=config.admin_chat_id)
    )
