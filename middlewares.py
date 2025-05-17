from aiogram import BaseMiddleware
from states import UserStates
from repositoreies import UserRepository
from aiogram.types import CallbackQuery, Message

class UserLoaderMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, CallbackQuery):
            chat_id = event.message.chat.id
        elif isinstance(event, Message):
            chat_id = event.chat.id
        else:
            return await handler(event, data)
        
        state = data['state']

        user_data = await state.get_data()
        if not user_data.get('user'):
            user = UserRepository.getUserById(chat_id)
            await state.update_data(user=user)
            await state.set_state(UserStates.profile_loaded)
        
        return await handler(event, data)