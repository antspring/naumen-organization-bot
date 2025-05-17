from aiogram import BaseMiddleware
from states import UserStates
from repositoreies import UserRepository
from aiogram.types import CallbackQuery, Message, Update

class UserLoaderMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Update):
            if event.callback_query:
                id = event.callback_query.from_user.id
            elif event.message:
                id = event.message.chat.id
        elif isinstance(event, CallbackQuery):
            if event.message:
                id = event.message.from_user_id
            else:
                await handler(event, data)
        elif isinstance(event, Message):
            id = event.chat.id
        else:
            return await handler(event, data)

        state = data['state']

        user_data = await state.get_data()
        if not user_data.get('user'):
            user = UserRepository.getUserById(id)
            await state.update_data(user=user)
            await state.set_state(UserStates.profile_loaded)
        
        
        return await handler(event, data)