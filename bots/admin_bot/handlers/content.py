import asyncio
from typing import Union
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.models import User, FAQQuestion, GeneralInformation
from bots.admin_bot.states import AddFAQ, AddInfo, EditFAQ, EditInfo
from bots.admin_bot.keyboards import (
    content_menu_kb, faq_list_kb, faq_detail_kb, faq_edit_fields_kb,
    info_list_kb, info_detail_kb, info_edit_fields_kb, back_kb,
    lang_select_kb
)
from locales.admin_texts import content as cnt, general as gen

router = Router()
PAGE_SIZE = 8

# ===========================================================================
# 📑 FAQ — НАВІГАЦІЯ ТА СПИСКИ
# ===========================================================================

@router.message(Command("content"))
@router.callback_query(F.data == "menu:content")
async def cmd_content_main(event: Union[Message, CallbackQuery], user: User, state: FSMContext):
    await state.clear()  # Примусово скидаємо будь-які застряглі FSM-стани додавання/редагування
    lang = user.language
    text = f"<b>{cnt[lang].get('title')}</b>"
    
    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=content_menu_kb(lang), parse_mode="HTML")
        except Exception:
            try: await event.message.delete()
            except: pass
            await event.message.answer(text, reply_markup=content_menu_kb(lang), parse_mode="HTML")
    else:
        await event.answer(text, reply_markup=content_menu_kb(lang), parse_mode="HTML")


