import asyncio
from typing import Union
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.models import User, Workshop, Status
from locales.admin_texts import workshops as ws, general as gen, content as cnt, requests as req
from bots.admin_bot.states import EditWorkshop
from bots.admin_bot.keyboards import (
    workshops_menu_kb, workshops_list_kb, workshop_detail_kb,
    workshop_edit_fields_kb, back_kb
)

router = Router()
PAGE_SIZE = 8

# ---------------------------------------------------------------------------
# Допоміжні функції
# ---------------------------------------------------------------------------
def _format_detail(lang: str, item: Workshop) -> str:
    status_str = item.status.value.lower()
    status_key = f"status_{status_str}" 
    status_label = ws[lang].get(status_key, item.status.value)

    return ws[lang].get("detail").format(
        workshop_id    = item.workshop_id,
        country        = item.country or "—",
        region         = item.region or "—",
        city           = item.city or "—",
        church_name    = item.church_name or "—",
        address        = item.address or "—",
        workshop_leader= item.workshop_leader or "—",
        phone_number   = item.phone_number or "—",
        status         = status_label,
    )

async def _get_workshop(session: AsyncSession, workshop_id: int) -> Workshop | None:
    return (await session.execute(
        select(Workshop).where(Workshop.workshop_id == workshop_id)
    )).scalar()

async def _show_workshop_form_builder(event: Union[Message, CallbackQuery], workshop_id: int, lang_filter: str, lang: str, session: AsyncSession):
    item = await _get_workshop(session, workshop_id)
    
    text = (
        f"<b>{ws[lang].get('builder_title')}</b>\n"
        f"<i>{ws[lang].get('builder_desc')}</i>\n\n"
        f"<b>{ws[lang].get('card_language')}</b> <code>{item.language.upper()}</code>\n"
        f"----------------------------------------\n"
        f"{_format_detail(lang, item)}"
    )
    kb = workshop_edit_fields_kb(lang, workshop_id, lang_filter)

    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            # 🛡️ ВИПРАВЛЕНО: Видаляємо старе повідомлення, щоб уникнути дублікатів
            try: await event.message.delete()
            except Exception: pass
            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        await event.answer(text, reply_markup=kb, parse_mode="HTML")

# ---------------------------------------------------------------------------
# Навігація та Мовний Фільтр списків
# ---------------------------------------------------------------------------
@router.message(Command("workshops"))
@router.callback_query(F.data == "menu:workshops")
async def cmd_workshops_main(event: Union[Message, CallbackQuery], user: User):
    lang = user.language
    text = ws[lang].get("title")
    kb = workshops_menu_kb(lang)

    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=kb)
        except Exception:
            pass
    else:
        await event.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("ws:filter:"))
async def cb_ws_filter_select(callback: CallbackQuery, user: User, session: AsyncSession):
    lang_filter = callback.data.split(":")[2]
    lang = user.language
    await _show_filtered_list(callback, session, lang, lang_filter, page=0)


@router.callback_query(F.data.startswith("ws_page:"))
async def cb_ws_pagination(callback: CallbackQuery, user: User, session: AsyncSession):
    _, lang_filter, page = callback.data.split(":")
    lang = user.language
    await _show_filtered_list(callback, session, lang, lang_filter, int(page))


