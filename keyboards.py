from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models import Role


def get_concrete_event_keyboard(role_id):
    buttons = [
        [InlineKeyboardButton(text="✅ Записаться", callback_data="event_check_in")]
    ]

    if role_id == Role.ORGANIZATOR or role_id == Role.ADMIN:
        buttons.append([InlineKeyboardButton(text="✏️ Редактировать", callback_data="event_edit")])
    
    if role_id == Role.ADMIN:
        buttons.append([InlineKeyboardButton(text="❌ Удалить", callback_data="event_delete")])
    
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)