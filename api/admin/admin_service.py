from sqlalchemy import func
from sqlmodel import select

from api.summary.summary import Summary
from api.user.entity.user import User
from db.config import SessionDep


def count_users(session: SessionDep) -> int:
    result = session.execute(select(func.count(User.id)))
    total_users = result.scalar()
    return total_users


def count_summaries(session: SessionDep) -> int:
    result = session.execute(select(func.count(Summary.id)))
    total_summaries = result.scalar()
    return total_summaries
