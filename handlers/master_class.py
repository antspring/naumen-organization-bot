from aiogram import Router, F
from states import MasterClassStates
from models import MasterClass
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time_picker import get_time_keyboard
from repositoreies import MasterClassRepository, EventRepository
from responses import get_event_response, get_masterclass_response

router = Router(name=__name__)


@router.callback_query(F.data.startswith("masterclass_create"))
async def create_master_class(callback_query, state):
    event_id = callback_query.data.split(" ")[1]
    masterclass = MasterClass(event_id=event_id)
    await state.update_data(masterclass=masterclass, role_id=(await state.get_data()).get("user").role_id)
    await state.set_state(MasterClassStates.set_name)
    await callback_query.message.answer("Введите название мастер-класса")


@router.message(MasterClassStates.set_name)
async def set_name(message, state):
    name = message.text
    masterclass = (await state.get_data()).get("masterclass")
    masterclass.name = name
    await state.update_data(masterclass=masterclass)
    await state.set_state(MasterClassStates.set_description)
    await message.answer("Введите описание мастер-класса")


@router.message(MasterClassStates.set_description)
async def set_description(message, state):
    description = message.text
    masterclass = (await state.get_data()).get("masterclass")
    masterclass.description = description
    await state.update_data(masterclass=masterclass)
    await state.set_state(MasterClassStates.set_capacity)
    await message.answer("Введите вместимость мастер-класса")


@router.message(MasterClassStates.set_capacity)
async def set_capacity(message, state):
    capacity = message.text
    masterclass = (await state.get_data()).get("masterclass")
    masterclass.capacity = int(capacity)
    await state.update_data(masterclass=masterclass)
    await state.set_state(MasterClassStates.set_start_date)
    await message.answer(
        "Введите дату начала мастер-класса",
        reply_markup=await SimpleCalendar().start_calendar())


@router.callback_query(MasterClassStates.set_start_date, SimpleCalendarCallback.filter())
async def set_start_date(callback_query, state, callback_data):
    calendar = SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(
        datetime.now() - relativedelta(days=1), datetime.now() + relativedelta(years=5))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        start_date = date
        await state.update_data(start_date=start_date)
        await state.set_state(MasterClassStates.set_start_time)
        await callback_query.message.answer(
            "Введите время начала мастер-класса",
            reply_markup=get_time_keyboard(0)
        )


@router.callback_query(F.data.startswith("select_time-"), MasterClassStates.set_start_time)
async def set_start_time(callback_query, state):
    start_time = callback_query.data.split("-")[1]
    start_date = (await state.get_data()).get("start_date")
    start_datetime = datetime.combine(
        start_date, datetime.strptime(start_time, "%H:%M").time())
    masterclass = (await state.get_data()).get("masterclass")
    masterclass.start_time = start_datetime
    await state.update_data(masterclass=masterclass)
    await state.set_state(MasterClassStates.set_end_date)
    await callback_query.message.answer(
        "Введите дату окончания мастер-класса",
        reply_markup=await SimpleCalendar().start_calendar()
    )


@router.callback_query(MasterClassStates.set_end_date, SimpleCalendarCallback.filter())
async def set_end_date(callback_query, state, callback_data):
    calendar = SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(
        datetime.now() - relativedelta(days=1), datetime.now() + relativedelta(years=5))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        end_date = date
        await state.update_data(end_date=end_date)
        await state.set_state(MasterClassStates.set_end_time)
        await callback_query.message.answer(
            "Введите время окончания мастер-класса",
            reply_markup=get_time_keyboard(0)
        )


@router.callback_query(F.data.startswith("select_time-"), MasterClassStates.set_end_time)
async def set_end_time(callback_query, state):
    end_time = callback_query.data.split("-")[1]
    data = await state.get_data()
    end_date = data.get("end_date")
    end_datetime = datetime.combine(
        end_date, datetime.strptime(end_time, "%H:%M").time())
    masterclass = data.get("masterclass")
    masterclass.end_time = end_datetime
    MasterClassRepository.create(masterclass)
    await state.clear()
    await callback_query.message.answer("Мастер-класс успешно создан!")
    await get_event_response(callback_query.message,
                             EventRepository.getById(masterclass.event_id),
                             data.get("role_id"))


@router.callback_query(F.data.startswith("masterclass_list"))
async def masterclass_list(callback_query, state):
    event_id = callback_query.data.split(" ")[1]
    masterclasses = MasterClassRepository.getByEventId(event_id)
    if not masterclasses:
        await callback_query.message.answer("Мастер-классов нет")
        await get_event_response(callback_query.message,
                                 EventRepository.getById(event_id),
                                 (await state.get_data()).get("user").role_id)
        return

    result = "Список мастер-классов:\n\n"
    for masterclass in masterclasses:
        result += f"🎯 {masterclass.id}. {masterclass.name}\n"

    result += "\nНапиши номер мастер-класса, чтобы получить подробную информацию"

    await state.set_state(MasterClassStates.choosing)

    await callback_query.message.answer(result)


@router.message(MasterClassStates.choosing)
async def masterclass_concrete(message, state):
    master_class = MasterClassRepository.getById(message.text)
    if not master_class:
        await message.answer("Мастер-класса с таким номером нет")
        await masterclass_list(message, state)
    else:
        await get_masterclass_response(message, master_class, (await state.get_data()).get("user").role_id)
        await state.clear()


@router.callback_query(F.data.startswith("masterclass_delete"))
async def masterclass_delete(callback_query):
    master_class_id = callback_query.data.split(" ")[1]
    try:
        MasterClassRepository.delete(master_class_id)
        await callback_query.message.answer("Мастер-класс удален")
    except:
        await callback_query.message.answer("Такого мастер-класса нет")


@router.callback_query(F.data.startswith("masterclass_check_in"))
async def masterclass_check_in(callback_query, state):
    master_class_id = callback_query.data.split(" ")[1]
    user = (await state.get_data()).get("user")
    try:
        if MasterClassRepository.checkIn(master_class_id, user.id):
            await callback_query.message.answer("Вы записаны на мастер-класс")
        else:
            await callback_query.message.answer("На мастер-классе нет мест")
    except:
        await callback_query.message.answer("Вы уже записаны на мастер-класс или такого мастер-класса нет")


@router.callback_query(F.data.startswith("masterclass_check_out"))
async def masterclass_check_out(callback_query, state):
    master_class_id = callback_query.data.split(" ")[1]
    user = (await state.get_data()).get("user")
    try:
        MasterClassRepository.checkOut(master_class_id, user.id)
        await callback_query.message.answer("Вы вышли из мастер-класса")
    except:
        await callback_query.message.answer("Вы не записаны на мастер-класс или такого мастер-класса нет")


@router.callback_query(F.data.startswith("masterclasses_my_list"))
async def masterclass_list_my(callback_query, state):
    user_id = (await state.get_data()).get("user").id
    groupd_items = MasterClassRepository.getForUser(user_id)

    if groupd_items:
        result = ""
        for event, master_classes in groupd_items.items():
            result += f"📅 {event.name}:\n\n"
            for master_class in master_classes:
                result += f"    🎯 {master_class.id}. {master_class.name}\n"
        
        result += "\nНапиши номер мастер-класса, чтобы получить подробную информацию"
        await callback_query.message.answer(result)
        await state.set_state(MasterClassStates.choosing)

    else:
        callback_query.message.answer("Вы не записаны ни на один мастер-класс")