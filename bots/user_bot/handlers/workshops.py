from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, distinct, asc
from database.models import User, Workshop, Status
from bots.user_bot.states import WorkshopStates
from bots.user_bot.keyboards import get_workshop_nav_kb
from locales.texts import workshop_phrases as ws_p, general_info as gen

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from config import settings

router = Router()

async def get_lang(user_id: int, session: AsyncSession):
    res = await session.execute(select(User.language).where(User.telegram_id == user_id))
    return res.scalar() or "ua"

# --- РІВЕНЬ 1: Країни ---
@router.message(Command("workshops"))
@router.callback_query(F.data.startswith("ws_countries"))
async def ws_countries(event: Union[types.Message, types.CallbackQuery], session: AsyncSession, state: FSMContext):
    await state.clear() # Скидаємо все зайве (включаючи списки видалення фото)
    lang = await get_lang(event.from_user.id, session)

    page = 0
    if isinstance(event, types.CallbackQuery):
        parts = event.data.split(":")
        if len(parts) > 1 and parts[-1].isdigit():
            page = int(parts[-1])
        try:
            await event.answer()
        except Exception:
            pass

    # ВИПРАВЛЕНО: Прибрали distinct() з asc() для сумісності з PostgreSQL
    stmt = select(distinct(Workshop.country)).where(
        Workshop.status == Status.ACTIVE,
        Workshop.language == lang
    ).order_by(asc(Workshop.country))
    
    res = await session.execute(stmt)
    items = res.scalars().all()
    
    if not items:
        text = f"<b>{ws_p[lang].get('title')}</b>\n\n" + gen[lang].get('no_info')
        if isinstance(event, types.Message):
            await event.answer(text, parse_mode="HTML")
        else:
            await event.message.edit_text(text, parse_mode="HTML")
        return

    text = f"<b>{ws_p[lang].get('title')}</b>\n\n{ws_p[lang].get('choose_country')}"
    kb = get_workshop_nav_kb(lang, items, "ws_countries", "ws_reg", [], page)

    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")

# --- РІВЕНЬ 2: Регіони ---
@router.callback_query(F.data.startswith("ws_reg"))
async def ws_regions(callback: types.CallbackQuery, session: AsyncSession):
    parts = callback.data.split(":")
    country = parts[1]
    page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0

    lang = await get_lang(callback.from_user.id, session)
    
    # ВИПРАВЛЕНО: Прибрали distinct() з asc()
    stmt = select(distinct(Workshop.region)).where(
        Workshop.country == country,
        Workshop.status == Status.ACTIVE,
        Workshop.language == lang
    ).order_by(asc(Workshop.region))
    
    res = await session.execute(stmt)
    items = res.scalars().all()
    
    back = [(f"{ws_p[lang].get('back_to')} {ws_p[lang].get('country_lvl')}", "ws_countries:0")]
    
    await callback.message.edit_text(
        f"<b>{ws_p[lang].get('title')}</b>\n\n {ws_p[lang].get('choose_region')}",
        reply_markup=get_workshop_nav_kb(lang, items, f"ws_reg:{country}", f"ws_city:{country}", back, page),
        parse_mode="HTML"
    )
    try:
        await callback.answer()
    except Exception:
        pass

