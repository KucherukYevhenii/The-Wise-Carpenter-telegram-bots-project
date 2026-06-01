from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from typing import Union

# Імпортуємо модель User, щоб працювала типізація
from database.models import User, AdminPrivilege 
from locales.admin_texts import menu as mn, requests as req, workshops as ws, \
    support as sup, content as cnt, stats as sts, admins as adm, settings as sett
from bots.admin_bot.keyboards import (
    main_menu_kb, requests_menu_kb, workshops_menu_kb,
    support_menu_kb, content_menu_kb, stats_kb, admins_menu_kb,
    settings_menu_kb
)

router = Router()

# ---------------------------------------------------------------------------
# Допоміжна функція для безпечного перемикання меню (захист від крашів)
# ---------------------------------------------------------------------------
async def _safe_menu_switch(event: Union[Message, CallbackQuery], text: str, reply_markup):
    """Безпечно відправляє або редагує повідомлення, обробляючи переходи від фото до тексту."""
    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text=text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception:
            try:
                await event.message.delete()
            except Exception:
                pass
            await event.message.answer(text=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await event.answer(text=text, reply_markup=reply_markup, parse_mode="HTML")


# ---------------------------------------------------------------------------
# /start та Головне меню
# ---------------------------------------------------------------------------

@router.message(CommandStart())
@router.callback_query(F.data == "menu:main")
async def cmd_start_and_main(event: Union[Message, CallbackQuery], state: FSMContext, user: User):
    await state.clear()  # 🎯 Очищаємо будь-які завислі стани

    lang = user.language  
    is_superadmin = user.admin_privilege == AdminPrivilege.SUPERADMIN

    text = mn[lang].get("welcome").format(name=user.name)
    reply_markup = main_menu_kb(lang, is_superadmin=is_superadmin)

    await _safe_menu_switch(event, text, reply_markup)


# ---------------------------------------------------------------------------
# Навігація з головного меню
# ---------------------------------------------------------------------------

@router.message(Command("requests"))
@router.callback_query(F.data == "menu:requests")
async def cb_menu_requests(event: Union[Message, CallbackQuery], state: FSMContext, user: User):
    await state.clear()
    lang = user.language  
    text = req[lang].get("title")
    reply_markup = requests_menu_kb(lang)

    await _safe_menu_switch(event, text, reply_markup)


@router.message(Command("workshops"))
@router.callback_query(F.data == "menu:workshops")
async def cb_menu_workshops(event: Union[Message, CallbackQuery], state: FSMContext, user: User):
    await state.clear()
    lang = user.language  
    text = ws[lang].get("title")
    reply_markup = workshops_menu_kb(lang)

    await _safe_menu_switch(event, text, reply_markup)


@router.message(Command("support"))
@router.callback_query(F.data == "menu:support")
async def cb_menu_support(event: Union[Message, CallbackQuery], state: FSMContext, user: User):
    await state.clear()
    lang = user.language  
    text = sup[lang].get("title")
    reply_markup = support_menu_kb(lang)

    await _safe_menu_switch(event, text, reply_markup)


@router.message(Command("content"))
@router.callback_query(F.data == "menu:content")
async def cb_menu_content(event: Union[Message, CallbackQuery], state: FSMContext, user: User):
    await state.clear()
    lang = user.language  
    text = cnt[lang].get("title")
    reply_markup = content_menu_kb(lang)

    await _safe_menu_switch(event, text, reply_markup)


@router.message(Command("stats"))
@router.callback_query(F.data == "menu:stats")
async def cb_menu_stats(event: Union[Message, CallbackQuery], state: FSMContext, user: User):
    await state.clear()
    lang = user.language  
    text = sts[lang].get("title").format(
        total_users="...", new_users_week="...",
        opening_new="...", opening_in_progress="...", opening_completed="...",
        mobile_new="...", mobile_in_progress="...", mobile_completed="...",
        active_workshops="...", support_new="...",
    )
    reply_markup = stats_kb(lang)

    await _safe_menu_switch(event, text, reply_markup)


@router.message(Command("admins"))
@router.callback_query(F.data == "menu:admins")
async def cb_menu_admins(event: Union[Message, CallbackQuery], state: FSMContext, user: User):
    await state.clear()
    lang = user.language  
    
    if user.admin_privilege != AdminPrivilege.SUPERADMIN:
        if isinstance(event, CallbackQuery):
            await event.answer(adm[lang].get("superadmin_only"), show_alert=True)
        else:
            await event.answer(adm[lang].get("superadmin_only"))
        return

    text = adm[lang].get("title")
    reply_markup = admins_menu_kb(lang)

    await _safe_menu_switch(event, text, reply_markup)


@router.message(Command("settings"))
@router.callback_query(F.data == "menu:settings")
async def cb_menu_settings_redirect(event: Union[Message, CallbackQuery], state: FSMContext, user: User):
    await state.clear()
    lang = user.language

    text = sett[lang].get("title").format(
        name=user.name,
        phone_number=user.phone_number or "—",
    )
    reply_markup = settings_menu_kb(lang)

    await _safe_menu_switch(event, text, reply_markup)