from db import session
from models import User, Role, Event
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

class UserRepository():

    def getUserById(id):
        query = select(User).options(joinedload(User.role)).where(User.id == id)
        return session.scalar(query)
    

    def createUser(id, full_name):
        user = User(id=id, full_name=full_name, role_id=Role.PARTICIPANT)
        session.add(user)
        session.commit()


class EventRepository():
    
    def create(event):
        session.add(event)
        session.commit()
    
    def getActual():
        query = select(Event).where(Event.end_time > datetime.now(timezone.utc))
        return session.execute(query).scalars().all()