@router.callback_query(F.data.startswith("cnt:faq:"))
async def cb_faq_list(callback: CallbackQuery, user: User, session: AsyncSession):
    page = int(callback.data.split(":")[-1])
    lang = user.language

    total = (await session.execute(select(func.count(FAQQuestion.question_id)))).scalar() or 0
    total_pages = max(1, -(-total // PAGE_SIZE))

    stmt = select(FAQQuestion).order_by(FAQQuestion.category, FAQQuestion.question_id).offset(page * PAGE_SIZE).limit(PAGE_SIZE)
    items = (await session.execute(stmt)).scalars().all()

    text = f"<b>{cnt[lang].get('faq_title')}</b>"

    if not items:
        await callback.message.edit_text(text=cnt[lang].get("faq_list_empty"), reply_markup=faq_list_kb(lang, [], 0, 1), parse_mode="HTML")
        return

    try:
        await callback.message.edit_text(text, reply_markup=faq_list_kb(lang, items, page, total_pages), parse_mode="HTML")
    except Exception:
        try: await callback.message.delete()
        except: pass
        await callback.message.answer(text, reply_markup=faq_list_kb(lang, items, page, total_pages), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("faq_page:"))
async def cb_faq_pagination(callback: CallbackQuery, user: User, session: AsyncSession):
    await cb_faq_list(callback, user, session)


@router.callback_query(F.data.startswith("faq_detail:"))
async def cb_faq_detail(callback: CallbackQuery, user: User, session: AsyncSession):
    parts = callback.data.split(":")
    faq_id = int(parts[1])
    back_page = int(parts[2]) if len(parts) > 2 else 0
    lang = user.language

    item = (await session.execute(select(FAQQuestion).where(FAQQuestion.question_id == faq_id))).scalar_one_or_none()
    if not item:
        await callback.answer(gen[lang].get("not_found"), show_alert=True)
        return

    text = cnt[lang].get("faq_detail").format(
        question_id=item.question_id,
        language=item.language.upper(),
        category=item.category,
        question=item.question,
        answer=item.answer
    )
    await callback.message.edit_text(text, reply_markup=faq_detail_kb(lang, faq_id, back_page), parse_mode="HTML")


# ===========================================================================
# ➕ FAQ — ДОДАВАННЯ З ПОВНИМ СКИНУТТЯМ СТАНІВ НА КОЖНОМУ КРОЦІ
# ===========================================================================

@router.callback_query(F.data == "faq:add")
async def cb_add_faq_start(callback: CallbackQuery, user: User, state: FSMContext):
    lang = user.language
    await state.set_state(AddFAQ.language)
    await state.update_data(bot_msg_id=callback.message.message_id)
    await callback.message.edit_text(cnt[lang].get("ask_faq_lang"), reply_markup=lang_select_kb(lang), parse_mode="HTML")


@router.callback_query(AddFAQ.language, F.data == "menu:content")
async def cb_back_from_faq_add_lang(callback: CallbackQuery, state: FSMContext, user: User):
    await state.clear()
    await cmd_content_main(callback, user, state)


@router.callback_query(AddFAQ.language, F.data.startswith("lang:"))
async def process_add_faq_lang(callback: CallbackQuery, state: FSMContext, user: User):
    chosen_lang = callback.data.split(":")[-1]
    await state.update_data(chosen_lang=chosen_lang)
    
    lang = user.language
    await state.set_state(AddFAQ.category)
    await callback.message.edit_text(cnt[lang].get("ask_faq_category"), reply_markup=back_kb(lang, "faq_add_cancel"), parse_mode="HTML")


@router.message(AddFAQ.category, F.text)
async def process_add_faq_category(message: Message, state: FSMContext, user: User):
    fsm_data = await state.get_data()
    await state.update_data(category=message.text.strip())
    try: await message.delete()
    except: pass
    
    lang = user.language
    await state.set_state(AddFAQ.question)
    await message.bot.edit_message_text(
        chat_id=message.chat.id, message_id=fsm_data["bot_msg_id"],
        text=cnt[lang].get("ask_faq_question"), reply_markup=back_kb(lang, "faq_add_cancel"), parse_mode="HTML"
    )


@router.message(AddFAQ.question, F.text)
async def process_add_faq_question(message: Message, state: FSMContext, user: User):
    fsm_data = await state.get_data()
    await state.update_data(question=message.text.strip())
    try: await message.delete()
    except: pass
    
    lang = user.language
    await state.set_state(AddFAQ.answer)
    await message.bot.edit_message_text(
        chat_id=message.chat.id, message_id=fsm_data["bot_msg_id"],
        text=cnt[lang].get("ask_faq_answer"), reply_markup=back_kb(lang, "faq_add_cancel"), parse_mode="HTML"
    )


@router.message(AddFAQ.answer, F.text)
async def process_add_faq_finalize(message: Message, state: FSMContext, user: User, session: AsyncSession):
    fsm_data = await state.get_data()
    try: await message.delete()
    except: pass
    
    new_faq = FAQQuestion(
        language=fsm_data["chosen_lang"],
        category=fsm_data["category"],
        question=fsm_data["question"],
        answer=message.text.strip()
    )
    session.add(new_faq)
    await session.commit()
    await state.clear()
    
    lang = user.language
    await message.bot.edit_message_text(
        chat_id=message.chat.id, message_id=fsm_data["bot_msg_id"],
        text=cnt[lang].get("faq_added"), reply_markup=back_kb(lang, "cnt:faq:0"), parse_mode="HTML"
    )


@router.callback_query(StateFilter(AddFAQ), F.data == "faq_add_cancel")
async def cb_cancel_faq_addition_chain(callback: CallbackQuery, state: FSMContext, user: User):
    await state.clear()
    await callback.answer(gen[user.language].get("cancelled"))
    await cmd_content_main(callback, user, state)


# ===========================================================================
# ⚙️ FAQ — РЕДАГУВАННЯ СТАНІВ
# ===========================================================================

@router.callback_query(F.data.startswith("faq_edit:"))
async def cb_faq_edit_menu(callback: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    faq_id = int(callback.data.split(":")[1])
    lang = user.language
    await callback.message.edit_text(
        text=gen[lang].get("choose_action"),
        reply_markup=faq_edit_fields_kb(lang, faq_id)
    )


@router.callback_query(F.data.startswith("faq_back_detail:"))
async def cb_faq_back_to_detail_view(callback: CallbackQuery, user: User, session: AsyncSession):
    faq_id = int(callback.data.split(":")[1])
    callback.data = f"faq_detail:{faq_id}:0"
    await cb_faq_detail(callback, user, session)


@router.callback_query(F.data.startswith("faq_field:"))
async def cb_faq_field_trigger(callback: CallbackQuery, state: FSMContext, user: User):
    _, faq_id, field = callback.data.split(":")
    lang = user.language

    await state.set_state(EditFAQ.enter_value)
    await state.update_data(faq_id=int(faq_id), field=field, bot_msg_id=callback.message.message_id)

    prompts = {
        "category": cnt[lang].get("ask_faq_category"),
        "question": cnt[lang].get("ask_faq_question"),
        "answer": cnt[lang].get("ask_faq_answer")
    }
    await callback.message.edit_text(text=prompts.get(field, gen[lang].get("choose_action")), reply_markup=back_kb(lang, f"faq_edit:{faq_id}"))


@router.message(EditFAQ.enter_value, F.text)
async def process_faq_field_save(message: Message, state: FSMContext, session: AsyncSession, user: User):
    fsm_data = await state.get_data()
    lang = user.language
    
    try: await message.delete()
    except: pass

    await session.execute(
        update(FAQQuestion).where(FAQQuestion.question_id == fsm_data["faq_id"]).values({fsm_data["field"]: message.text.strip()})
    )
    await session.commit()
    await state.clear()

    item = (await session.execute(select(FAQQuestion).where(FAQQuestion.question_id == fsm_data["faq_id"]))).scalar_one_or_none()
    text = cnt[lang].get("faq_detail").format(
        question_id=item.question_id, language=item.language.upper(), category=item.category, question=item.question, answer=item.answer
    )
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=fsm_data["bot_msg_id"], text=text, reply_markup=faq_detail_kb(lang, item.question_id, 0))


@router.callback_query(F.data.startswith("faq_delete:"))
async def cb_faq_delete(callback: CallbackQuery, user: User, session: AsyncSession):
    faq_id = int(callback.data.split(":")[1])
    await session.execute(delete(FAQQuestion).where(FAQQuestion.question_id == faq_id))
    await session.commit()
    await callback.answer(cnt[user.language].get("faq_deleted"))
    await cb_faq_list(callback, user, session)


# ===========================================================================
# 📑 ЗАГАЛЬНА ІНФОРМАЦІЯ — НАВІГАЦІЯ ТА СПИСКИ
# ===========================================================================

@router.callback_query(F.data.startswith("cnt:info:"))
async def cb_info_list(callback: CallbackQuery, user: User, session: AsyncSession):
    page = int(callback.data.split(":")[-1])
    lang = user.language

    total = (await session.execute(select(func.count(GeneralInformation.information_id)))).scalar() or 0
    total_pages = max(1, -(-total // PAGE_SIZE))

    stmt = select(GeneralInformation).order_by(GeneralInformation.category).offset(page * PAGE_SIZE).limit(PAGE_SIZE)
    items = (await session.execute(stmt)).scalars().all()

    text = f"<b>{cnt[lang].get('info_title')}</b>"

    if not items:
        await callback.message.edit_text(text=cnt[lang].get("info_list_empty"), reply_markup=info_list_kb(lang, [], 0, 1), parse_mode="HTML")
        return

    try:
        await callback.message.edit_text(text, reply_markup=info_list_kb(lang, items, page, total_pages), parse_mode="HTML")
    except Exception:
        try: await callback.message.delete()
        except: pass
        await callback.message.answer(text, reply_markup=info_list_kb(lang, items, page, total_pages), parse_mode="HTML")


@router.callback_query(F.data.startswith("info_page:"))
async def cb_info_pagination(callback: CallbackQuery, user: User, session: AsyncSession):
    await cb_info_list(callback, user, session)


@router.callback_query(F.data.startswith("info_detail:"))
async def cb_info_detail(callback: CallbackQuery, user: User, session: AsyncSession):
    parts = callback.data.split(":")
    info_id = int(parts[1])
    back_page = int(parts[2]) if len(parts) > 2 else 0
    lang = user.language

    item = (await session.execute(select(GeneralInformation).where(GeneralInformation.information_id == info_id))).scalar_one_or_none()
    if not item:
        await callback.answer(gen[lang].get("not_found"), show_alert=True)
        return

    text = cnt[lang].get("info_detail").format(
        information_id=item.information_id,
        language=item.language.upper(),
        category=item.category,
        information=item.information
    )

    await callback.message.edit_text(text, reply_markup=info_detail_kb(lang, info_id, back_page), parse_mode="HTML")


# ===========================================================================
# ➕ ЗАГАЛЬНА ІНФОРМАЦІЯ — ДОДАВАННЯ З МИТТЄВИМ ЗБЕРЕЖЕННЯМ В ТЕКСТ
# ===========================================================================

@router.callback_query(F.data == "info:add")
async def cb_add_info_start(callback: CallbackQuery, user: User, state: FSMContext):
    lang = user.language
    await state.set_state(AddInfo.language)
    await state.update_data(bot_msg_id=callback.message.message_id)
    await callback.message.edit_text(cnt[lang].get("ask_info_lang"), reply_markup=lang_select_kb(lang), parse_mode="HTML")


@router.callback_query(AddInfo.language, F.data == "menu:content")
async def cb_back_from_info_add_lang(callback: CallbackQuery, state: FSMContext, user: User):
    await state.clear()
    await cmd_content_main(callback, user, state)


@router.callback_query(AddInfo.language, F.data.startswith("lang:"))
async def process_add_info_lang(callback: CallbackQuery, state: FSMContext, user: User):
    await state.update_data(chosen_lang=callback.data.split(":")[-1])
    lang = user.language
    await state.set_state(AddInfo.category)
    await callback.message.edit_text(cnt[lang].get("ask_info_category"), reply_markup=back_kb(lang, "info_add_cancel"), parse_mode="HTML")


@router.message(AddInfo.category, F.text)
async def process_add_info_cat(message: Message, state: FSMContext, user: User):
    fsm_data = await state.get_data()
    await state.update_data(category=message.text.strip())
    try: await message.delete()
    except: pass
    
    lang = user.language
    await state.set_state(AddInfo.information)
    
    await message.bot.edit_message_text(
        chat_id=message.chat.id, message_id=fsm_data["bot_msg_id"],
        text=cnt[lang].get("ask_info_text"), reply_markup=back_kb(lang, "info_add_cancel"), parse_mode="HTML"
    )


# 🎯 ПЕРЕПИСАНО: Фіналізація, збереження та автоматичне повернення до списку
@router.message(AddInfo.information, F.text)
async def process_add_info_text_finalize(message: Message, state: FSMContext, user: User, session: AsyncSession):
    fsm_data = await state.get_data()
    lang = user.language
    bot_msg_id = fsm_data.get("bot_msg_id")
    
    try: await message.delete()
    except: pass
    
    new_info = GeneralInformation(
        language=fsm_data["chosen_lang"],
        category=fsm_data["category"],     # 🎯 ВИПРАВЛЕНО: беремо збережену категорію
        information=message.text.strip(),
        media_message_id=None  # Медіа-сервер повністю законсервовано
    )
    
    # Захист транзакції бази даних від збоїв послідовностей (sequences)
    try:
        session.add(new_info)
        await session.commit()
    except Exception:
        await session.rollback()
        error_text = "❌ <b>Помилка збереження!</b> Збиті внутрішні SQL-лічильники індексів. Виконайте синхронізацію послідовностей в базі!"
        if lang == "en":
            error_text = "❌ <b>Database error!</b> Duplicate key detected. Please synchronize SQL sequences!"
            
        try:
            await message.bot.edit_message_text(chat_id=message.chat.id, message_id=bot_msg_id, text=error_text, reply_markup=back_kb(lang, "cnt:info:0"), parse_mode="HTML")
        except Exception:
            await message.bot.send_message(chat_id=message.chat.id, text=error_text, reply_markup=back_kb(lang, "cnt:info:0"), parse_mode="HTML")
        await state.clear()
        return

    await state.clear()
    
    # 🌟 UX-ОПТИМІЗАЦІЯ: Генеруємо оновлений список карток одразу на першій сторінці
    page = 0
    total = (await session.execute(select(func.count(GeneralInformation.information_id)))).scalar() or 0
    total_pages = max(1, -(-total // PAGE_SIZE))

    stmt = select(GeneralInformation).order_by(GeneralInformation.category).offset(page * PAGE_SIZE).limit(PAGE_SIZE)
    items = (await session.execute(stmt)).scalars().all()

    text = f"<b>{cnt[lang].get('info_title')}</b>"

    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=bot_msg_id, 
            text=text, 
            reply_markup=info_list_kb(lang, items, page, total_pages), 
            parse_mode="HTML"
        )
    except Exception:
        await message.bot.send_message(
            chat_id=message.chat.id, 
            text=text, 
            reply_markup=info_list_kb(lang, items, page, total_pages), 
            parse_mode="HTML"
        )


@router.callback_query(StateFilter(AddInfo), F.data == "info_add_cancel")
async def cb_cancel_info_addition_chain(callback: CallbackQuery, state: FSMContext, user: User):
    await state.clear()
    await callback.answer(gen[user.language].get("cancelled"))
    await cmd_content_main(callback, user, state)


# ===========================================================================
# ⚙️ ЗАГАЛЬНА ІНФОРМАЦІЯ — РЕДАГУВАННЯ
# ===========================================================================

@router.callback_query(F.data.startswith("info_edit:"))
async def cb_info_edit_menu(callback: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    info_id = int(callback.data.split(":")[1])
    lang = user.language
    
    text = gen[lang].get("choose_action")
    try:
        await callback.message.edit_text(text=text, reply_markup=info_edit_fields_kb(lang, info_id))
    except Exception:
        try: await callback.message.delete()
        except: pass
        await callback.message.answer(text=text, reply_markup=info_edit_fields_kb(lang, info_id))


@router.callback_query(StateFilter(EditInfo), F.data.startswith("info_edit:"))
async def cb_cancel_info_field_edit(callback: CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    await cb_info_edit_menu(callback, user, state)


@router.callback_query(F.data.startswith("info_back_detail:"))
async def cb_info_back_to_detail_view(callback: CallbackQuery, user: User, session: AsyncSession):
    info_id = int(callback.data.split(":")[1])
    callback.data = f"info_detail:{info_id}:0"
    await cb_info_detail(callback, user, session)


@router.callback_query(F.data.startswith("info_field:"))
async def cb_info_field_trigger(callback: CallbackQuery, state: FSMContext, user: User):
    _, info_id, field = callback.data.split(":")
    lang = user.language

    # 🛡️ ПЕРЕПИСАНО: Захист-заглушка на випадок спроби викликати редагування photo
    if field == "media_message_id":
        await callback.answer("📸 Фотографії тимчасово вимкнено!", show_alert=True)
        return

    await state.set_state(EditInfo.enter_value)
    await state.update_data(info_id=int(info_id), field=field, bot_msg_id=callback.message.message_id)

    prompts = {
        "category": cnt[lang].get("ask_info_category"),
        "information": cnt[lang].get("ask_info_text")
    }
    await callback.message.edit_text(text=prompts.get(field, gen[lang].get("choose_action")), reply_markup=back_kb(lang, f"info_edit:{info_id}"))


@router.message(EditInfo.enter_value, F.text)
async def process_info_field_save(message: Message, state: FSMContext, session: AsyncSession, user: User):
    fsm_data = await state.get_data()
    lang = user.language
    field = fsm_data["field"]
    bot_msg_id = fsm_data["bot_msg_id"]
    
    try: await message.delete()
    except: pass

    new_value = message.text.strip() if message.text else ""

    await session.execute(
        update(GeneralInformation)
        .where(GeneralInformation.information_id == fsm_data["info_id"])
        .values({field: new_value})
    )
    await session.commit()
    await state.clear()

    item = (await session.execute(select(GeneralInformation).where(GeneralInformation.information_id == fsm_data["info_id"]))).scalar_one_or_none()
    text = cnt[lang].get("info_detail").format(
        information_id=item.information_id, language=item.language.upper(), category=item.category, information=item.information
    )
    
    try:
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=bot_msg_id, text=text, reply_markup=info_detail_kb(lang, item.information_id, 0))
    except Exception:
        await message.answer(text, reply_markup=info_detail_kb(lang, item.information_id, 0))


@router.callback_query(F.data.startswith("info_delete:"))
async def cb_info_delete(callback: CallbackQuery, user: User, session: AsyncSession):
    info_id = int(callback.data.split(":")[1])
    
    await session.execute(delete(GeneralInformation).where(GeneralInformation.information_id == info_id))
    await session.commit()
    
    await callback.answer(cnt[user.language].get("info_deleted"))
    
    callback.data = "cnt:info:0"
    await cb_info_list(callback, user, session)


# ===========================================================================
# 🛡️ UX ФОЛБЕК — ПЕРЕХОПЛЕННЯ НЕКОРЕКТНОГО КОНТЕНТУ
# ===========================================================================

@router.message(StateFilter(AddFAQ, AddInfo, EditFAQ, EditInfo), ~F.text)
async def cb_wrong_content_type(message: Message, user: User):
    """Спрацює, якщо адмін замість тексту надішле фото, відео, стікер чи файл."""
    try: 
        await message.delete()
    except Exception: 
        pass
    
    lang = user.language
    error_msg = (
        "❌ Будь ласка, надішліть текст. Фотографії та інші файли не підтримуються!" 
        if lang == "ua" 
        else "❌ Please send text only. Photos and other files are not supported!"
    )
    
    alert = await message.answer(error_msg)
    
    await asyncio.sleep(4)
    try:
        await alert.delete()
    except Exception:
        pass