from aiogram import Router, F
from aiogram.filters import Command
from states import EventStates
from repositoreies import EventRepository, EventParticipantsRepository
from filters import RoleFilter
from models import Event
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time_picker import get_time_keyboard
from handlers.menu import main_menu_message
from keyboards import get_edit_event_keyboard
from responses import get_event_response

router = Router(name=__name__)


@router.message(Command("event_create"), RoleFilter(["admin", "organizator"]))
async def create_event_handler(message, state):
    await state.set_state(EventStates.set_name)
    await message.answer("Введи название мероприятия")


@router.message(Command("cancel"))
async def cancel_operation(message, state):
    await state.clear()
    await main_menu_message(message)


@router.message(EventStates.set_name, RoleFilter(["admin", "organizator"]))
async def set_event_name_handler(message, state):
    event = Event(name=message.text)
    await state.set_state(EventStates.set_description)
    await state.update_data(event=event)
    await message.answer("Введи описание мероприятия")


@router.message(EventStates.set_description, RoleFilter(["admin", "organizator"]))
async def set_event_desription_handler(message, state):
    event = (await state.get_data()).get("event")
    event.description = message.text
    await state.set_state(EventStates.set_map)
    await state.update_data(event=event)
    await message.answer("Отправь картинку карты/схемы мероприятия")


@router.message(EventStates.set_map, RoleFilter(["admin", "organizator"]))
async def set_event_map_handler(message, state):
    event = (await state.get_data()).get("event")
    event.map = message.photo[-1].file_id
    await state.set_state(EventStates.set_schedule)
    await state.update_data(event=event, is_master_class=True)
    await message.answer("Отправь расписание мероприятия")


@router.message(EventStates.set_schedule, RoleFilter(["admin", "organizator"]))
async def set_event_schedule_handler(message, state):
    event = (await state.get_data()).get("event")
    event.schedule = message.text
    await state.set_state(EventStates.set_start_date)
    await state.update_data(event=event)
    await message.answer(
        "Выбери дату начала:",
        reply_markup=await SimpleCalendar().start_calendar()
    )


@router.callback_query(SimpleCalendarCallback.filter(), EventStates.set_start_date)
async def process_simple_calendar(callback_query, callback_data, state):
    calendar = SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(
        datetime.now() - relativedelta(days=1), datetime.now() + relativedelta(years=5))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.set_state(EventStates.set_start_time)
        await state.update_data(start_date=date)
        await callback_query.message.answer(
            "Выберите время начала:",
            reply_markup=get_time_keyboard(0)
        )


@router.callback_query(F.data.startswith("select_time-"), EventStates.set_start_time)
async def process_start_time(callback, state):
    time_str = callback.data.split("-")[1]
    selected_time = datetime.strptime(time_str, "%H:%M").time()

    data = await state.get_data()
    start_date = data.get("start_date")
    start_datetime = datetime.combine(start_date, selected_time)

    await state.set_state(EventStates.set_end_date)
    await state.update_data(start_datetime=start_datetime)

    await callback.message.answer("Теперь выберите дату окончания:", reply_markup=await SimpleCalendar().start_calendar())


@router.callback_query(SimpleCalendarCallback.filter(), EventStates.set_end_date)
async def process_end_date(callback_query, callback_data, state):
    calendar = SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(
        datetime.now() - relativedelta(days=1), datetime.now() + relativedelta(years=5))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(end_date=date)
        await state.set_state(EventStates.set_end_time)
        await callback_query.message.answer(
            "Выберите время окончания:",
            reply_markup=get_time_keyboard(0)
        )


@router.callback_query(F.data.startswith("select_time-"), EventStates.set_end_time)
async def process_end_time(callback, state):
    time_str = callback.data.split("-")[1]
    selected_time = datetime.strptime(time_str, "%H:%M").time()

    data = await state.get_data()
    end_date = data.get("end_date")
    end_datetime = datetime.combine(end_date, selected_time)

    start_datetime = data["start_datetime"]

    event = data.get("event")
    event.start_time = start_datetime
    event.end_time = end_datetime

    if data.get("is_master_class"):
        pass
    else:
        EventRepository.create(event)

    await callback.message.answer("Событие создано")

    await state.clear()


@router.callback_query(F.data.startswith("time_page:"))
async def change_time_page(callback):
    page = callback.data.split(":")[1]
    await callback.message.edit_reply_markup(reply_markup=get_time_keyboard(int(page)))


