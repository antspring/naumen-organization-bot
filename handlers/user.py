from aiogram import Router
from aiogram.filters import Command
from states import UserStates
from repositoreies import UserRepository
from models import Role
from handlers.menu import main_menu_message


router = Router(name=__name__)


@router.message(Command("start"))
async def start_command_handler(message, state):
    await state.set_state(UserStates.registration)
    await message.answer('''👋 Привет!  

📌 Чтобы начать, выбери мероприятие и зарегистрируйся. 
🤝Укажи свое имя и фамилию. 

🔹 После регистрации ты получишь:  
✔️ Доступ к расписанию  
✔️ Возможность записываться на мастер-классы  
✔️ Уведомления о важных событиях''')


@router.message(UserStates.registration)
async def registration_handler(message, state):
    user = UserRepository.getUserById(message.chat.id)
    if not user:
        user = UserRepository.createUser(message.chat.id, message.text)
    else:
        await message.answer(f'''ℹ️ Вы уже зарегистрированы!  

Похоже, вы уже завершили регистрацию.  

🔹 Ваш текущий статус: {Role.NAMES[user.role.name]}''')
        await main_menu_message(message)

    await state.clear()


@router.message(Command("set_organizator"))
async def set_organizator(message):
    try:
        args = message.text.split()

        if len(args) < 2:
            await message.answer("Введите ID вместе с командой")
            return

        user_id = int(args[1])
        UserRepository.makeOrganizator(user_id)
        await message.answer("Пользователь теперь организатор")
    except:
        await message.answer("Такого пользователя нет")


@router.message(Command("set_admin"))
async def set_organizator(message):
    try:
        args = message.text.split()

        if len(args) < 2:
            await message.answer("Введите ID вместе с командой")
            return

        user_id = int(args[1])
        UserRepository.makeAdmin(user_id)
        await message.answer("Пользователь теперь администратор")
    except:
        await message.answer("Такого пользователя нет")
