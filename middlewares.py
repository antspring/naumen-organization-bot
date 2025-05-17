from aiogram import BaseMiddleware
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models import User
from db import session
from states import UserStates

class UserLoaderMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state = data['state']

        user_data = await state.get_data()
        if not user_data.get('user'):
            query = select(User).options(joinedload(User.role)).where(User.telegram_id == event.message.chat.id)
            user = session.scalar(query)
            await state.update_data(user=user)
            await state.set_state(UserStates.profile_loaded)
        
        return await handler(event, data)