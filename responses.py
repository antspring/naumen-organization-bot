from keyboards import get_concrete_event_keyboard

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