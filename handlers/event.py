from aiogram import Router, F
from aiogram.filters import Command
from states import EventStates
from repositoreies import EventRepository
from filters import RoleFilter
from models import Event
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time_picker import get_time_keyboard
from handlers.menu import main_menu_message

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
    calendar.set_dates_range(datetime.now() - relativedelta(days=1), datetime.now() + relativedelta(years=5))
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
    calendar.set_dates_range(datetime.now() - relativedelta(days=1), datetime.now() + relativedelta(years=5))
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
async def get_events(callback_query):
    result = "Актуальные мероприятия:\n\n"
    for event in EventRepository.getActual():
        result += f"🎯 {event.id}. {event.name}\n\n"
    
    result += "Напишите номер мероприятия, которое хотите посмотреть поподробнее"
    await callback_query.message.answer(result)