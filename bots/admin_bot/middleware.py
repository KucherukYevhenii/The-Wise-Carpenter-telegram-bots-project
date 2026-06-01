from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from sqlalchemy import select
from database.models import User

from locales.admin_texts import access as acc

class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # 1. Отримуємо сесію БД з попереднього мідлваря
        session = data.get("session")
        if not session:
            return

        # Надійніший спосіб отримати юзера в aiogram 3 — через event.event
        # (це автоматично підтягне або message.from_user, або callback_query.from_user)
        from_user = getattr(event.event, "from_user", None)
        if not from_user:
            # Якщо це службовий апдейт (наприклад, my_chat_member) — пропускаємо далі
            return await handler(event, data)

        user_id = from_user.id

        # 2. Перевіряємо статус адміна в базі за telegram_id
        res = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = res.scalar()

        # 3. Логіка допуску
        if user and user.is_admin:
            # Прокидаємо об'єкт користувача далі в хендлери як параметр `user: User`
            data["user"] = user
            return await handler(event, data)
        
        # 4. Якщо не адмін — відхиляємо запит
        if event.callback_query:
            lang = user.language if user else "ua"
            # Показуємо спливаюче вікно, щоб зняти анімацію завантаження з кнопки

            text_dict = acc.get(lang, acc.get("ua"))
            alert_text = text_dict.get('denied', "Доступ заборонено")

            await event.callback_query.answer(alert_text, show_alert=True)
                    
        return # Зупиняємо виконання, хендлер не викликається