@router.callback_query(F.data.startswith("events_all"))
async def get_events(callback_query, state):
    result = "Актуальные мероприятия:\n\n"
    for event in EventRepository.getActual():
        result += f"🎯 {event.id}. {event.name}\n\n"

    result += "Напишите номер мероприятия, которое хотите посмотреть поподробнее"

    await state.set_state(EventStates.choosing)
    await callback_query.message.answer(result)


@router.message(EventStates.choosing)
async def get_concrete_event(message, state):
    event = EventRepository.getById(message.text)
    role_id = (await state.get_data()).get("user").role_id
    if not event:
        await message.answer("Такого мероприятия не найдено")
    else:
        await get_event_response(message, event, role_id)
        await state.clear()


@router.callback_query(F.data.startswith("event_check_in"))
async def event_check_in(callback_query, state):
    event_id = callback_query.data.split(" ")[1]
    user_id = (await state.get_data()).get("user").id
    eventParticipants = EventParticipantsRepository.getByEventIdAndUserId(
        event_id, user_id)

    if not eventParticipants:
        EventParticipantsRepository.create(event_id, user_id)
        await callback_query.message.answer("Вы записаны")
        await main_menu_message(callback_query.message)
    else:
        await callback_query.message.answer("Вы уже записаны")
        await main_menu_message(callback_query.message)


@router.callback_query(F.data.startswith("event_check_out"))
async def event_check_out(callback_query, state):
    event_id = callback_query.data.split(" ")[1]
    user_id = (await state.get_data()).get("user").id
    eventParticipants = EventParticipantsRepository.getByEventIdAndUserId(
        event_id, user_id)

    if not eventParticipants:
        await callback_query.message.answer("Вы не записаны")
    else:
        EventParticipantsRepository.delete(eventParticipants)
        await callback_query.message.answer("Теперь вы не записаны")
        await main_menu_message(callback_query.message)


@router.callback_query(F.data.startswith("event_edit_field"), RoleFilter(["admin", "organizator"]))
async def event_edit(callback_query, state):
    event_id = callback_query.data.split(" ")[1]
    await state.set_state(EventStates.edit)
    await state.update_data(event_id=event_id)
    await callback_query.message.answer(
        "Выберите, какое поле вы хотите редактировать: ",
        reply_markup=get_edit_event_keyboard()
    )


@router.callback_query(EventStates.edit, RoleFilter(["admin", "organizator"]))
async def event_edit_choose_field(callback_query, state):
    field_name = callback_query.data.split(".")[1]
    await state.set_state(EventStates.edit_getting_value)
    await state.update_data(field_name=field_name)

    if field_name == "start_time" or field_name == "end_time":
        await state.set_state(EventStates.edit_getting_time)
        await callback_query.message.answer(
            "Выберите новую дату:",
            reply_markup=await SimpleCalendar().start_calendar()
        )
    else:
        await callback_query.message.answer("Введите новое значение")


@router.message(EventStates.edit_getting_value, RoleFilter(["admin", "organizator"]))
async def event_edit_field(message, state):
    field_name = (await state.get_data()).get("field_name")
    event_id = (await state.get_data()).get("event_id")
    if field_name == "map":
        event = EventRepository.update(
            event_id, field_name, message.photo[-1].file_id)
    else:
        event = EventRepository.update(event_id, field_name, message.text)
    role_id = (await state.get_data()).get("user").role_id

    await message.answer("Значение изменено")
    await get_event_response(message, event, role_id)


@router.callback_query(SimpleCalendarCallback.filter(), EventStates.edit_getting_time, RoleFilter(["admin", "organizator"]))
async def edit_event_time(callback_query, callback_data, state):
    calendar = SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(
        datetime.now() - relativedelta(days=1), datetime.now() + relativedelta(years=5))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(new_date=date)
        await callback_query.message.answer(
            "Выберите новое время:",
            reply_markup=get_time_keyboard(0)
        )


@router.callback_query(F.data.startswith("select_time-"), EventStates.edit_getting_time)
async def process_end_time(callback, state):
    time_str = callback.data.split("-")[1]
    selected_time = datetime.strptime(time_str, "%H:%M").time()

    data = await state.get_data()
    date = data.get("new_date")
    date = datetime.combine(date, selected_time)

    field_name = data.get("field_name")
    event_id = data.get("event_id")
    event = EventRepository.update(event_id, field_name, date)
    role_id = (await state.get_data()).get("user").role_id
    await get_event_response(callback.message, event, role_id)

    await state.clear()
