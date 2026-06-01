import asyncio
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import User, SupportQuestion, Status
from locales.admin_texts import support as sup, general as gen
from bots.admin_bot.states import ReplySupport
from bots.admin_bot.keyboards import (
    support_menu_kb, support_list_kb, support_detail_kb, back_kb,
)
from config import settings

router = Router()
PAGE_SIZE = 8


# ---------------------------------------------------------------------------
# Допоміжні функції
# ---------------------------------------------------------------------------

def _format_detail(lang: str, item: SupportQuestion) -> str:
    # 🛡️ ВИПРАВЛЕНО: Безпечне отримання даних користувача
    user_name = item.user.name if item.user else "Anonymous"
    user_phone = item.user.phone_number if item.user else "—"

    return sup[lang].get("detail").format(
        question_id = item.question_id,
        user_name   = user_name,
        user_phone  = user_phone,
        created_at  = item.created_at.strftime("%d.%m.%Y %H:%M"),
        status      = sup[lang].get(f"status_{item.status.value.lower()}", item.status.value),
        question    = item.question,
    )


async def _show_list(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
    status_filter: str,
    page: int,
):
    base_q = select(SupportQuestion).options(selectinload(SupportQuestion.user))

    if status_filter == "NEW":
        base_q = base_q.where(SupportQuestion.status == Status.NEW)

    total = (await session.execute(
        select(func.count()).select_from(base_q.subquery())
    )).scalar()
    total_pages = max(1, -(-total // PAGE_SIZE))

    items = (await session.execute(
        base_q.order_by(SupportQuestion.created_at.desc())
              .offset(page * PAGE_SIZE).limit(PAGE_SIZE)
    )).scalars().all()

    if not items:
        try:
            await callback.message.edit_text(
                text=sup[lang].get("list_empty"),
                reply_markup=support_menu_kb(lang),
            )
        except Exception:
            pass
        return

    status_label_key = f"status_{status_filter.lower()}" if status_filter != "ALL" else "btn_all"
    
    try:
        await callback.message.edit_text(
            text=sup[lang].get("list_title").format(
                status_label=sup[lang].get(status_label_key, status_filter),
                count=total,
            ),
            reply_markup=support_list_kb(lang, items, page, total_pages, status_filter),
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Фільтр → список
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("sup_filter:"))
async def cb_sup_filter(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession):
    await state.clear()
    status_filter = callback.data.split(":")[1]
    lang = user.language

    await state.update_data(sup_filter=status_filter)
    await _show_list(callback, session, lang, status_filter, page=0)


@router.callback_query(F.data.startswith("sup_page:"))
async def cb_sup_page(callback: CallbackQuery, user: User, session: AsyncSession):
    _, status_filter, page = callback.data.split(":")
    lang = user.language

    await _show_list(callback, session, lang, status_filter, int(page))


# ---------------------------------------------------------------------------
# Деталі питання
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("sup_detail:"))
async def cb_sup_detail(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession):
    question_id = int(callback.data.split(":")[1])
    lang = user.language

    item = (await session.execute(
        select(SupportQuestion)
        .where(SupportQuestion.question_id == question_id)
        .options(selectinload(SupportQuestion.user))
    )).scalar()

    if not item:
        await callback.answer(gen[lang].get("not_found"), show_alert=True)
        return

    fsm = await state.get_data()
    await state.update_data(sup_filter=fsm.get("sup_filter", "ALL"))

    try:
        await callback.message.edit_text(
            text=_format_detail(lang, item),
            reply_markup=support_detail_kb(lang, item.question_id, item.status.value),
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Відповідь на питання — FSM
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("sup_reply:"))
async def cb_sup_reply(callback: CallbackQuery, state: FSMContext, user: User):
    question_id = int(callback.data.split(":")[1])
    lang = user.language

    await state.set_state(ReplySupport.enter_text)
    await state.update_data(
        lang=lang,
        question_id=question_id,
        bot_msg_id=callback.message.message_id,
    )

    try:
        await callback.message.edit_text(
            text=sup[lang].get("ask_reply"),
            reply_markup=back_kb(lang, f"sup_detail:{question_id}"),
        )
    except Exception:
        pass


# 🎯 ВИПРАВЛЕНО: Додано фільтр F.text, щоб приймати лише текст
@router.message(ReplySupport.enter_text, F.text)
async def reply_sup_text(message: Message, state: FSMContext, session: AsyncSession):
    fsm = await state.get_data()
    admin_lang = fsm["lang"]

    try:
        await message.delete()
    except Exception:
        pass

    item = (await session.execute(
        select(SupportQuestion)
        .where(SupportQuestion.question_id == fsm["question_id"])
        .options(selectinload(SupportQuestion.user))
    )).scalar()

    if not item:
        await state.clear()
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=fsm["bot_msg_id"],
                text=gen[admin_lang].get("not_found"),
                reply_markup=back_kb(admin_lang, "menu:support"),
            )
        except Exception:
            pass
        return

    item.answer = message.text.strip()
    item.status = Status.COMPLETED
    await session.commit()

    # 🎯 ВИПРАВЛЕНО: Сповіщення формується мовою КОРИСТУВАЧА, а не адміна
    if item.user:
        user_lang = getattr(item.user, "language", "ua") or "ua"
        notify_text = sup[user_lang].get("notify_reply")
        
        if notify_text:
            async with Bot(token=settings.USER_BOT_TOKEN.get_secret_value()) as user_bot:
                try:
                    await user_bot.send_message(
                        chat_id=item.user.telegram_id,
                        text=notify_text.format(text=item.answer),
                    )
                except Exception:
                    pass

    await state.clear()

    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=fsm["bot_msg_id"],
            text=_format_detail(admin_lang, item),
            reply_markup=support_detail_kb(admin_lang, item.question_id, item.status.value),
        )
    except Exception:
        pass


# ===========================================================================
# 🛡️ UX ФОЛБЕК — ПЕРЕХОПЛЕННЯ НЕКОРЕКТНОГО КОНТЕНТУ
# ===========================================================================

@router.message(StateFilter(ReplySupport), ~F.text)
async def cb_wrong_support_reply(message: Message, user: User):
    """Спрацює, якщо адмін замість тексту відповіді надішле фото, голосове чи файл."""
    try: 
        await message.delete()
    except Exception: 
        pass
    
    lang = user.language
    error_msg = (
        "❌ Будь ласка, надішліть відповідь текстом." 
        if lang == "ua" 
        else "❌ Please send the reply as text."
    )
    
    alert = await message.answer(error_msg)
    
    await asyncio.sleep(4)
    try:
        await alert.delete()
    except Exception:
        pass