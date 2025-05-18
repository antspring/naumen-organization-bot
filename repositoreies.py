from db import session
from models import User, Role, Event, EventParticipants
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
    
    def getById(id):
        query = select(Event).where(Event.id == id)
        return session.scalar(query)
    
    def update(id, field_name, value):
        query = select(Event).where(Event.id == id)
        event = session.scalar(query)
        setattr(event, field_name, value)
        session.commit()
        return event

class EventParticipantsRepository():

    def getByEventIdAndUserId(event_id, user_id):
        query = select(EventParticipants).where(EventParticipants.event_id == event_id and EventParticipants.user_id == user_id)
        return session.scalar(query)
    
    def create(event_id, user_id):
        eventParticipants = EventParticipants(event_id=event_id, user_id=user_id)
        session.add(eventParticipants)
        session.commit()
    
    def delete(eventParticipants):
        session.delete(eventParticipants)
        session.commit()