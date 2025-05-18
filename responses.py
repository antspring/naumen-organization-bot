from keyboards import get_concrete_event_keyboard, get_concrete_masterclass_keyboard


async def get_event_response(message, event, role_id):
    await message.answer_photo(
        photo=event.map,
        caption=f'''🎯 {event.name}\n
{event.description}\n
{event.schedule}\n
Время начала: {event.start_time}
Время конца: {event.end_time}\n''',
        reply_markup=get_concrete_event_keyboard(role_id, event.id)
    )


async def get_masterclass_response(message, master_class, role_id):
    result = f"🎯 {master_class.name}\n\n"
    result += f"Описание: {master_class.description}\n\n"
    result += f"Вместимость: {master_class.capacity}\n\n"
    result += f"Дата начала: {master_class.start_time.strftime('%d.%m.%Y %H:%M')}\n\n"
    result += f"Дата окончания: {master_class.end_time.strftime('%d.%m.%Y %H:%M')}\n\n"

    await message.answer(result, reply_markup=get_concrete_masterclass_keyboard(master_class.id, role_id))
