from sqlmodel import select

from api.admin.analytic import Analytic
from db.config import SessionDep


async def get_analytics_data(session: SessionDep) -> Analytic:
    statement = select(Analytic).order_by(Analytic.id.desc()).limit(1)
    result = session.exec(statement)
    return result.first()
