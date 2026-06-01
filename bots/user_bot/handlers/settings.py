from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from bots.user_bot.states import SettingsStates
from bots.user_bot.keyboards import get_settings_kb, get_lang_settings_kb, get_phone_number_kb, get_name_change_kb

from locales.texts import settings_phrases as sett

from typing import Union

router = Router()

async def get_lang(user_id: int, session: AsyncSession):
    res = await session.execute(select(User.language).where(User.telegram_id == user_id))
    return res.scalar() or "ua"

async def show_settings_menu(event: Union[types.Message, types.CallbackQuery], session: AsyncSession, force_new: bool = False):
    user_id = event.from_user.id
    res = await session.execute(select(User.language).where(User.telegram_id == user_id))
    user_lang = res.scalar() or "en"
    
    text = f"<b>{sett[user_lang].get('settings_label')}</b>"
    kb = get_settings_kb(user_lang)

    if isinstance(event, types.Message) or force_new:
        if isinstance(event, types.CallbackQuery):
            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
        else:
            await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        # Редагуємо існуюче
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            # Якщо повідомлення не знайдено (видалене) — шлемо нове
            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(Command("settings"))
async def cmd_settings(message: types.Message, session: AsyncSession):
    await show_settings_menu(message, session)

@router.callback_query(F.data == "settings_back")
async def settings_back_handler(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    msg_ids = data.get("messages_to_delete", [])
    
    # 1. Видаляємо повідомлення-інструкції
    for msg_id in msg_ids:
        try:
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
        except Exception: pass

    # 2. Видаляємо поточне повідомлення з кнопкою "Назад"
    try:
        await callback.message.delete()
    except Exception: pass

    # 3. Скидаємо стан
    await state.clear()
    
    # 4. Надсилаємо ОДНЕ повідомлення, яке прибере Reply-клавіатуру
    temp_msg = await callback.message.answer(
        ".", 
        reply_markup=ReplyKeyboardRemove()
    )
    try:
        await temp_msg.delete()
    except Exception: 
        pass
    
    # 5. Викликаємо меню примусово новим повідомленням (force_new=True)
    await show_settings_menu(callback, session, force_new=True)


# --- Зміна мови ---
@router.callback_query(F.data == "set_lang_menu")
async def set_lang_menu(callback: types.CallbackQuery, session: AsyncSession ):
    user_lang = await get_lang(callback.from_user.id, session)
    text = sett[user_lang].get("language_choose")

    await callback.message.edit_text(f"{text}", reply_markup=get_lang_settings_kb(user_lang))
    await callback.answer()

@router.callback_query(F.data.startswith("set_lang:"))
async def change_language(callback: types.CallbackQuery, session: AsyncSession):
    new_lang = callback.data.split(":")[1]
    
    await session.execute(
        update(User).where(User.telegram_id == callback.from_user.id).values(language=new_lang)
    )
    await session.commit()
    
    text = sett[new_lang].get("language_changed")
    await callback.message.answer(text)

    try:
        await callback.message.delete()
    except Exception:
        pass

    # Передаємо параметр force_new=True, тому що старе меню ми щойно видалили рядком вище!
    await show_settings_menu(callback, session, force_new=True)

# --- Зміна імені (FSM) ---
@router.callback_query(F.data == "set_name_start")
async def change_name_start(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    lang = await get_lang(callback.from_user.id, session)

    # Видаляємо головне меню, щоб звільнити місце
    await callback.message.delete()

    text1 = sett[lang].get("name_enter")
    text2 = sett[lang].get("cancel_instruction")
    sent_msg1 = await callback.message.answer(text1)
    sent_msg2 = await callback.message.answer(text2, reply_markup=get_name_change_kb(lang))

    await state.update_data(messages_to_delete=[sent_msg1.message_id, sent_msg2.message_id])
    await state.set_state(SettingsStates.waiting_for_new_name)
    await callback.answer()

@router.message(SettingsStates.waiting_for_new_name, F.text)
async def process_new_name(message: types.Message, state: FSMContext, session: AsyncSession):
    new_name = message.text.strip()
    lang = await get_lang(message.from_user.id, session=session)
    
    # Проста валідація
    if len(new_name) > 50:
        await message.answer(sett[lang].get("name_long"))
        return
    
    data = await state.get_data()
    for msg_id in data.get("messages_to_delete", []):
        try: await message.bot.delete_message(message.chat.id, msg_id)
        except: pass
    
    try: await message.delete()  # Очищаємо текстове повідомлення користувача
    except Exception: pass

    await session.execute(
        update(User).where(User.telegram_id == message.from_user.id).values(name=new_name)
    )
    await session.commit()
    
    # Виправлено внутрішні подвійні лапки на одинарні 'name_changed'
    success = f"{sett[lang].get('name_changed')}, {new_name}!"
    await message.answer(success)
    await state.clear()
    await show_settings_menu(message, session)

# Запуск процесу зміни телефону
@router.callback_query(F.data == "set_phone_start")
async def change_phone_start(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    lang = await get_lang(callback.from_user.id, session)
    
    await callback.message.delete()

    text = sett[lang].get("phone_share")

    reply_kb, inline_kb = get_phone_number_kb(lang)
    
    msg1 = await callback.message.answer(text, reply_markup=reply_kb)
    msg2 = await callback.message.answer(sett[lang].get('cancel_instruction'), 
                                 reply_markup=inline_kb)
    
    await state.update_data(messages_to_delete=[msg1.message_id, msg2.message_id])
    await state.set_state(SettingsStates.waiting_for_new_phone)
    await callback.answer()

# Обробка номера (Захистили фільтром контакту та тексту)
@router.message(SettingsStates.waiting_for_new_phone, F.text | F.contact)
async def process_new_phone(message: types.Message, state: FSMContext, session: AsyncSession):
    lang = await get_lang(message.from_user.id, session)
    
    if message.contact:
        new_phone = message.contact.phone_number
    else:
        new_phone = message.text.strip()
        # Базова перевірка валідності вводу вручну
        if not new_phone.replace("+", "").isdigit() or len(new_phone) < 9:
            await message.answer(sett[lang].get("phone_error", "Некоректний формат. Спробуйте ще раз:"))
            return
    
    data = await state.get_data()
    for msg_id in data.get("messages_to_delete", []):
        try: await message.bot.delete_message(message.chat.id, msg_id)
        except: pass
        
    try: await message.delete()  # Очищаємо чат від повідомлення користувача
    except Exception: pass

    await session.execute(
        update(User).where(User.telegram_id == message.from_user.id).values(phone_number=new_phone)
    )
    await session.commit()
    
    success = f"{sett[lang].get('phone_changed')} {new_phone}!"
    
    await message.answer(success, reply_markup=ReplyKeyboardRemove()) 
    await state.clear()
    
    await show_settings_menu(message, session)