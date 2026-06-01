from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, delete, update
from database.models import User, MobileWorkshopRequest, Status
from locales.texts import mobile_workshop_phrases as mq_p, status_phrases as st_p

from bots.user_bot.keyboards import get_mq_main_kb, get_mq_form_kb, get_mq_archive_kb
from bots.user_bot.states import MobileQuestionnaireStates

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

router = Router()

# --- Допоміжна функція: Отримання мови ---
async def get_lang(user_id: int, session: AsyncSession):
    res = await session.execute(select(User.language).where(User.telegram_id == user_id))
    return res.scalar() or "ua"

# Допоміжна функція відображення форми
async def show_mq_form(event: Union[types.Message, types.CallbackQuery], state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    lang = await get_lang(event.from_user.id, session)
    p = mq_p[lang]

    text = (
        f"<b>{p['title']}</b>\n\n"
        f"{p['country_name']}: <code>{data.get('country') or '—'}</code>\n"
        f"{p['region_name']}: <code>{data.get('region') or '—'}</code>\n"
        f"{p['city_name']}: <code>{data.get('city') or '—'}</code>\n"
        f"{p['organization_name']}: <code>{data.get('organization') or '—'}</code>\n"
        f"{p['purpose_name']}: <code>{data.get('purpose') or '—'}</code>"
    )
    
    kb = get_mq_form_kb(lang, data)
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    await state.set_state(MobileQuestionnaireStates.filling_form)

# --- 1. ВХІД В МЕНЮ АНКЕТ ---
@router.message(Command("call_mobile_workshop"))
@router.callback_query(F.data == "mobile_menu")
async def mq_menu(event: Union[types.Message, types.CallbackQuery], session: AsyncSession, state: FSMContext):
    await state.clear()
    lang = await get_lang(event.from_user.id, session)
    p = mq_p[lang]
    
    user_res = await session.execute(select(User).where(User.telegram_id == event.from_user.id))
    db_user = user_res.scalar()

    res = await session.execute(select(MobileWorkshopRequest).where(
        MobileWorkshopRequest.user_id == db_user.user_id,
        MobileWorkshopRequest.status == Status.DRAFT
    ))
    draft = res.scalars().first()
    text = f"<b>{p['title']}</b>\n\n{p['desc']}"
    kb = get_mq_main_kb(lang, bool(draft))

    # ВИПРАВЛЕННЯ ТУТ:
    if isinstance(event, types.Message):
        # Якщо це повідомлення (команда) — шлемо нове
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        # Якщо це кнопка — редагуємо існуюче
        await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# --- 2. ІНІЦІАЛІЗАЦІЯ (Нова/Продовжити) ---
@router.callback_query(F.data.in_(["mq_new", "mq_continue"]))
async def mq_init(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    user_res = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
    db_user = user_res.scalar()

    res = await session.execute(select(MobileWorkshopRequest).where(
        MobileWorkshopRequest.user_id == db_user.user_id,
        MobileWorkshopRequest.status == Status.DRAFT
    ))
    draft = res.scalars().first()

    if callback.data == "mq_new":
        if draft:
            await session.delete(draft)
            await session.commit()
        draft = MobileWorkshopRequest(user_id=db_user.user_id, status=Status.DRAFT)
        session.add(draft)
        await session.commit()
        await session.refresh(draft)

    await state.update_data(
        req_id=draft.request_id,
        country=draft.country, 
        region=draft.region, 
        city=draft.city,
        organization=draft.organization, 
        purpose=draft.purpose
    )
    await show_mq_form(callback, state, session)

# --- 3. РЕДАГУВАННЯ ПОЛЯ ---
@router.callback_query(F.data.startswith("mq_edit:"))
async def mq_edit_start(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    lang = await get_lang(callback.from_user.id, session)
    field = callback.data.split(":")[1]
    p = mq_p[lang]
    
    config = {
        "country": (MobileQuestionnaireStates.input_country, "set_country"),
        "region": (MobileQuestionnaireStates.input_region, "set_region"),
        "city": (MobileQuestionnaireStates.input_city, "set_city"),
        "organization": (MobileQuestionnaireStates.input_organization, "set_organization"),
        "purpose": (MobileQuestionnaireStates.input_purpose, "set_purpose")
    }
    
    state_to_set, phrase_key = config[field]
    await callback.message.delete()
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{p['back_to_form']}", callback_data="mq_continue")
    
    prompt_text = f"<b>{p[phrase_key]}:</b>"

    prompt = await callback.message.answer(
        prompt_text, 
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    await state.update_data(
        msg_to_delete=prompt.message_id, 
        editing_field=field
        )
    await state.set_state(state_to_set)

# --- 4. ЗБЕРЕЖЕННЯ ТЕКСТУ ---
@router.message(F.text, StateFilter(MobileQuestionnaireStates))
async def mq_save_input(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    field = data['editing_field']
    
    # Чистимо чат
    if data.get("msg_to_delete"):
        try: await message.bot.delete_message(message.chat.id, data['msg_to_delete'])
        except: pass
    await message.delete()

    # Оновлюємо БД
    await session.execute(update(MobileWorkshopRequest).where(
        MobileWorkshopRequest.request_id == data['req_id']
    ).values({field: message.text}))
    await session.commit()
    
    await state.update_data({field: message.text})

    await show_mq_form(message, state, session)

# --- 5. ВІДПРАВКА ---
@router.callback_query(F.data == "mq_send")
async def mq_final_send(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    lang = await get_lang(callback.from_user.id, session)
    
    await session.execute(update(MobileWorkshopRequest).where(
        MobileWorkshopRequest.request_id == data['req_id']
    ).values(status=Status.NEW))
    await session.commit()
    
    await state.clear()
    await callback.answer(mq_p[lang]['form_sent'], show_alert=True)
    await mq_menu(callback, session, state)

# --- 6. ВИДАЛЕННЯ (Чернетки мобільної майстерні) ---
@router.callback_query(F.data == "mq_cancel")
async def mq_confirm_del(callback: types.CallbackQuery, session: AsyncSession):
    lang = await get_lang(callback.from_user.id, session)
    p = mq_p[lang] # mobile_workshop_phrases
    
    builder = InlineKeyboardBuilder()
    # Використовуємо фрази з sw_p, якщо в mq_p немає дублікатів (або додай в mq_p)
    builder.button(text=p.get('confirm_canceling'), callback_data="mq_del_confirm")
    builder.button(text=p.get('back_to_form'), callback_data="mq_continue")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"<b>{p.get('confirm_canceling_desc')}</b>", 
        reply_markup=builder.as_markup(), 
        parse_mode="HTML"
    )

@router.callback_query(F.data == "mq_del_confirm")
async def mq_delete(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    # Видаляємо саме з мобільної таблиці
    await session.execute(delete(MobileWorkshopRequest).where(MobileWorkshopRequest.request_id == data['req_id']))
    await session.commit()
    await state.clear()
    await callback.answer(".")
    await mq_menu(callback, session, state)

# --- 7. СПИСОК АРХІВНИХ АНКЕТ (Мобільні) ---
@router.callback_query(F.data == "mq_archive")
async def mq_archive_list(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    lang = await get_lang(callback.from_user.id, session)
    p = mq_p[lang]

    user_res = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
    db_user = user_res.scalar()

    # Шукаємо всі надіслані мобільні анкети
    res = await session.execute(
        select(MobileWorkshopRequest)
        .where(
            MobileWorkshopRequest.user_id == db_user.user_id,
            MobileWorkshopRequest.status != Status.DRAFT
        )
        .order_by(MobileWorkshopRequest.created_at.desc())
    )
    requests = res.scalars().all()

    if not requests:
        return await callback.answer(p.get("no_archived"), show_alert=True)

    await callback.message.edit_text(
        f"<b>{p.get('form_archive')}</b>\n\n{p.get('archive_desc')}",
        reply_markup=get_mq_archive_kb(lang, requests), # Спеціальна клавіатура для мобільних
        parse_mode="HTML"
    )

# --- 8. ДЕТАЛЬНИЙ ПЕРЕГЛЯД ---
@router.callback_query(F.data.startswith("mq_arch_view:"))
async def mq_archive_view_detail(callback: types.CallbackQuery, session: AsyncSession):
    lang = await get_lang(callback.from_user.id, session)
    p = mq_p[lang]
    req_id = int(callback.data.split(":")[1])

    res = await session.execute(
        select(MobileWorkshopRequest).where(MobileWorkshopRequest.request_id == req_id)
    )
    req = res.scalar()

    if not req:
        return await callback.answer("Анкету не знайдено", show_alert=True)
    
    S = st_p[lang]
    status_map = {
        Status.NEW: S["status_new"],
        Status.IN_PROGRESS: S["status_in_progress"],
        Status.COMPLETED: S["status_completed"],
        Status.REJECTED: S["status_rejected"],
        Status.CLOSED: S["status_closed"]
    }

    # Тут додаємо наше нове поле Organization та Purpose
    text = (
        f"<b>{p.get('title')}</b>\n"
        f"--------------------------\n"
        f"<b>{p.get('status')}:</b> {status_map.get(req.status)}\n"
        f"<b>{p.get('date')}:</b> {req.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"{p.get('country_name')}: {req.country}\n"
        f"{p.get('region_name')}: {req.region}\n"
        f"{p.get('city_name')}: {req.city}\n"
        f"{p.get('organization_name')}: {req.organization}\n"
        f"{p.get('purpose_name')}:\n{req.purpose}"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text=f"{p.get('back_to_archive')}", callback_data="mq_archive")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")