from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from database.models import User  
from bots.user_bot.states import Registration
from bots.user_bot.keyboards import lang_kb, get_phone_number_kb_reg
from locales.texts import registration_phrases as reg_txt

router = Router()

# --- Блок Реєстрація ---

# --- Етап 1: Запуск start та обрання мови ---
@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):
    # Перевіряємо, чи є користувач у базі
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    if user:
        # Виправлено лапки з подвійних на одинарні 'start_again'
        await message.answer(f"{reg_txt[user.language].get('start_again')}, {user.name}!")
        return
    
    await message.answer(reg_txt["start"], reply_markup=lang_kb)
    await state.set_state(Registration.choosing_language)

# --- Етап 2: Введення імені ---
@router.callback_query(Registration.choosing_language)
async def language_chosen(callback: types.CallbackQuery, state: FSMContext):
    # Очищуємо callback_data від префіксів (наприклад, якщо там lang:ua чи set_lang:ua)
    lang_code = callback.data.split(":")[-1] if ":" in callback.data else callback.data
    
    # Фолбек на випадок, якщо прилетіло непередбачуване значення
    if lang_code not in ["ua", "en"]:
        lang_code = "ua"
        
    await state.update_data(chosen_lang=lang_code)

    await callback.message.edit_text(reg_txt[lang_code]["name_set"])
    await state.set_state(Registration.entering_name)
    await callback.answer()

# --- Етап 3: Введення телефону ---
@router.message(Registration.entering_name)
async def name_entered(message: types.Message, state: FSMContext):
    user_name = message.text.strip() if message.text else "Користувач"
    await state.update_data(user_name=user_name)

    data = await state.get_data()
    lang = data.get("chosen_lang", "ua")

    await message.answer(
        reg_txt[lang]["phone_set"], 
        reply_markup=get_phone_number_kb_reg(lang)
    )
    await state.set_state(Registration.entering_phone)

# --- Етап 4: Реєстрація користувача ---
# Змінили фільтр: тепер приймаємо і кнопку контакту, і звичайне текстове повідомлення
@router.message(Registration.entering_phone, F.contact | F.text)
async def phone_entered(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    lang = data.get("chosen_lang", "ua")
    
    # Визначаємо номер телефону залежно від того, як його надіслали
    if message.contact:
        phone = message.contact.phone_number
    else:
        # Якщо юзер ввів текст — чистимо його від пробілів
        phone = message.text.strip()
        # Базова валідація (можна розширити за потреби)
        if not phone.replace("+", "").isdigit() or len(phone) < 9:
            await message.answer(reg_txt[lang].get("phone_error", "Некоректний формат. Спробуйте ще раз або натисніть кнопку:"))
            return

    new_user = User(
        telegram_id=message.from_user.id,
        name=data['user_name'],
        phone_number=phone,
        language=lang,
        is_admin=False
    )

    session.add(new_user)
    await session.commit()
    
    await state.clear()

    # Прибираємо reply-кнопку відправки контакту за допомогою ReplyKeyboardRemove
    await message.answer(
        reg_txt[lang].get("registrated_successfully"), 
        reply_markup=types.ReplyKeyboardRemove()
    )