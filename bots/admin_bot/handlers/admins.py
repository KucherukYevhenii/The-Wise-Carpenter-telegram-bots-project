import asyncio
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from database.models import User, AdminPrivilege
from bots.admin_bot.states import AddAdmin
from bots.admin_bot.keyboards import admins_menu_kb, admins_list_kb, admin_detail_kb, back_kb, users_list_kb
from locales.admin_texts import admins as adm, access as acc

router = Router()
PAGE_SIZE = 8

async def _show_admins_list(callback: CallbackQuery, session: AsyncSession, page: int):
    # Отримуємо свіжого юзера для мови
    current_admin = (await session.execute(select(User).where(User.telegram_id == callback.from_user.id))).scalar_one()
    lang = current_admin.language

    total = (await session.execute(select(func.count(User.user_id)).where(User.is_admin == True))).scalar() or 0
    total_pages = max(1, -(-total // PAGE_SIZE))
    
    # Коригуємо page, якщо воно виходить за межі (наприклад, після видалення останнього адміна на сторінці)
    if page >= total_pages:
        page = total_pages - 1

    stmt = select(User).where(User.is_admin == True).order_by(User.name).offset(page * PAGE_SIZE).limit(PAGE_SIZE)
    items = (await session.execute(stmt)).scalars().all()

    text = adm[lang].get("list_title").format(count=total)
    
    # Використовуємо callback.message для редагування
    await callback.message.edit_text(
        text, 
        reply_markup=admins_list_kb(lang, items, page, total_pages), 
        parse_mode="HTML"
    )


@router.message(Command("admins"))
@router.callback_query(F.data == "menu:admins")
async def cb_admins_main_menu(event: Union[Message, CallbackQuery], user: User, state: FSMContext):
    # 🎯 ВИПРАВЛЕНО: Завжди скидаємо стан при вході в меню, щоб уникнути "застрягання" FSM
    await state.clear() 
    
    lang = user.language
    
    if user.admin_privilege != AdminPrivilege.SUPERADMIN:
        text_denied = acc[lang].get("superadmin_only")
        if isinstance(event, CallbackQuery):
            await event.answer(text_denied, show_alert=True)
        else:
            await event.answer(text_denied)
        return

    text = f"<b>{adm[lang].get('title')}</b>"
    
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=admins_menu_kb(lang), parse_mode="HTML")
    else:
        await event.answer(text, reply_markup=admins_menu_kb(lang), parse_mode="HTML")


@router.callback_query(F.data.startswith("adm:list:"))
async def cb_admins_list(callback: CallbackQuery, session: AsyncSession):
    page = int(callback.data.split(":")[-1])
    await _show_admins_list(callback, session, page)


@router.callback_query(F.data.startswith("adm_page:"))
async def cb_admins_pagination(callback: CallbackQuery, session: AsyncSession):
    page = int(callback.data.split(":")[-1])
    await _show_admins_list(callback, session, page)


@router.callback_query(F.data.startswith("adm_detail:"))
async def cb_admin_detail_card(callback: CallbackQuery, user: User, session: AsyncSession):
    target_tg_id = int(callback.data.split(":")[1])
    lang = user.language

    target_user = (await session.execute(select(User).where(User.telegram_id == target_tg_id))).scalar_one_or_none()
    if not target_user:
        await callback.answer(adm[lang].get("user_not_found"), show_alert=True)
        return

    is_super = target_user.admin_privilege == AdminPrivilege.SUPERADMIN
    priv_label = adm[lang].get("privilege_superadmin") if is_super else adm[lang].get("privilege_admin")

    text = adm[lang].get("detail").format(
        name=target_user.name,
        telegram_id=target_user.telegram_id,
        phone_number=target_user.phone_number or "—",
        privilege=priv_label,
        language = target_user.language
    )
    await callback.message.edit_text(text, reply_markup=admin_detail_kb(lang, target_tg_id, is_superadmin_target=is_super), parse_mode="HTML")


@router.callback_query(F.data == "adm:add")
async def cb_add_admin_start(callback: CallbackQuery, user: User, session: AsyncSession):
    lang = user.language
    # Вибираємо користувачів, які не є адмінами, і сортуємо за ім'ям
    stmt = select(User).where(User.is_admin == False).order_by(User.name).limit(PAGE_SIZE)
    items = (await session.execute(stmt)).scalars().all()
    
    # Текст для вибору (можна додати в admin_texts)
    text = "Оберіть користувача зі списку:" if lang == "ua" else "Select a user from the list:"
    
    await callback.message.edit_text(
        text, 
        reply_markup=users_list_kb(lang, items, 0, 1), 
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_select_page:"))
async def cb_users_pagination(callback: CallbackQuery, user: User, session: AsyncSession):
    page = int(callback.data.split(":")[-1])
    lang = user.language
    
    stmt = select(User).where(User.is_admin == False).order_by(User.name).offset(page * PAGE_SIZE).limit(PAGE_SIZE)
    items = (await session.execute(stmt)).scalars().all()
    
    # Тут треба порахувати total_pages для пагінації
    total = (await session.execute(select(func.count(User.user_id)).where(User.is_admin == False))).scalar() or 0
    total_pages = max(1, -(-total // PAGE_SIZE))

    await callback.message.edit_text(
        "Оберіть користувача:", 
        reply_markup=users_list_kb(lang, items, page, total_pages), 
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("adm_select:"))
async def cb_select_user_for_admin(callback: CallbackQuery, user: User, session: AsyncSession):
    target_id = int(callback.data.split(":")[1])
    
    target_user = (await session.execute(select(User).where(User.telegram_id == target_id))).scalar_one_or_none()
    
    if target_user:
        target_user.is_admin = True
        target_user.admin_privilege = AdminPrivilege.ADMIN
        await session.commit()
        
        lang = user.language
        msg = f"Користувача {target_user.name} призначено адміном." if lang == "ua" else f"User {target_user.name} assigned as admin."
        await callback.answer(msg, show_alert=True)
    
    # 🎯 ВИПРАВЛЕНО: Замість виклику іншої функції, просто редагуємо повідомлення на меню списку адмінів
    # Це змусить бота оновити список і показати актуальний склад
    page = 0
    total = (await session.execute(select(func.count(User.user_id)).where(User.is_admin == True))).scalar() or 0
    total_pages = max(1, -(-total // PAGE_SIZE))

    stmt = select(User).where(User.is_admin == True).order_by(User.name).offset(page * PAGE_SIZE).limit(PAGE_SIZE)
    items = (await session.execute(stmt)).scalars().all()

    text = adm[lang].get("list_title").format(count=total)
    await callback.message.edit_text(text, reply_markup=admins_list_kb(lang, items, page, total_pages), parse_mode="HTML")


@router.message(AddAdmin.enter_telegram_id, F.text)
async def process_add_admin_id(message: Message, state: FSMContext, user: User, session: AsyncSession):
    input_text = message.text.strip()
    lang = user.language
    fsm_data = await state.get_data()
    bot_msg_id = fsm_data.get("bot_msg_id")
    
    # 🛡️ ВИПРАВЛЕНО: Захист видалення повідомлення
    try:
        await message.delete()
    except Exception:
        pass

    # Створюємо помічну функцію для виведення помилок, щоб не дублювати код
    async def show_error(error_key: str):
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id, message_id=bot_msg_id,
                text=adm[lang].get(error_key), reply_markup=back_kb(lang, "menu:admins")
            )
        except Exception:
            pass

    if not input_text.isdigit():
        await show_error("invalid_id")
        return

    target_id = int(input_text)
    target_user = (await session.execute(select(User).where(User.telegram_id == target_id))).scalar_one_or_none()

    if not target_user:
        await show_error("user_not_found")
        return

    if target_user.is_admin:
        await show_error("already_admin")
        return

    # Якщо всі перевірки пройдено — даємо права
    target_user.is_admin = True
    target_user.admin_privilege = AdminPrivilege.ADMIN
    await session.commit()
    await state.clear()

    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id, message_id=bot_msg_id,
            text=adm[lang].get("granted").format(name=target_user.name),
            reply_markup=back_kb(lang, "menu:admins"), parse_mode="HTML"
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("adm_remove:"))
async def cb_remove_admin_rights(callback: CallbackQuery, session: AsyncSession):
    # Отримуємо свіжу інформацію про поточного адміна
    current_admin = (await session.execute(select(User).where(User.telegram_id == callback.from_user.id))).scalar_one()
    lang = current_admin.language
    
    target_tg_id = int(callback.data.split(":")[1]) 

    if target_tg_id == callback.from_user.id:
        await callback.answer(adm[lang].get("cannot_remove_self"), show_alert=True)
        return

    target_user = (await session.execute(select(User).where(User.telegram_id == target_tg_id))).scalar_one_or_none()
    if target_user:
        user_name = target_user.name
        target_user.is_admin = False
        target_user.admin_privilege = None
        
        await session.commit()
        session.expire_all()
        
        await callback.answer(adm[lang].get("revoked").format(name=user_name), show_alert=True)
        
    # Викликаємо оновлення списку
    await _show_admins_list(callback, session, 0)
# ===========================================================================
# 🛡️ UX ФОЛБЕК — ПЕРЕХОПЛЕННЯ НЕКОРЕКТНОГО КОНТЕНТУ
# ===========================================================================
@router.message(StateFilter(AddAdmin), ~F.text)
async def cb_wrong_admin_input(message: Message, user: User):
    """Спрацює, якщо замість Telegram ID адмін надішле стікер або фотографію."""
    try: 
        await message.delete()
    except Exception: 
        pass
    
    lang = user.language
    error_msg = (
        "❌ Будь ласка, надішліть числовий ID текстом." 
        if lang == "ua" 
        else "❌ Please send the numeric ID as text."
    )
    
    alert = await message.answer(error_msg)
    await asyncio.sleep(4)
    try:
        await alert.delete()
    except Exception:
        pass