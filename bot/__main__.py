import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from bot.handlers import setup_routers
from fluent.runtime import FluentLocalization, FluentResourceLoader
from bot.commandsworker import set_bot_commands
from bot.middlewares import L10nMiddleware
from pathlib import Path

from bot.config_reader import config


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Получение пути до каталога locales относительно текущего файла
    locales_dir = Path(__file__).parent.joinpath("locales")
    # Создание объектов Fluent
    # FluentResourceLoader использует фигурные скобки, поэтому f-strings здесь нельзя
    l10n_loader = FluentResourceLoader(str(locales_dir) + "/{locale}")
    l10n = FluentLocalization(["ru"], [
        "strings.ftl",
        "errors.ftl",
        "feedback.ftl",
    ], l10n_loader)

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    router = setup_routers()
    dp.include_router(router)

    if config.custom_bot_api:
        bot.session.api = TelegramAPIServer.from_base(config.custom_bot_api, is_local=True)

    # Регистрация мидлварей
    dp.update.middleware(L10nMiddleware(l10n))

    # Регистрация /-команд в интерфейсе
    await set_bot_commands(bot, l10n)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


asyncio.run(main())
