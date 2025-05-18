from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models import Role


def get_concrete_event_keyboard(role_id, event_id):
    buttons = [
        [InlineKeyboardButton(text="✅ Записаться", callback_data=f"event_check_in {event_id}")],
        [InlineKeyboardButton(text="↪️ Не пойду", callback_data=f"event_check_out {event_id}")],
        [InlineKeyboardButton(text="📝 Список мастер-классов", callback_data=f"masterclass_list {event_id}")],
    ]

    if role_id == Role.ORGANIZATOR or role_id == Role.ADMIN:
        buttons.append([InlineKeyboardButton(text="👷 Добавить мастер-класс", callback_data=f"masterclass_create {event_id}")])
        buttons.append([InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"event_edit_field {event_id}")])
    
    if role_id == Role.ADMIN:
        buttons.append([InlineKeyboardButton(text="❌ Удалить", callback_data=f"event_delete {event_id}")])
    
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_edit_event_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Название", callback_data=f"event_edit.name")],
        [InlineKeyboardButton(text="Описание", callback_data=f"event_edit.description")],
        [InlineKeyboardButton(text="Карта/схема", callback_data=f"event_edit.map")],
        [InlineKeyboardButton(text="Расписание", callback_data=f"event_edit.schedule")],
        [InlineKeyboardButton(text="Время начала", callback_data=f"event_edit.start_time")],
        [InlineKeyboardButton(text="Время конца", callback_data=f"event_edit.end_time")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_concrete_masterclass_keyboard(master_class_id, role_id):
    buttons = [
        [InlineKeyboardButton(text="✅ Записаться", callback_data=f"masterclass_check_in {master_class_id}")],
        [InlineKeyboardButton(text="↪️ Не пойду", callback_data=f"masterclass_check_out {master_class_id}")],
    ]

    if role_id == Role.ORGANIZATOR or role_id == Role.ADMIN:
        buttons.append([InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"masterclass_edit_field {master_class_id}")])
    
    if role_id == Role.ADMIN:
        buttons.append([InlineKeyboardButton(text="❌ Удалить", callback_data=f"masterclass_delete {master_class_id}")])
    
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)