from aiogram import Router
from aiogram.filters import Command
from states import UserStates
from repositoreies import UserRepository

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

🔹 Ваш текущий статус: {user.role.name}''')
    
    await state.clear()