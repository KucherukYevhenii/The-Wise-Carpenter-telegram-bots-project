from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from database.models import User, GeneralInformation
from bots.user_bot.keyboards import get_info_categories_kb, get_back_kb
from config import settings
from locales.texts import general_info as gen

router = Router()

async def get_user_context(user_id: int, session: AsyncSession):
    """Отримує мову та категорії одним запитом до БД"""
    user_stmt = select(User.language).where(User.telegram_id == user_id)
    user_lang = (await session.execute(user_stmt)).scalar() or "ua"

    cat_stmt = (
        select(GeneralInformation)
        .where(GeneralInformation.language == user_lang)
        .order_by(GeneralInformation.category.asc())
    )
    categories = (await session.execute(cat_stmt)).scalars().all()
    return categories, user_lang

@router.message(Command("general_info"))
@router.callback_query(F.data == "info_back_to_list")
async def cmd_general_info(event: Union[types.Message, types.CallbackQuery], session: AsyncSession):
    """Обробка головного меню інформації (команда або кнопка Назад)"""
    user_id = event.from_user.id
    categories, lang = await get_user_context(user_id, session)

    if not categories:
        text = gen[lang].get('no_info')
        if isinstance(event, types.Message):
            await event.answer(text)
        else:
            await event.message.edit_text(text)
        return

    # Виправлено подвійні лапки на одинарні 'general_info_label', 'choose_category', 'page'
    text = (
        f"<b>{gen[lang].get('general_info_label')}</b>\n"
        f"{gen[lang].get('choose_category')} ({gen[lang].get('page')} 1):"
    )
    
    kb = get_info_categories_kb(categories, user_lang=lang, page=0)

    # Захист: якщо це CallbackQuery, пробуємо редагувати. 
    # Якщо старе повідомлення було видалено — безпечно відправляємо нове через try-except, щоб уникнути крашу.
    if isinstance(event, types.CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("info_page:"))
async def process_info_pagination(callback: types.CallbackQuery, session: AsyncSession):
    page = int(callback.data.split(":")[1])
    categories, lang = await get_user_context(callback.from_user.id, session)

    # Виправлено внутрішні лапки
    text = (
        f"<b>{gen[lang].get('general_info_label')}</b>\n"
        f"{gen[lang].get('choose_category')} ({gen[lang].get('page')} {page + 1}):"
    )
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_info_categories_kb(categories, user_lang=lang, page=page), 
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("info_id:"))
async def show_info_detail(callback: types.CallbackQuery, session: AsyncSession):
    info_id = int(callback.data.split(":")[1])
    
    stmt = select(GeneralInformation).where(GeneralInformation.information_id == info_id)
    info_item = (await session.execute(stmt)).scalar_one_or_none()
    
    user_stmt = select(User.language).where(User.telegram_id == callback.from_user.id)
    lang = (await session.execute(user_stmt)).scalar() or "ua"

    if not info_item:
        await callback.answer(gen[lang].get('no_info'), show_alert=True)
        return
    
    text = (
        f"<b>{gen[lang].get('general_info_label')}</b>\n"
        f"<b><i>{info_item.category}</i></b>\n\n"
        f"{info_item.information}"
    )

    # Видаляємо старе інлайн-меню (Clean Chat концепція)
    try:
        await callback.message.delete()
    except Exception:
        pass

    back_keyboard = get_back_kb(lang, "info_back_to_list")
    
    # ---------------------------------------------------------------------------
    # 📸 ЛОГІКА З ФОТОГРАФІЯМИ ЗАКОМЕНТОВАНА (ТИМЧАСОВО ВИМКНЕНО)
    # ---------------------------------------------------------------------------
    # if info_item.media_message_id:
    #     try:
    #         # Тимчасово пересилаємо повідомлення боту, щоб дізнатися file_id
    #         tmp_forward = await callback.bot.forward_message(
    #             chat_id=callback.message.chat.id,
    #             from_chat_id=settings.GROUP_ID,
    #             message_id=info_item.media_message_id
    #         )
    #         
    #         if tmp_forward.photo:
    #             photo_file_id = tmp_forward.photo[-1].file_id
    #             
    #             try: await tmp_forward.delete()
    #             except: pass
    #             
    #             if len(text) > 1024:
    #                 await callback.bot.send_photo(chat_id=callback.message.chat.id, photo=photo_file_id)
    #                 await callback.bot.send_message(chat_id=callback.message.chat.id, text=text, reply_markup=back_keyboard, parse_mode="HTML")
    #             else:
    #                 await callback.bot.send_photo(
    #                     chat_id=callback.message.chat.id,
    #                     photo=photo_file_id,
    #                     caption=text,
    #                     reply_markup=back_keyboard,
    #                     parse_mode="HTML"
    #                 )
    #         else:
    #             try: await tmp_forward.delete()
    #             except: pass
    #             await callback.bot.send_message(chat_id=callback.message.chat.id, text=text, reply_markup=back_keyboard, parse_mode="HTML")
    #             
    #     except Exception as e:
    #         print(f"🚨 Помилка обробки медіа: {e}")
    #         await callback.bot.send_message(chat_id=callback.message.chat.id, text=text, reply_markup=back_keyboard, parse_mode="HTML")
    # else:
    #     await callback.bot.send_message(chat_id=callback.message.chat.id, text=text, reply_markup=back_keyboard, parse_mode="HTML")
    # ---------------------------------------------------------------------------

    # Залізобетонна пряма відправка текстового контенту
    await callback.bot.send_message(
        chat_id=callback.message.chat.id, 
        text=text, 
        reply_markup=back_keyboard, 
        parse_mode="HTML"
    )
    
    await callback.answer()