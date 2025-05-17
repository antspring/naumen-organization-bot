from models import User, Role
from db import session
from sqlalchemy import select
from sqlalchemy.orm import joinedload

# role = Role(name="admin")
# user = User(telegram_id=2342, full_name="a;lskjdf", role_id=1)

# session.add_all([role, user])

# session.commit()

# stmt = select(User).options(joinedload(User.role)).where(User.telegram_id == 2342)
