from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import settings
from database.models import User, WorkshopOpeningRequest, MobileWorkshopRequest, Status
from locales.admin_texts import requests as req
from bots.admin_bot.keyboards import (
    requests_filter_kb, requests_list_kb,
    request_detail_kb,
)

router = Router()
PAGE_SIZE = 8

# ---------------------------------------------------------------------------
# Допоміжні функції
# ---------------------------------------------------------------------------

def _status_from_filter(status_filter: str) -> Status | None:
    """Перетворює рядок фільтра на enum Status або None (для 'ALL')."""
    return {
        "NEW":         Status.NEW,
        "IN_PROGRESS": Status.IN_PROGRESS,
    }.get(status_filter)


def _status_label(lang: str, status_filter: str) -> str:
    return {
        "NEW":         req[lang].get("status_new"),
        "IN_PROGRESS": req[lang].get("status_in_progress"),
        "ALL":         req[lang].get("btn_filter_all"),
    }.get(status_filter, status_filter)


def _model_by_type(req_type: str):
    """Повертає модель залежно від типу заявки."""
    return WorkshopOpeningRequest if req_type == "opening" else MobileWorkshopRequest


def _format_detail(lang: str, req_type: str, item) -> str:
    """Формує текст деталі заявки на основі чистих шаблонів з файлу локалізації."""
    base = dict(
        request_id  = item.request_id,
        name        = item.user.name if item.user else "Anonymous",
        phone_number= item.user.phone_number if item.user else "—",
        country     = item.country,
        region      = item.region or "—",
        city        = item.city,
        created_at  = item.created_at.strftime("%d.%m.%Y %H:%M"),
        status      = req[lang].get(f"status_{item.status.value.lower()}", item.status.value),
    )
    
    category_key = "category_opening" if req_type == "opening" else "category_mobile"
    category_label = req[lang].get(category_key, "")

    if req_type == "opening":
        details = req[lang].get("opening_detail").format(
            **base,
            church_name       = item.church_name or "—",
            known_information = item.known_information or "—",
        )
    else:
        details = req[lang].get("mobile_detail").format(
            **base,
            organization = item.organization or "—",
            purpose      = item.purpose or "—",
        )
        
    header = req[lang].get("detail_header").format(category_label=category_label)
    return f"{header}{details}"


# ---------------------------------------------------------------------------
# 1. Екран вибору фільтра (Нові / В роботі / Всі)
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("req_type:"))
async def cb_req_type(callback: CallbackQuery, user: User): 
    req_type = callback.data.split(":")[1]
    lang = user.language

    category_key = "category_opening" if req_type == "opening" else "category_mobile"
    category_label = req[lang].get(category_key, "")

    try:
        await callback.message.edit_text(
            text=req[lang].get("filter_menu_title").format(category_label=category_label),
            reply_markup=requests_filter_kb(lang, req_type),
            parse_mode="HTML"
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 2. Фільтр → список заявок
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("req_filter:"))
async def cb_req_filter(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession): 
    _, req_type, status_filter = callback.data.split(":")
    lang = user.language
    await state.update_data(status_filter=status_filter)
    await _show_list(callback, session, lang, req_type, status_filter, page=0)


@router.callback_query(F.data.startswith("req_page:"))
async def cb_req_page(callback: CallbackQuery, user: User, session: AsyncSession): 
    parts = callback.data.split(":")
    req_type      = parts[1]
    status_filter = parts[2]
    page          = int(parts[3])
    lang = user.language
    await _show_list(callback, session, lang, req_type, status_filter, page)