# --- РІВЕНЬ 3: Міста ---
@router.callback_query(F.data.startswith("ws_city"))
async def ws_cities(callback: types.CallbackQuery, session: AsyncSession):
    parts = callback.data.split(":")
    country = parts[1]
    region = parts[2]
    page = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0

    lang = await get_lang(callback.from_user.id, session)

    # ВИПРАВЛЕНО: Прибрали distinct() з asc()
    stmt = select(distinct(Workshop.city)).where(
        Workshop.country == country,
        Workshop.region == region,
        Workshop.status == Status.ACTIVE,
        Workshop.language == lang
    ).order_by(asc(Workshop.city))
    
    res = await session.execute(stmt)
    items = res.scalars().all()

    back = [
        (f"{ws_p[lang].get('back_to')} {ws_p[lang].get('region_lvl')}", f"ws_reg:{country}:0"),
        (f"{ws_p[lang].get('back_to')} {ws_p[lang].get('country_lvl')}", "ws_countries:0")
    ]
    
    await callback.message.edit_text(
        f"<b>{ws_p[lang].get('title')}</b>\n\n {ws_p[lang].get('choose_city')}",
        reply_markup=get_workshop_nav_kb(lang, items, f"ws_city:{country}:{region}", f"ws_list:{country}:{region}", back, page),
        parse_mode="HTML"
    )
    try:
        await callback.answer()
    except Exception:
        pass

# --- РІВЕНЬ 4: Майстерні (Логіка чищення фото) ---
@router.callback_query(F.data.startswith("ws_list"))
async def ws_list(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    for m_id in data.get("to_del", []):
        try: 
            await callback.bot.delete_message(callback.message.chat.id, m_id)
        except Exception: 
            pass
    await state.clear()

    parts = callback.data.split(":")
    if len(parts) < 4:
        return await ws_countries(callback, session, state)
        
    country = parts[1]
    region = parts[2]
    city = parts[3]
    page = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0

    lang = await get_lang(callback.from_user.id, session)

    stmt = select(Workshop).where(
        Workshop.country == country,
        Workshop.region == region,
        Workshop.city == city,
        Workshop.status == Status.ACTIVE,
        Workshop.language == lang
    ).order_by(Workshop.church_name.asc())
    
    res = await session.execute(stmt)
    items = res.scalars().all()

    back = [
        (f"{ws_p[lang].get('back_to')} {ws_p[lang].get('city_lvl')}", f"ws_city:{country}:{region}:0"),
        (f"{ws_p[lang].get('back_to')} {ws_p[lang].get('region_lvl')}", f"ws_reg:{country}:0"),
        (f"{ws_p[lang].get('back_to')} {ws_p[lang].get('country_lvl')}", "ws_countries:0")
    ]
    
    text = f"<b>{ws_p[lang].get('title')}</b>\n\n {ws_p[lang].get('choose_workshop')}"
    kb = get_workshop_nav_kb(lang, items, f"ws_list:{country}:{region}:{city}", f"ws_view:{country}:{region}:{city}", back, page)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    try:
        await callback.answer()
    except Exception:
        pass

# --- РІВЕНЬ 5: Картка майстерні ---
@router.callback_query(F.data.startswith("ws_view"))
async def ws_view(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    ws_id = int(callback.data.split(":")[-1])
    res = await session.execute(select(Workshop).where(Workshop.workshop_id == ws_id))
    ws_item = res.scalar()

    lang = await get_lang(callback.from_user.id, session)
    
    try:
        await callback.message.delete()
    except Exception:
        pass

    text = (
        f"<b>{ws_p[lang].get('title')}</b>\n\n"
        f"<b>{ws_item.church_name}</b>\n\n"
        f"{ws_p[lang].get('address')} {ws_item.address}\n"
        f"{ws_p[lang].get('leader')} {ws_item.workshop_leader}\n"
        f"{ws_p[lang].get('phone')}: {ws_item.phone_number}"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text=f"{ws_p[lang].get('back_to')} {ws_p[lang].get('list_lvl')}", 
                   callback_data=f"ws_list:{ws_item.country}:{ws_item.region}:{ws_item.city}:0")

    if ws_item.media_message_id:
        try:
            msg = await callback.bot.copy_message(
                chat_id=callback.message.chat.id,
                from_chat_id=settings.GROUP_ID,
                message_id=ws_item.media_message_id,
                caption=text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
        except Exception:
            msg = await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        msg = await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    
    await state.update_data(to_del=[msg.message_id])
    try:
        await callback.answer()
    except Exception:
        pass