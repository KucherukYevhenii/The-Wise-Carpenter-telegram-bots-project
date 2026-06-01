from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, delete, update
from database.models import User, WorkshopOpeningRequest, Status
from locales.texts import start_workshop_phrases as sw_p, status_phrases as st_p

from bots.user_bot.keyboards import get_q_main_kb, get_q_form_kb, get_q_archive_kb
from bots.user_bot.states import QuestionnaireStates

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

router = Router()

# --- Допоміжна функція: Отримання мови ---
async def get_lang(user_id: int, session: AsyncSession):
    res = await session.execute(select(User.language).where(User.telegram_id == user_id))
    return res.scalar() or "ua"

# --- Допоміжна функція: Головний екран анкети (Clean View) ---
async def show_q_form(event: Union[types.Message, types.CallbackQuery], state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    lang = await get_lang(event.from_user.id, session)
    p = sw_p[lang]

    text = (
        f"<b>{p['title']}</b>\n\n"
        f"{p['country_name']}: <code>{data.get('country') or '—'}</code>\n"
        f"{p['region_name']}: <code>{data.get('region') or '—'}</code>\n"
        f"{p['city_name']}: <code>{data.get('city') or '—'}</code>\n"
        f"{p['church_name']}: <code>{data.get('church_name') or '—'}</code>\n"
        f"{p['info']}: <code>{data.get('known_information') or '—'}</code>"
    )
    
    kb = get_q_form_kb(lang, data)

    # Якщо ми прийшли сюди з callback — редагуємо
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    # Якщо після введення тексту (Message) — шлемо нове, бо старе видалили
    else:
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    
    await state.set_state(QuestionnaireStates.filling_form)

# --- 1. ВХІД В МЕНЮ АНКЕТ ---
@router.message(Command("start_workshop"))
@router.callback_query(F.data == "questionnaire_menu")
async def q_menu(event: Union[types.Message, types.CallbackQuery], session: AsyncSession, state: FSMContext):
    await state.clear()
    lang = await get_lang(event.from_user.id, session)
    p = sw_p[lang]

    user_res = await session.execute(
        select(User).where(User.telegram_id == event.from_user.id)
    )
    db_user = user_res.scalar()
    
    # Шукаємо чернетку в БД
    res = await session.execute(select(WorkshopOpeningRequest).where(
        WorkshopOpeningRequest.user_id == db_user.user_id,
        WorkshopOpeningRequest.status == Status.DRAFT
    ))
    draft = res.scalar()
    
    text = f"<b>{p['title']}</b>\n\n{p['desc']}"
    kb = get_q_main_kb(lang, bool(draft))

    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# --- 2. СТВОРЕННЯ / ПРОДОВЖЕННЯ ---
@router.callback_query(F.data.in_(["q_new", "q_continue"]))
async def q_init(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):

    user_res = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    db_user = user_res.scalar()

    res = await session.execute(select(WorkshopOpeningRequest).where(
        WorkshopOpeningRequest.user_id == db_user.user_id,
        WorkshopOpeningRequest.status == Status.DRAFT
    ))
    draft = res.scalar()

    if callback.data == "q_new":
        if draft:
            await session.delete(draft)
            await session.commit()
        draft = WorkshopOpeningRequest(
            user_id=db_user.user_id,
            status=Status.DRAFT
        )
        session.add(draft)
        await session.commit()
        await session.refresh(draft)

    # Завантажуємо все в FSM
    await state.update_data(
        request_id=draft.request_id,
        country=draft.country, 
        region=draft.region, 
        city=draft.city,
        church_name=draft.church_name, 
        known_information=draft.known_information
    )
    await show_q_form(callback, state, session)

# --- 3. РЕДАГУВАННЯ ПОЛЯ (Запуск вводу) ---
@router.callback_query(F.data.startswith("q_edit_"))
async def q_edit_start(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    lang = await get_lang(callback.from_user.id, session)
    field = callback.data.replace("q_edit_", "")
    p = sw_p[lang]
    
    config = {
        "country": (QuestionnaireStates.input_country, "set_country"),
        "region": (QuestionnaireStates.input_region, "set_region"),
        "city": (QuestionnaireStates.input_city, "set_city"),
        "church": (QuestionnaireStates.input_church, "set_church"),
        "info": (QuestionnaireStates.input_info, "set_info")
    }
    
    state_to_set, phrase_key = config[field]

    builder = InlineKeyboardBuilder()
    builder.button(text=f"{p['back_to_form']}", callback_data="q_continue")

    await callback.message.delete()
    
    prompt_text = f"<b>{p[phrase_key]}:</b>"
    
    prompt = await callback.message.answer(
        prompt_text, 
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    
    await state.update_data(msg_to_delete=prompt.message_id)
    await state.set_state(state_to_set)

# --- 4. ЗБЕРЕЖЕННЯ ДАНИХ ---
@router.message(F.text, StateFilter(
        QuestionnaireStates.input_country, 
        QuestionnaireStates.input_region, 
        QuestionnaireStates.input_city, 
        QuestionnaireStates.input_church, 
        QuestionnaireStates.input_info
    ))
async def q_save_input(message: types.Message, state: FSMContext, session: AsyncSession):
    current_state = await state.get_state()
    data = await state.get_data()
    
    field_map = {
        QuestionnaireStates.input_country.state: "country",
        QuestionnaireStates.input_region.state: "region",
        QuestionnaireStates.input_city.state: "city",
        QuestionnaireStates.input_church.state: "church_name",
        QuestionnaireStates.input_info.state: "known_information"
    }
    column = field_map[current_state]

    if data.get("msg_to_delete"):
        try: await message.bot.delete_message(message.chat.id, data["msg_to_delete"])
        except: pass
    await message.delete()

    await session.execute(update(WorkshopOpeningRequest).where(
        WorkshopOpeningRequest.request_id == data['request_id']
    ).values({column: message.text}))
    await session.commit()
    
    await state.update_data({column: message.text})
    
    await show_q_form(message, state, session)

# --- 5. ВІДПРАВКА ---
@router.callback_query(F.data == "q_send")
async def q_send(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    lang = await get_lang(callback.from_user.id, session)

    await session.execute(update(WorkshopOpeningRequest).where(
        WorkshopOpeningRequest.request_id == data['request_id']
    ).values(status=Status.NEW))
    await session.commit()
    
    await state.clear()
    await callback.answer(sw_p[lang]['form_sent'], show_alert=True)
    await q_menu(callback, session, state)

# --- 6. ВИДАЛЕННЯ ---
@router.callback_query(F.data == "q_cancel")
async def q_confirm_del(callback: types.CallbackQuery, session: AsyncSession):
    lang = await get_lang(callback.from_user.id, session)
    p = sw_p[lang]
    
    builder = InlineKeyboardBuilder()
    builder.button(text=p['confirm_canceling'], callback_data="q_del_confirm")
    builder.button(text=p['back_to_form'], callback_data="q_continue")
    
    builder.adjust(1)
    
    await callback.message.edit_text(f"<b>{p['confirm_canceling_desc']}</b>", 
                                     reply_markup=builder.as_markup(), parse_mode="HTML")

@router.callback_query(F.data == "q_del_confirm")
async def q_delete(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    await session.execute(delete(WorkshopOpeningRequest).where(WorkshopOpeningRequest.request_id == data['request_id']))
    await session.commit()
    await state.clear()
    await callback.answer(".")
    await q_menu(callback, session, state)

# --- 7. СПИСОК АРХІВНИХ АНКЕТ ---
@router.callback_query(F.data == "q_archive")
async def q_archive_list(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    lang = await get_lang(callback.from_user.id, session)
    p = sw_p[lang]

    user_res = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
    db_user = user_res.scalar()

    res = await session.execute(
        select(WorkshopOpeningRequest)
        .where(
            WorkshopOpeningRequest.user_id == db_user.user_id,
            WorkshopOpeningRequest.status != Status.DRAFT
        )
        .order_by(WorkshopOpeningRequest.created_at.desc())
    )
    requests = res.scalars().all()

    if not requests:
        return await callback.answer(p.get("no_archived"), show_alert=True)

    # Виправлено внутрішні лапки на одинарні 'archive_desc'
    await callback.message.edit_text(
        f"<b>{p['form_archive']}</b>\n\n{p.get('archive_desc')}",
        reply_markup=get_q_archive_kb(lang, requests),
        parse_mode="HTML"
    )

# --- 8. ДЕТАЛЬНИЙ ПЕРЕГЛЯД АНКЕТИ З АРХІВУ ---
@router.callback_query(F.data.startswith("q_arch_view:"))
async def q_archive_view_detail(callback: types.CallbackQuery, session: AsyncSession):
    lang = await get_lang(callback.from_user.id, session)
    p = sw_p[lang]
    req_id = int(callback.data.split(":")[1])

    res = await session.execute(
        select(WorkshopOpeningRequest).where(WorkshopOpeningRequest.request_id == req_id)
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

    # Виправлено всі внутрішні лапки на одинарні 'title', 'status', 'date'
    text = (
        f"<b>{p.get('title')}</b>\n"
        f"--------------------------\n"
        f"<b>{p.get('status')}:</b> {status_map.get(req.status)}\n"
        f"<b>{p.get('date')}:</b> {req.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"{p['country_name']}: {req.country}\n"
        f"{p['region_name']}: {req.region}\n"
        f"{p['city_name']}: {req.city}\n"
        f"{p['church_name']}: {req.church_name}\n"
        f"{p['info']}:\n{req.known_information}"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text=f"{p.get('back_to_archive')}", callback_data="q_archive")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")