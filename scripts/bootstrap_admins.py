import asyncio
import logging
import sys
import os

# Додаємо корінь проекту в sys.path, щоб скрипт бачив модулі database та config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from config import settings
from database.engine import async_session
from database.models import User, AdminPrivilege

# Налаштування логування для терміналу
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

async def bootstrap_admins():
    """
    Скрипт для автоматичного призначення прав SUPERADMIN 
    на основі номерів телефонів з .env файлу.
    """
    async with async_session() as session:
        # 1. Отримуємо список номерів з нашого Settings (вже очищений від пробілів та плюсиків)
        admin_phones = settings.superadmin_list
        
        if not admin_phones:
            logger.error("Список SUPERADMIN_NUMBERS порожній. Перевірте файл .env!")
            return

        logger.info(f"Починаємо ініціалізацію суперадмінів: {len(admin_phones)} номер(ів)")

        for phone in admin_phones:
            # 2. Шукаємо користувача. Використовуємо .contains(), щоб обійти 
            # можливу різницю між "380..." та "+380..." у базі.
            query = select(User).where(User.phone_number.contains(phone))
            result = await session.execute(query)
            user = result.scalar()

            if user:
                # 3. Надаємо права та рівень доступу
                user.is_admin = True
                user.admin_privilege = AdminPrivilege.SUPERADMIN
                
                logger.info(f"ПРАВА НАДАНО: {user.name} (ID: {user.telegram_id}) тепер Superadmin.")
            else:
                logger.warning(f"НЕ ЗНАЙДЕНО: Номер {phone} відсутній у базі. "
                               f"Користувач має зареєструватися в боті перед запуском скрипта.")

        # 4. Зберігаємо зміни
        try:
            await session.commit()
            logger.info("Всі зміни успішно збережені в базі даних.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Помилка при збереженні: {e}")

if __name__ == "__main__":
    # Перевірка для Windows (якщо ти раптом пересядеш з Mac)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(bootstrap_admins())
    except KeyboardInterrupt:
        logger.info("Скрипт зупинено вручну.")