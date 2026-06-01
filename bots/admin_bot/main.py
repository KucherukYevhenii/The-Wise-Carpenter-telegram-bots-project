import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import ErrorEvent
from redis.asyncio import Redis

from config import settings
from database.engine import async_session

from bots.admin_bot.middleware import AdminCheckMiddleware
from bots.user_bot.middleware import DbSessionMiddleware

from bots.admin_bot.handlers import (
    start,
    requests,
    workshops,
    support,
    content,
    admins,
    stats,
    settings as sett
)


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.ADMIN_BOT_TOKEN.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    redis_client = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis_client)

    dp = Dispatcher(storage=storage)

    # Порядок важливий:
    # 1. DbSessionMiddleware — відкриває сесію БД і кладе її в data["session"]
    # 2. AdminCheckMiddleware — використовує data["session"] для перевірки is_admin
    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))
    dp.update.middleware(AdminCheckMiddleware())

    # Роутери — порядок від конкретного до загального
    dp.include_router(start.router)
    dp.include_router(requests.router)
    dp.include_router(workshops.router)
    dp.include_router(support.router)
    dp.include_router(content.router)
    dp.include_router(admins.router)
    dp.include_router(stats.router)
    dp.include_router(sett.router)

    # Обробник помилок — той самий підхід що і в user_bot
    @dp.errors()
    async def global_error_handler(event: ErrorEvent):
        if isinstance(event.exception, TelegramBadRequest):
            err_msg = str(event.exception).lower()
            
            if "query is too old" in err_msg:
                logging.warning(f"Query is too old: {event.exception}")
                return True
                
            if "message to delete not found" in err_msg:
                logging.info("Trying to delete already deleted message. Ignoring.")
                return True
                
            if "message is not modified" in err_msg:
                logging.info("Message content not changed. Ignoring.")
                return True

        # Всі інші (неочікувані) помилки логуємо повністю
        logging.error(f"Unexpected error: {event.exception}", exc_info=True)

    print("Адмін-бот стартував...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, handle_signals=False)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот зупинено.")