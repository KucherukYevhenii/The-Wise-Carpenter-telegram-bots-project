import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from locales.admin_texts import settings as sett
from bots.admin_bot.states import SettingsAdmin
from bots.admin_bot.keyboards import (
    settings_menu_kb, settings_language_kb, back_kb,
)

router = Router()

# ---------------------------------------------------------------------------
# Допоміжна — показати меню налаштувань
# ---------------------------------------------------------------------------
async def _show_settings(callback: CallbackQuery, user: User, lang: str):
    # 🛡️ ВИПРАВЛЕНО: Захист від Message is not modified
    try:
        await callback.message.edit_text(
            text=sett[lang].get("title").format(
                name        = user.name,
                phone_number= user.phone_number or "—",
            ),
            reply_markup=settings_menu_kb(lang),
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Мова
# ---------------------------------------------------------------------------
@router.callback_query(F.data == "set:language")
async def cb_set_language(callback: CallbackQuery, user: User):
    lang = user.language

    await callback.message.edit_text(
        text=sett[lang].get("language_title"),
        reply_markup=settings_language_kb(lang),
    )

@router.callback_query(F.data.startswith("set_lang:"))
async def cb_change_language(callback: CallbackQuery, user: User, session: AsyncSession):
    new_lang = callback.data.split(":")[1]

    if user.language != new_lang:
        await session.execute(
            update(User)
            .where(User.telegram_id == user.telegram_id)
            .values(language=new_lang)
        )
        await session.commit()
        user.language = new_lang

    await _show_settings(callback, user, new_lang)
    await callback.answer() # Знімаємо "годинник" завантаження з кнопки


# ---------------------------------------------------------------------------
# Зміна імені — FSM
# ---------------------------------------------------------------------------
@router.callback_query(F.data == "set:name")
async def cb_set_name(callback: CallbackQuery, state: FSMContext, user: User):
    lang = user.language

    await state.set_state(SettingsAdmin.enter_name)
    await state.update_data(lang=lang, bot_msg_id=callback.message.message_id)

    await callback.message.edit_text(
        text=sett[lang].get("ask_name"),
        reply_markup=back_kb(lang, "menu:settings"),
    )

@router.message(SettingsAdmin.enter_name, F.text)
async def process_new_name(message: Message, state: FSMContext, user: User, session: AsyncSession):
    fsm = await state.get_data()
    lang = fsm["lang"]

    try:
        await message.delete()
    except Exception:
        pass

    new_name = message.text.strip()
    if len(new_name) > 50 or len(new_name) < 2:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=fsm["bot_msg_id"],
                text=sett[lang].get("name_too_long"),
                reply_markup=back_kb(lang, "menu:settings"),
            )
        except Exception:
            pass
        return

    await session.execute(
        update(User)
        .where(User.telegram_id == user.telegram_id)
        .values(name=new_name)
    )
    await session.commit()
    user.name = new_name

    await state.clear()

    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=fsm["bot_msg_id"],
            text=sett[lang].get("name_changed").format(name=new_name),
            reply_markup=settings_menu_kb(lang),
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Зміна телефону — FSM
# ---------------------------------------------------------------------------
@router.callback_query(F.data == "set:phone")
async def cb_set_phone(callback: CallbackQuery, state: FSMContext, user: User):
    lang = user.language

    await state.set_state(SettingsAdmin.enter_phone)
    await state.update_data(lang=lang, bot_msg_id=callback.message.message_id)

    await callback.message.edit_text(
        text=sett[lang].get("ask_phone"),
        reply_markup=back_kb(lang, "menu:settings"),
    )

@router.message(SettingsAdmin.enter_phone, F.text)
async def process_new_phone(message: Message, state: FSMContext, user: User, session: AsyncSession):
    fsm = await state.get_data()
    lang = fsm["lang"]

    try:
        await message.delete()
    except Exception:
        pass

    new_phone = message.text.strip()
    # Базова захисна перевірка на валідність номеру телефону адміна
    if len(new_phone) < 9 or not new_phone.replace("+", "").isdigit():
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=fsm["bot_msg_id"],
                text=sett[lang].get("ask_phone"), # Повторюємо запит при помилці
                reply_markup=back_kb(lang, "menu:settings"),
            )
        except Exception:
            pass
        return

    await session.execute(
        update(User)
        .where(User.telegram_id == user.telegram_id)
        .values(phone_number=new_phone)
    )
    await session.commit()
    user.phone_number = new_phone

    await state.clear()

    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=fsm["bot_msg_id"],
            text=sett[lang].get("phone_changed").format(phone_number=new_phone),
            reply_markup=settings_menu_kb(lang),
        )
    except Exception:
        pass


# ===========================================================================
# 🛡️ UX ФОЛБЕК — ПЕРЕХОПЛЕННЯ НЕКОРЕКТНОГО КОНТЕНТУ
# ===========================================================================

@router.message(StateFilter(SettingsAdmin), ~F.text)
async def cb_wrong_settings_input(message: Message, user: User):
    """Спрацює, якщо адмін під час зміни імені чи телефону надішле не текст."""
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