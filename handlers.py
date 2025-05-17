from aiogram import Router
from aiogram.filters import Command
from states import UserStates
from repositoreies import UserRepository

router = Router(name=__name__)

@router.message(Command("start"))
async def start_command_handler(message, state):
    await state.set_state(UserStates.registration)
    await message.answer('Напиши свое имя')


@router.message(UserStates.registration)
async def registration_handler(message, state):
    await state.clear()
    user = UserRepository.getUserById(message.chat.id)
    if not user:
        user = UserRepository.createUser(message.chat.id, message.text)
        await message.answer('Ты создан')
    else:
        await message.answer('Ты уже есть')