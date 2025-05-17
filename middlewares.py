from aiogram import BaseMiddleware
from states import UserStates
from repositoreies import UserRepository

class UserLoaderMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state = data['state']

        user_data = await state.get_data()
        if not user_data.get('user'):
            user = UserRepository.getUserById(event.message.chat.id)
            await state.update_data(user=user)
            await state.set_state(UserStates.profile_loaded)
            print('пользователь создан')
        
        return await handler(event, data)