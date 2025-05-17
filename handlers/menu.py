from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router
from aiogram.filters import Command

router = Router(name=__name__)

async def main_menu_message(message):
    text = "🏠 Вы в главном меню.\n\nВыберите действие:"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Все мероприятия", callback_data="events_all"),
        InlineKeyboardButton(text="📖 Мои мероприятия", callback_data="events_my")]
    ])

    await message.answer(text, reply_markup=kb)


@router.message(Command("menu"))
async def return_to_main_menu(message):
    await main_menu_message(message)