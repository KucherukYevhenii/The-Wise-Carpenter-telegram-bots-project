import html
from typing import Union

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from bots.user_bot.keyboards import main_menu_kb
from locales.texts import main_menu_phrases as mm

router = Router()


async def send_main_menu(event: Union[types.Message, types.CallbackQuery], lang: str, name: str):
    """Показує головне меню: редагує повідомлення (для кнопок) або надсилає нове (для команд)."""
    text = mm[lang]["welcome"].format(name=html.escape(name or ""))
    kb = main_menu_kb(lang)

    if isinstance(event, types.CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            # повідомлення могло бути видалене або містити фото — шлемо нове
            try:
                await event.message.delete()
            except Exception:
                pass
            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
        try:
            await event.answer()
        except Exception:
            pass
    else:
        await event.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(Command("menu"))
@router.callback_query(F.data == "main_menu")
async def cmd_main_menu(event: Union[types.Message, types.CallbackQuery], state: FSMContext, session: AsyncSession):
    await state.clear()  # скидаємо будь-які завислі стани

    res = await session.execute(select(User).where(User.telegram_id == event.from_user.id))
    user = res.scalar_one_or_none()

    if user is None:
        text = f"{mm['ua']['not_registered']}\n{mm['en']['not_registered']}"
        if isinstance(event, types.CallbackQuery):
            await event.answer(text, show_alert=True)
        else:
            await event.answer(text)
        return

    await send_main_menu(event, user.language, user.name)