async def _show_filtered_list(callback: CallbackQuery, session: AsyncSession, lang: str, lang_filter: str, page: int):
    base_query = select(Workshop).where(Workshop.status != Status.DRAFT)
    
    if lang_filter != "all":
        base_query = base_query.where(Workshop.language == lang_filter)

    total_query = select(func.count()).select_from(base_query.subquery())
    total = (await session.execute(total_query)).scalar()
    total_pages = max(1, -(-total // PAGE_SIZE))

    items_query = base_query.order_by(Workshop.country, Workshop.city).offset(page * PAGE_SIZE).limit(PAGE_SIZE)
    items = (await session.execute(items_query)).scalars().all()

    text_title = ws[lang].get("list_title").format(count=total) + f" [{lang_filter.upper()}]"
    keyboard = workshops_list_kb(lang, items, lang_filter, page, total_pages)

    if not items:
        try:
            await callback.message.edit_text(text=ws[lang].get("list_empty"), reply_markup=workshops_menu_kb(lang))
        except Exception:
            try: await callback.message.delete()
            except Exception: pass
            await callback.message.answer(text=ws[lang].get("list_empty"), reply_markup=workshops_menu_kb(lang))
        return

    try:
        await callback.message.edit_text(text=text_title, reply_markup=keyboard)
    except Exception:
        try: await callback.message.delete()
        except Exception: pass
        await callback.message.answer(text=text_title, reply_markup=keyboard)

# ---------------------------------------------------------------------------
# Детальний перегляд картки майстерні
# ---------------------------------------------------------------------------
@router.callback_query(F.data.startswith("ws_detail:"))
async def cb_ws_card_detail(callback: CallbackQuery, user: User, session: AsyncSession):
    parts = callback.data.split(":")
    workshop_id = int(parts[1])
    lang_filter = parts[2]
    lang = user.language

    item = await _get_workshop(session, workshop_id)
    if not item:
        await callback.answer(gen[lang].get("not_found"), show_alert=True)
        return

    keyboard = workshop_detail_kb(lang, item.workshop_id, item.status.value, lang_filter)
    detail_text = _format_detail(lang, item)

    try:
        await callback.message.edit_text(text=detail_text, reply_markup=keyboard)
    except Exception:
        try: await callback.message.delete()
        except Exception: pass
        await callback.message.answer(text=detail_text, reply_markup=keyboard)

# ---------------------------------------------------------------------------
# Показ списку
# ---------------------------------------------------------------------------
@router.callback_query(F.data.startswith("ws:list:"))
async def cb_ws_back_to_list(callback: CallbackQuery, user: User, session: AsyncSession):
    _, _, lang_filter, page = callback.data.split(":")
    lang = user.language
    await _show_filtered_list(callback, session, lang, lang_filter, int(page))

# ---------------------------------------------------------------------------
# Зміна статусів та Видалення
# ---------------------------------------------------------------------------
@router.callback_query(F.data.startswith("ws_status:"))
async def cb_ws_status_toggle(callback: CallbackQuery, user: User, session: AsyncSession):
    _, workshop_id, target_status, lang_filter = callback.data.split(":")
    lang = user.language

    item = await _get_workshop(session, int(workshop_id))
    if item:
        item.status = Status(target_status)
        await session.commit()
        
        alert_msg = ws[lang].get("updated") if target_status == "ACTIVE" else ws[lang].get("deactivated")
        await callback.answer(alert_msg)
    
    await cb_ws_card_detail(callback, user, session)


@router.callback_query(F.data.startswith("ws_delete_item:"))
async def cb_ws_delete(callback: CallbackQuery, user: User, session: AsyncSession):
    _, workshop_id, lang_filter = callback.data.split(":")
    lang = user.language

    item = await _get_workshop(session, int(workshop_id))
    if item:
        await session.delete(item)
        await session.commit()
        await callback.answer(gen[lang].get("deleted"))
    
    await _show_filtered_list(callback, session, lang, lang_filter, page=0)

# ---------------------------------------------------------------------------
# КЛОНУВАННЯ
# ---------------------------------------------------------------------------
@router.callback_query(F.data.startswith("ws_clone:"))
async def cb_ws_clone_card(callback: CallbackQuery, user: User, session: AsyncSession):
    _, workshop_id, lang_filter = callback.data.split(":")
    lang = user.language

    source = await _get_workshop(session, int(workshop_id))
    if not source:
        await callback.answer(gen[lang].get("not_found"), show_alert=True)
        return

    target_lang = "en" if source.language == "ua" else "ua"

    clone = Workshop(
        language         = target_lang,
        country          = source.country,
        region           = source.region,
        city             = source.city,
        church_name      = source.church_name,
        address          = source.address,
        workshop_leader  = source.workshop_leader,
        phone_number     = source.phone_number,
        media_message_id = None, 
        status           = source.status
    )
    session.add(clone)
    await session.commit()
    await session.refresh(clone)

    msg = f"Клоновано на [{target_lang.upper()}]. Перекладіть назву та адресу!" if lang == "ua" else f"Cloned to [{target_lang.upper()}]. Translate title and address!"
    await callback.answer(msg, show_alert=True)
    
    await _show_workshop_form_builder(callback, clone.workshop_id, lang_filter, lang, session)

# ---------------------------------------------------------------------------
# АНКЕТУВАННЯ / КОНСТРУКТОР КАРТКИ
# ---------------------------------------------------------------------------
@router.callback_query(F.data == "ws:add")
async def cb_ws_add_start_form(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession):
    await state.clear() # Про всяк випадок чистимо старі стани
    lang = user.language
    
    draft = Workshop(
        language=lang, status=Status.DRAFT, 
        country="", region="", city="", church_name="", address="", workshop_leader="", phone_number=""
    )
    session.add(draft)
    await session.commit()
    await session.refresh(draft)

    await _show_workshop_form_builder(callback, draft.workshop_id, "all", lang, session)


@router.callback_query(F.data.startswith("ws_edit_card:"))
async def cb_ws_edit_existing_card(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession):
    await state.clear()
    _, workshop_id, lang_filter = callback.data.split(":")
    lang = user.language
    await _show_workshop_form_builder(callback, int(workshop_id), lang_filter, lang, session)


@router.callback_query(F.data.startswith("ws_field:"))
async def cb_ws_field_input_trigger(callback: CallbackQuery, state: FSMContext, user: User):
    _, workshop_id, field, lang_filter = callback.data.split(":")
    lang = user.language

    if field == "photo":
        await callback.answer("📸 Фотографії тимчасово вимкнено!", show_alert=True)
        return

    await state.set_state(EditWorkshop.enter_value)
    await state.update_data(
        workshop_id=int(workshop_id),
        field=field,
        lang_filter=lang_filter,
        msg_to_delete=callback.message.message_id
    )

    field_prompts = {
        "country":         ws[lang].get("ask_country"),
        "region":          ws[lang].get("ask_region"),
        "city":            ws[lang].get("ask_city"),
        "church_name":     ws[lang].get("ask_church"),
        "address":         ws[lang].get("ask_address"),
        "workshop_leader": ws[lang].get("ask_leader"),
        "phone_number":    ws[lang].get("ask_phone"),
    }

    builder = InlineKeyboardBuilder()
    builder.button(text=gen[lang].get("back"), callback_data=f"ws_back_form:{workshop_id}:{lang_filter}")

    await callback.message.edit_text(
        text=field_prompts.get(field, gen[lang].get("choose_action")),
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("ws_set_lang_value:"))
async def cb_ws_save_language_field(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    _, workshop_id, target_lang_val, lang_filter = callback.data.split(":")
    
    res_user = await session.execute(select(User.language).where(User.telegram_id == callback.from_user.id))
    lang = res_user.scalar() or "ua"

    item = await _get_workshop(session, int(workshop_id))
    if item:
        item.language = target_lang_val
        await session.commit()

    await state.clear()
    await _show_workshop_form_builder(callback, int(workshop_id), lang_filter, lang, session)


@router.message(EditWorkshop.enter_value, F.text)
async def process_ws_form_input_capture(message: Message, state: FSMContext, session: AsyncSession):
    fsm_data = await state.get_data()
    workshop_id = fsm_data["workshop_id"]
    field = fsm_data["field"]
    lang_filter = fsm_data["lang_filter"]
    
    res_user = await session.execute(select(User.language).where(User.telegram_id == message.from_user.id))
    lang = res_user.scalar() or "ua"

    if fsm_data.get("msg_to_delete"):
        try:
            await message.bot.delete_message(message.chat.id, fsm_data["msg_to_delete"])
        except Exception: 
            pass
    try:
        await message.delete()
    except Exception:
        pass

    item = await _get_workshop(session, workshop_id)
    if item and message.text:
        setattr(item, field, message.text.strip())
        await session.commit()

    await state.clear()
    await _show_workshop_form_builder(message, workshop_id, lang_filter, lang, session)


@router.callback_query(F.data.startswith("ws_back_form:"))
async def cb_ws_cancel_input_return(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession):
    _, workshop_id, lang_filter = callback.data.split(":")
    lang = user.language
    await state.clear()
    await _show_workshop_form_builder(callback, int(workshop_id), lang_filter, lang, session)

# ---------------------------------------------------------------------------
# Фіналізація та збереження
# ---------------------------------------------------------------------------
@router.callback_query(F.data.startswith("ws_save_card:"))
async def cb_ws_finalize_and_publish(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession):
    await state.clear() # 🛡️ ВИПРАВЛЕНО: Скидання FSM
    _, workshop_id, lang_filter = callback.data.split(":")
    lang = user.language

    item = await _get_workshop(session, int(workshop_id))
    if item:
        is_new_draft = item.status == Status.DRAFT
        if is_new_draft:
            item.status = Status.ACTIVE
            
        await session.commit()
        await callback.answer(ws[lang].get("added") if is_new_draft else ws[lang].get("updated"))
    
    await cb_ws_card_detail(callback, user, session)


@router.callback_query(F.data.startswith("ws_cancel_draft:"))
async def cb_ws_cancel_or_delete_draft(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession):
    await state.clear() # 🛡️ ВИПРАВЛЕНО: Скидання FSM
    _, workshop_id, lang_filter = callback.data.split(":")
    lang = user.language

    item = await _get_workshop(session, int(workshop_id))
    if item:
        if item.status == Status.DRAFT:
            await session.delete(item)
            await session.commit()
            await callback.answer(gen[lang].get("cancelled"))
        else:
            await callback.answer(gen[lang].get("back"))

    await _show_filtered_list(callback, session, lang, lang_filter, page=0)


# ===========================================================================
# 🛡️ UX ФОЛБЕК — ПЕРЕХОПЛЕННЯ НЕКОРЕКТНОГО КОНТЕНТУ
# ===========================================================================
@router.message(StateFilter(EditWorkshop), ~F.text)
async def cb_wrong_workshop_input(message: Message, user: User):
    """Спрацює, якщо адмін замість тексту надішле фото, відео чи стікер."""
    try: 
        await message.delete()
    except Exception: 
        pass
    
    lang = user.language
    error_msg = (
        "❌ Будь ласка, надішліть текст." 
        if lang == "ua" 
        else "❌ Please send text only."
    )
    
    alert = await message.answer(error_msg)
    await asyncio.sleep(4)
    try:
        await alert.delete()
    except Exception:
        pass