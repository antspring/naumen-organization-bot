from db import session
from models import User, Role, Event, EventParticipants, MasterClass
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone


class UserRepository():

    def getUserById(id):
        query = select(User).options(
            joinedload(User.role)).where(User.id == id)
        return session.scalar(query)

    def createUser(id, full_name):
        user = User(id=id, full_name=full_name, role_id=Role.PARTICIPANT)
        session.add(user)
        session.commit()

    def getEvents(id):
        query = select(Event).join(EventParticipants).where(
            EventParticipants.user_id == id).order_by(Event.start_time)
        result = session.execute(query)
        return result.scalars().all()

    def makeOrganizator(id):
        query = select(User).where(User.id == id)
        user = session.scalar(query)
        user.role_id = Role.ORGANIZATOR
        session.commit()

    def makeAdmin(id):
        query = select(User).where(User.id == id)
        user = session.scalar(query)
        user.role_id = Role.ADMIN
        session.commit()


class EventRepository():

    def create(event):
        session.add(event)
        session.commit()

    def getActual():
        query = select(Event).where(
            Event.end_time > datetime.now(timezone.utc))
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

    def delete(id):
        query = delete(Event).where(Event.id == id)
        session.execute(query)


class EventParticipantsRepository():

    def getByEventIdAndUserId(event_id, user_id):
        query = select(EventParticipants).where(
            EventParticipants.event_id == event_id and EventParticipants.user_id == user_id)
        return session.scalar(query)

    def create(event_id, user_id):
        eventParticipants = EventParticipants(
            event_id=event_id, user_id=user_id)
        session.add(eventParticipants)
        session.commit()

    def delete(eventParticipants):
        session.delete(eventParticipants)
        session.commit()


class MasterClassRepository():

    def create(masterclass):
        session.add(masterclass)
        session.commit()

    def getByEventId(event_id):
        query = select(MasterClass).where(MasterClass.event_id == event_id)
        return session.execute(query).scalars().all()

    def getById(id):
        query = select(MasterClass).where(MasterClass.id == id)
        return session.scalar(query)

    def delete(id):
        query = delete(MasterClass).where(MasterClass.id == id)
        session.execute(query)
