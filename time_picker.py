from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

time_options = [
    "10:00", "10:30", "11:00",
    "11:30", "12:00", "12:30",
    "13:00", "13:30", "14:00",
    "14:30", "15:00", "15:30",
    "16:00", "16:30", "17:00",
    "17:30", "18:00", "18:30",
    "19:00", "19:30", "20:00",
    "20:30", "21:00"
]

ITEMS_PER_PAGE = 3

def get_time_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    current_items = time_options[start:end]

    buttons = [
        [InlineKeyboardButton(text=t, callback_data=f"select_time-{t}")]
        for t in current_items
    ]

    navigation = []

    if page > 0:
        navigation.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"time_page:{page - 1}"))

    if end < len(time_options):
        navigation.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"time_page:{page + 1}"))

    if navigation:
        buttons.append(navigation)

    return InlineKeyboardMarkup(inline_keyboard=buttons)