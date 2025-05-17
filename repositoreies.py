from db import session
from models import User, Role
from sqlalchemy import select
from sqlalchemy.orm import joinedload

class UserRepository():

    def getUserById(telegram_id):
        query = select(User).options(joinedload(User.role)).where(User.telegram_id == telegram_id)
        return session.scalar(query)
    

    def createUser(telegram_id, full_name):
        user = User(telegram_id=telegram_id, full_name=full_name, role_id=Role.PARTICIPANT)
        session.add(user)
        session.commit()