async def _show_list(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
    req_type: str,
    status_filter: str,
    page: int,
):
    Model = _model_by_type(req_type)
    status = _status_from_filter(status_filter)

    base_q = select(Model).options(selectinload(Model.user))
    if status:
        base_q = base_q.where(Model.status == status)

    count_q = select(func.count()).select_from(base_q.subquery())
    total = (await session.execute(count_q)).scalar()
    total_pages = max(1, -(-total // PAGE_SIZE)) 

    items_q = base_q.order_by(Model.created_at.desc()) \
                    .offset(page * PAGE_SIZE).limit(PAGE_SIZE)
    items = (await session.execute(items_q)).scalars().all()

    category_key = "category_opening" if req_type == "opening" else "category_mobile"
    category_label = req[lang].get(category_key, "")

    if not items:
        try:
            await callback.message.edit_text(
                text=f"<b>📂 {category_label}</b>\n----------------------------------------\n❌ {req[lang].get('list_empty')}",
                reply_markup=requests_filter_kb(lang, req_type),
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    main_title = req[lang].get("list_title").format(
        category_label=category_label,
        status_label=_status_label(lang, status_filter),
        count=total,
    )

    try:
        await callback.message.edit_text(
            text=main_title,
            reply_markup=requests_list_kb(lang, items, req_type, status_filter, page, total_pages),
            parse_mode="HTML"
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 3. Деталі заявки
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("req_detail:"))
async def cb_req_detail(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession): 
    _, req_type, request_id = callback.data.split(":")
    lang = user.language
    Model = _model_by_type(req_type)

    item = (await session.execute(
        select(Model)
        .where(Model.request_id == int(request_id))
        .options(selectinload(Model.user))
    )).scalar()

    if not item:
        await callback.answer(req[lang].get("list_empty"), show_alert=True)
        return

    fsm_data = await state.get_data()
    status_filter = fsm_data.get("status_filter", "ALL")

    try:
        await callback.message.edit_text(
            text=_format_detail(lang, req_type, item),
            reply_markup=request_detail_kb(lang, req_type, item.request_id, item.status.value, status_filter),
            parse_mode="HTML"
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 4. Зміна статусу та двосторонній інтерфейс сповіщень
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("req_status:"))
async def cb_req_status(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession): 
    _, req_type, request_id, new_status = callback.data.split(":")
    admin_lang = user.language  # Мова адміністратора (для адмін-панелі)
    Model = _model_by_type(req_type)

    item = (await session.execute(
        select(Model)
        .where(Model.request_id == int(request_id))
        .options(selectinload(Model.user))
    )).scalar()

    if not item:
        await callback.answer(req[admin_lang].get("list_empty"), show_alert=True)
        return

    # Оновлюємо статус
    item.status = Status(new_status)
    await session.commit()

    # 🎯 ВИПРАВЛЕНО: Сповіщення формується мовою КОРИСТУВАЧА, а не адміна
    if item.user:
        user_lang = getattr(item.user, "language", "ua") or "ua"
        
        req_type_key = "btn_workshop_opening" if req_type == "opening" else "btn_mobile"
        req_type_label = req[user_lang].get(req_type_key, "").lower()

        notify_template = req[user_lang].get(f"notify_{new_status.lower()}") or req[user_lang].get(f"notify_{new_status}")
        
        if notify_template:
            async with Bot(token=settings.USER_BOT_TOKEN.get_secret_value()) as user_bot:
                try:
                    await user_bot.send_message(
                        chat_id=item.user.telegram_id,
                        text=notify_template.format(req_type_label=req_type_label),
                    )
                except Exception:
                    pass 

    fsm_data = await state.get_data()
    status_filter = fsm_data.get("status_filter", "ALL")

    # Повертаємо оновлену картку (адміністратору його мовою)
    try:
        await callback.message.edit_text(
            text=_format_detail(admin_lang, req_type, item),
            reply_markup=request_detail_kb(admin_lang, req_type, item.request_id, item.status.value, status_filter),
            parse_mode="HTML"
        )
    except Exception:
        pass # Якщо статус той самий, Telegram видасть помилку, ми її просто ігноруємо

    await callback.answer(
        req[admin_lang].get("status_changed").format(
            request_id=item.request_id,
            status=req[admin_lang].get(f"status_{new_status.lower()}", new_status),
        )
    )