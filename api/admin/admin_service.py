from sqlalchemy import func
from sqlmodel import select

from api.admin.analytic import Analytic
from api.user.user import User
from db.config import SessionDep


async def get_analytics_data(session: SessionDep) -> Analytic:
    statement = select(Analytic).order_by(Analytic.id.desc()).limit(1)
    result = session.exec(statement)
    return result.first()


async def count_users(session: SessionDep) -> int:
    result = session.execute(select(func.count(User.id)))
    total_users = result.scalar()
    return total_users
