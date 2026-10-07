from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, distinct, asc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from database.models import User, FAQQuestion
from bots.user_bot.keyboards import get_faq_categories_kb, get_faq_questions_kb, get_back_kb, h

from locales.texts import general_info as gen

router = Router()

async def unh_category(session: AsyncSession, lang: str, value_hash: str):
    """Повертає назву категорії FAQ за її хешем (callback_data обмежена 64 байтами)."""
    res = await session.execute(select(distinct(FAQQuestion.category)).where(FAQQuestion.language == lang))
    return next((c for c in res.scalars() if h(c) == value_hash), None)

async def get_lang(user_id: int, session: AsyncSession):
    res = await session.execute(select(User.language).where(User.telegram_id == user_id))
    return res.scalar() or "ua"

# --- 1. Початок: Список категорій ---
@router.message(Command("faq"))
@router.callback_query(F.data == "menu:faq")
async def cmd_faq(event: Union[types.Message, types.CallbackQuery], session: AsyncSession):
    """Функція для знаходження категорій FAQ"""
    lang = await get_lang(event.from_user.id, session)
    
    # Отримуємо унікальні категорії для мови, відсортовані за алфавітом
    stmt = select(distinct(FAQQuestion.category)).where(FAQQuestion.language == lang).order_by(asc(FAQQuestion.category))
    res = await session.execute(stmt)
    categories = res.scalars().all()
    
    if categories:
        text = f"<b>{gen[lang].get('faq_label')}</b>\n{gen[lang].get('choose_category')} ({gen[lang].get('page')} 1):"
        kb = get_faq_categories_kb(categories, lang)
    else:
        text = gen[lang].get('no_info')
        kb = get_back_kb(lang, "main_menu") if isinstance(event, types.CallbackQuery) else None
 
    if isinstance(event, types.CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
        try:
            await event.answer()
        except Exception:
            pass
    else:
        await event.answer(text, reply_markup=kb, parse_mode="HTML")

# --- 2. Пагінація категорій ---
@router.callback_query(F.data.startswith("faq_cat_page:"))
async def process_faq_categories_pagination(callback: types.CallbackQuery, session: AsyncSession):
    """Обробка гортання сторінок у списку категорій"""
    page = int(callback.data.split(":")[1])
    lang = await get_lang(callback.from_user.id, session)
    
    stmt = select(distinct(FAQQuestion.category)).where(FAQQuestion.language == lang).order_by(asc(FAQQuestion.category))
    res = await session.execute(stmt)
    categories = res.scalars().all()
    
    text = f"<b>{gen[lang].get('faq_label')}</b>\n{gen[lang].get('choose_category')} ({gen[lang].get('page')} {page + 1}):"
    await callback.message.edit_text(text, reply_markup=get_faq_categories_kb(categories, lang, page=page), parse_mode="HTML")
    await callback.answer()

# --- 3. Вибір категорії -> Список запитань ---
# Додали фільтр на повернення зі сторінки відповіді, щоб зберегти пагінацію
@router.callback_query(F.data.startswith("faq_cat:") | F.data.startswith("faq_back_to_cat:"))
async def show_questions_in_category(callback: types.CallbackQuery, session: AsyncSession):
    """Функція для знаходження питань в категорії"""
    parts = callback.data.split(":")
    # Якщо повертаємось від відповіді — витягуємо збережену сторінку, інакше за дефолтом 0
    page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
    
    lang = await get_lang(callback.from_user.id, session)

    category = await unh_category(session, lang, parts[1])
    if category is None:
        await callback.answer(gen[lang].get('no_info'), show_alert=True)
        return
    
    stmt = select(FAQQuestion).where(
        FAQQuestion.category == category, 
        FAQQuestion.language == lang
    ).order_by(asc(FAQQuestion.question_id))
    
    res = await session.execute(stmt)
    questions = res.scalars().all()

    if not questions:
        await callback.message.edit_text(gen[lang].get('no_info'))
        await callback.answer()
        return
    
    await callback.message.edit_text(
        f"<b>{gen[lang].get('faq_label')}</b>\n{gen[lang].get('select_question')} <b>{category}</b> ({gen[lang].get('page')} {page + 1}):",
        reply_markup=get_faq_questions_kb(questions, lang, category, page=page),
        parse_mode="HTML"
    )
    await callback.answer()

# --- 4. Пагінація запитань усередині категорії ---
@router.callback_query(F.data.startswith("faq_q_page:"))
async def process_faq_questions_pagination(callback: types.CallbackQuery, session: AsyncSession):
    """Обробка гортання сторінок у списку запитань"""
    _, category_h, page = callback.data.split(":")
    page = int(page)
    lang = await get_lang(callback.from_user.id, session)

    category = await unh_category(session, lang, category_h)
    if category is None:
        await callback.answer(gen[lang].get('no_info'), show_alert=True)
        return
    
    stmt = select(FAQQuestion).where(
        FAQQuestion.category == category, 
        FAQQuestion.language == lang
    ).order_by(asc(FAQQuestion.question_id))
    
    res = await session.execute(stmt)
    questions = res.scalars().all()
    
    text = f"<b>{gen[lang].get('faq_label')}</b>\n{gen[lang].get('select_question')} <b>{category}</b> ({gen[lang].get('page')} {page + 1}):"
    await callback.message.edit_text(text,
                                     reply_markup=get_faq_questions_kb(questions, lang, category, page=page),
                                     parse_mode="HTML")
    await callback.answer()

# --- 5. Вибір запитання -> Відповідь (Clean View!) ---
@router.callback_query(F.data.startswith("faq_id:"))
async def show_faq_answer(callback: types.CallbackQuery, session: AsyncSession):
    """Вивід тексту відповіді у тому самому повідомленні з кнопкою Назад"""
    # Callback data format: "faq_id:{question_id}:{current_page}"
    parts = callback.data.split(":")
    q_id = int(parts[1])
    # Передаємо сторінку пагінації через кнопку (якщо її немає в callback_data від клавіатури, ставимо 0)
    back_page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
    
    lang = await get_lang(callback.from_user.id, session)
    
    stmt = select(FAQQuestion).where(FAQQuestion.question_id == q_id)
    res = await session.execute(stmt)
    item = res.scalar_one_or_none()
    
    if item:
        text = f"<b>{gen[lang].get('faq_label')}</b>\n<b>{item.question}</b>\n\n{item.answer}"
        
        # Динамічно створюємо кнопку повернення до списку цієї ж категорії на ту саму сторінку
        builder = InlineKeyboardBuilder()
        builder.button(
            text=gen[lang].get('back', 'Назад'), 
            callback_data=f"faq_back_to_cat:{h(item.category)}:{back_page}"
        )
        
        # Редагуємо поточне повідомлення замість відправки нового спаму
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

# --- 6. Повернення до головного меню FAQ ---
@router.callback_query(F.data == "faq_main")
async def faq_back_to_main(callback: types.CallbackQuery, session: AsyncSession):
    """Повернення до списку категорій"""
    lang = await get_lang(callback.from_user.id, session)

    stmt = select(distinct(FAQQuestion.category)).where(FAQQuestion.language == lang).order_by(asc(FAQQuestion.category))
    res = await session.execute(stmt)
    categories = res.scalars().all()
    
    await callback.message.edit_text(
        f"<b>{gen[lang].get('faq_label')}</b>\n{gen[lang].get('choose_category')} ({gen[lang].get('page')} 1):", 
        reply_markup=get_faq_categories_kb(categories, lang), 
        parse_mode="HTML"
    )
    await callback.answer()