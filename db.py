import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, User, Role


engine = create_engine("sqlite:///bot.db", echo=True)
session = Session(engine)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    from main import parse_args
    args = parse_args()

    if  args.seed:
        roles = [Role(name="admin"), Role(name="organizator"), Role(name="participant")]
        user = User(telegram_id=os.getenv('ADMIN_ID'), full_name="administrator", role=roles[0])

        session.add_all(roles)
        session.add(user)

        session.commit()