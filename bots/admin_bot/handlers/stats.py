from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Union

from database.models import User, WorkshopOpeningRequest, MobileWorkshopRequest, Workshop, SupportQuestion, Status
from locales.admin_texts import stats as sts
from bots.admin_bot.keyboards import stats_kb

router = Router()

async def _get_stats_text(lang: str, session: AsyncSession) -> str:
    """Виконує запити до БД та генерує текст статистики."""
    # 1. Рахуємо користувачів
    total_users = (await session.execute(select(func.count(User.user_id)))).scalar() or 0

    # Користувачі за останні 7 днів (UTC)
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    new_users = "—" 
    if hasattr(User, 'created_at'):
        new_users = (await session.execute(select(func.count(User.user_id)).where(User.created_at >= one_week_ago))).scalar() or 0

    # 2. Статистика заявок на відкриття
    op_new = (await session.execute(select(func.count(WorkshopOpeningRequest.request_id)).where(WorkshopOpeningRequest.status == Status.NEW))).scalar() or 0
    op_prog = (await session.execute(select(func.count(WorkshopOpeningRequest.request_id)).where(WorkshopOpeningRequest.status == Status.IN_PROGRESS))).scalar() or 0
    op_comp = (await session.execute(select(func.count(WorkshopOpeningRequest.request_id)).where(WorkshopOpeningRequest.status == Status.COMPLETED))).scalar() or 0

    # 3. Статистика мобільних заявок
    mb_new = (await session.execute(select(func.count(MobileWorkshopRequest.request_id)).where(MobileWorkshopRequest.status == Status.NEW))).scalar() or 0
    mb_prog = (await session.execute(select(func.count(MobileWorkshopRequest.request_id)).where(MobileWorkshopRequest.status == Status.IN_PROGRESS))).scalar() or 0
    mb_comp = (await session.execute(select(func.count(MobileWorkshopRequest.request_id)).where(MobileWorkshopRequest.status == Status.COMPLETED))).scalar() or 0

    # 4. Активні майстерні та Нові питання підтримки
    active_ws = (await session.execute(select(func.count(Workshop.workshop_id)).where(Workshop.status == Status.ACTIVE).where(Workshop.language == "ua"))).scalar() or 0
    new_sup = (await session.execute(select(func.count(SupportQuestion.question_id)).where(SupportQuestion.status == Status.NEW))).scalar() or 0

    # Форматуємо рядок за допомогою шаблону з admin_texts
    text = sts[lang].get("title").format(
        total_users=total_users,
        new_users_week=new_users,
        opening_new=op_new,
        opening_in_progress=op_prog,
        opening_completed=op_comp,
        mobile_new=mb_new,
        mobile_in_progress=mb_prog,
        mobile_completed=mb_comp,
        active_workshops=active_ws,
        support_new=new_sup
    )
    return text


@router.message(Command("stats"))
@router.callback_query(F.data == "menu:stats")
async def cb_stats_menu(event: Union[Message, CallbackQuery], state: FSMContext, user: User, session: AsyncSession):
    await state.clear()  # Очищаємо залишки станів
    lang = user.language

    if isinstance(event, CallbackQuery):
        text = await _get_stats_text(lang, session)
        await event.message.edit_text(text, reply_markup=stats_kb(lang), parse_mode="HTML")
    else:
        # Відправляємо "заглушку" під час генерації для команди /stats
        msg = await event.answer("📊 <i>Збір та аналітика даних, зачекайте...</i>", parse_mode="HTML")
        text = await _get_stats_text(lang, session)
        await msg.edit_text(text, reply_markup=stats_kb(lang), parse_mode="HTML")


@router.callback_query(F.data == "stats:refresh")
async def cb_stats_refresh(callback: CallbackQuery, user: User, session: AsyncSession):
    lang = user.language
    text = await _get_stats_text(lang, session)
    
    try:
        await callback.message.edit_text(text, reply_markup=stats_kb(lang), parse_mode="HTML")
    except Exception:
        pass  # Ігноруємо помилку, якщо статистика не змінилася з минулого разу
        
    await callback.answer(sts[lang].get("btn_refresh"))