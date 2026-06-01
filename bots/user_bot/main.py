import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import settings
from database.engine import async_session  

from aiogram.fsm.storage.redis import RedisStorage
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ErrorEvent
from redis.asyncio import Redis

from bots.user_bot.middleware import DbSessionMiddleware
from bots.user_bot.handlers import registration, info,faq_info, settings as sett, questions, workshops, questionnaire, mobile_questionnaire

async def main():
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Ініціалізація бота через SecretStr
    bot = Bot(token=settings.USER_BOT_TOKEN.get_secret_value())


    # Підключення до Redis
    redis_client = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis_client)

    dp = Dispatcher(storage=storage)

    
    # підключення middleware
    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))

    # підключення Функцій
    dp.include_router(registration.router)
    dp.include_router(info.router)
    dp.include_router(faq_info.router)
    dp.include_router(sett.router)
    dp.include_router(questions.router)
    dp.include_router(workshops.router)
    dp.include_router(questionnaire.router)
    dp.include_router(mobile_questionnaire.router)


    # підключення обробника помилок
    @dp.errors()
    async def global_error_handler(event: ErrorEvent):
        # 1. Обробка застарілих Callback-запитів (після перебоїв з інтернетом)
        if isinstance(event.exception, TelegramBadRequest):
            if "query is too old" in event.exception.message:
                logging.warning(f"Query is canceled: {event.exception.message}. The user has been waiting for request for too long.")
                return True # Повідомляємо aiogram, що помилка оброблена

        # 2. Обробка спроби видалити вже видалене повідомлення
        if isinstance(event.exception, TelegramBadRequest):
            if "message to delete not found" in event.exception.message:
                logging.info("The trying to delete the deleted message. Ignoting")
                return True

        # 3. Логування всіх інших непередбачуваних помилок
        logging.error(f"Unnexpected error: {event.exception}", exc_info=True)

    print("Користувацький бот стартував...\nUser bot started...")
    await dp.start_polling(bot, handle_signals=False)

if __name__ == "__main__":
    asyncio.run(main())