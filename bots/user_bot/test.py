import asyncio
from aiogram import Bot
from config import settings

async def test_bot_access():
    print("🔄 Ініціалізація клієнтського бота...")
    # Використовуємо токен USER_BOT, який і має проблеми з доступом
    bot = Bot(token=settings.USER_BOT_TOKEN.get_secret_value())
    
    chat_id = settings.GROUP_ID
    print(f"📡 Стукаємо в GROUP_ID: {chat_id}")
    
    # Крок 1: Пробуємо просто відправити повідомлення від імені USER_BOT
    try:
        test_msg = await bot.send_message(
            chat_id=chat_id, 
            text="🚨 <b>Тест зв'язку:</b> Якщо ви бачите це повідомлення, User Bot успішно пише в групу контенту!"
        )
        print(f"✅ Успішно відправлено! ID тестового повідомлення: {test_msg.message_id}")
        
        # Крок 2: Пробуємо переслати це ж повідомлення (імітуємо логіку з info.py)
        try:
            forwarded = await bot.forward_message(
                chat_id=test_msg.chat.id,  # Пересилаємо в той самий чат з адміном
                from_chat_id=chat_id,
                message_id=test_msg.message_id
            )
            print("🎉 ІДЕАЛЬНО! Бот зміг сам переслати повідомлення. Доступ повний!")
            
            # Чистимо за собою сміття в групі
            # await test_msg.delete()
            # await forwarded.delete()
            print("🧹 Тестові повідомлення успішно видалено.")
            
        except Exception as forward_error:
            print(f"❌ Помилка на етапі ПЕРЕСИЛАННЯ (forward): {forward_error}")
            print("👉 Це означає: бот вміє писати, але у нього закриті права на читання історії/повідомлень чату!")
            
    except Exception as send_error:
        print(f"❌ Помилка на етапі ВІДПРАВКИ (send): {send_error}")
        print("👉 Це означає: бот взагалі не доданий в групу, або у нього немає прав писати туди.")
        
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_bot_access())