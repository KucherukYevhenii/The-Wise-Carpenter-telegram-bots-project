from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from database.models import User, SupportQuestion, Status
from bots.user_bot.states import QSTStates
from bots.user_bot.keyboards import (
    get_qstort_main_kb, 
    get_confirm_question_kb, 
    get_qstort_cancel_kb, 
    get_archive_kb
)
from locales.texts import questions_phrases as qst, status_phrases as sts, general as gen

router = Router()

# Допоміжна функція для отримання мови (ua/en)
async def get_lang(user_id: int, session: AsyncSession):
    res = await session.execute(select(User.language).where(User.telegram_id == user_id))
    return res.scalar() or "ua"

# --- 1. Головне меню підтримки ---
@router.message(Command("ask_question"))
@router.callback_query(F.data == "open_qstort")
async def open_support_menu(event: Union[types.Message, types.CallbackQuery], session: AsyncSession, state: FSMContext):
    await state.clear()
    user_id = event.from_user.id
    lang = await get_lang(user_id, session)
    L = qst[lang]
    
    text = f"<b>{L['questions_label']}</b>\n\n{L['questions_desc']}"
    kb = get_qstort_main_kb(lang)
    
    # Якщо це повідомлення (команда) — надсилаємо нове
    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    # Якщо це колбек від інлайн-кнопки
    else:
        try:
            # Намагаємось відредагувати поточний текст
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            # Якщо повідомлення вже було видалене в іншому хендлері — безпечно шлемо нове
            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
        try:
            await event.answer()
        except Exception:
            pass


# --- 2. Початок введення питання ---
@router.callback_query(F.data == "ask_qstort_start")
async def ask_question_start(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    lang = await get_lang(callback.from_user.id, session)
    L = qst[lang]
    
    try:
        await callback.message.delete() # Очищаємо старе меню
    except Exception:
        pass
    
    msg = await callback.message.answer(
        f"<b>{L['question_desc']}</b>", 
        reply_markup=get_qstort_cancel_kb(lang),
        parse_mode="HTML"
    )
    
    await state.update_data(messages_to_delete=[msg.message_id])
    await state.set_state(QSTStates.waiting_for_question)
    try:
        await callback.answer()
    except Exception:
        pass

# --- 3. Отримання текста та показ прев'ю (Підтвердження) ---
@router.message(QSTStates.waiting_for_question)
async def process_question_text(message: types.Message, state: FSMContext, session: AsyncSession):
    lang = await get_lang(message.from_user.id, session)
    L = qst[lang]
    
    question_text = message.text.strip() if message.text else ""

    if not question_text:
        return

    # Зберігаємо текст у FSM чернетку
    await state.update_data(draft_question=question_text)
    
    # Отримуємо та видаляємо попереднє повідомлення-інструкцію бота
    data = await state.get_data()
    for m_id in data.get("messages_to_delete", []):
        try: 
            await message.bot.delete_message(message.chat.id, m_id)
        except Exception: 
            pass

    # Повідомлення для підтвердження
    confirm_text = f"<b>{L['question_approval']}:</b>\n\n<i>{question_text}</i>"
    sent_msg = await message.answer(confirm_text, reply_markup=get_confirm_question_kb(lang), parse_mode="HTML")
    
    # Оновлюємо список на видалення (включаючи повідомлення юзера та поточне прев'ю)
    await state.update_data(messages_to_delete=[message.message_id, sent_msg.message_id])
    await state.set_state(QSTStates.waiting_for_confirmation)


# --- 4. Запис у базу та фінал ---
@router.callback_query(F.data == "confirm_question_send")
async def confirm_send_handler(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    question_text = data.get("draft_question")
    lang = await get_lang(callback.from_user.id, session)
    L = qst[lang]

    # Шукаємо внутрішній user_id
    res = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
    user = res.scalar()

    try:
        # Створюємо тікет, статус суворо у верхньому регістрі з Enum
        new_q = SupportQuestion(
            user_id=user.user_id,
            question=question_text,
            status=Status.NEW
        )
        session.add(new_q)
        await session.commit()
        
        # Повністю очищаємо чат від проміжних кроків оформлення питання
        for m_id in data.get("messages_to_delete", []):
            try: 
                await callback.bot.delete_message(callback.message.chat.id, m_id)
            except Exception: 
                pass
            
        await callback.message.answer(f"{L['feedback']}")
        await state.clear()
        
        # Передаємо об'єкт кліку 'callback' напряму. Метод open_support_menu сам 
        # зрозуміє, що старе повідомлення видалене, і надішле нове меню через .answer()
        await open_support_menu(callback, session, state)
        
    except Exception as e:
        print(f"Error: {e}")
        await session.rollback()
        try:
            await callback.answer(L['error'], show_alert=True)
        except Exception:
            pass


# --- 5. Архів питань з пагінацією ---
@router.callback_query(F.data.startswith("qstort_archive") | F.data.startswith("archive_page:"))
async def view_archive(callback: types.CallbackQuery, session: AsyncSession):
    # Визначаємо сторінку
    page = int(callback.data.split(":")[1]) if ":" in callback.data else 0
    lang = await get_lang(callback.from_user.id, session)
    L = qst[lang]

    user_res = await session.execute(select(User.user_id).where(User.telegram_id == callback.from_user.id))
    u_id = user_res.scalar()

    # Беремо питання юзера (від нових до старих)
    q_res = await session.execute(
        select(SupportQuestion)
        .where(SupportQuestion.user_id == u_id)
        .order_by(SupportQuestion.created_at.desc())
    )
    questions = q_res.scalars().all()

    if not questions:
        try:
            await callback.answer(L['empty_archive'], show_alert=True)
        except Exception:
            pass
        return

    await callback.message.edit_text(
        f"<b>{L['archive_questions']}</b>",
        reply_markup=get_archive_kb(questions, lang, page=page),
        parse_mode="HTML"
    )
    try:
        await callback.answer()
    except Exception:
        pass

# --- 6. Детальний перегляд одного питання ---
@router.callback_query(F.data.startswith("view_q:"))
async def view_single_question(callback: types.CallbackQuery, session: AsyncSession):
    params = callback.data.split(":")
    q_id, back_page = int(params[1]), int(params[2])
    
    res = await session.execute(select(SupportQuestion).where(SupportQuestion.question_id == q_id))
    q = res.scalar()
    
    lang = await get_lang(callback.from_user.id, session)
    L = qst[lang]
    S = sts[lang]

    # Текстове представлення статусу з твого словника
    status_map = {
        Status.NEW: S["status_new"],
        Status.IN_PROGRESS: S["status_in_progress"],
        Status.COMPLETED: S["status_completed"],
        Status.REJECTED: S["status_rejected"],
        Status.CLOSED: S["status_closed"]
    }
    
    status_text = status_map.get(q.status, S["status_new"])
    
    # Виправлено внутрішні лапки з подвійних на одинарні 'question_arch', 'status_arch', 'answer_arch'
    text = (
        f"<b>{L.get('question_arch')}:</b>\n{q.question}\n\n"
        f"<b>{L.get('status_arch')}:</b> {status_text}\n"
    )
    
    # Якщо є відповідь в БД — виводимо її
    if q.answer:
        text += f"<b>{L.get('answer_arch')}:</b>\n{q.answer}"
    
    # Кнопка повернення на ту ж сторінку пагінації
    builder = InlineKeyboardBuilder()
    builder.button(text=gen[lang].get("back"), callback_data=f"archive_page:{back_page}")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    try:
        await callback.answer()
    except Exception:
        pass