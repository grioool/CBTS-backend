from fastapi import APIRouter, HTTPException

from api.admin.admin_service import count_summaries, count_users
from db.config import SessionDep

router = APIRouter()


@router.get("/admin/analytics")
async def get_admin_analytics(session: SessionDep):
    total_summaries = await count_summaries(session)
    total_users = await count_users(session)
    if total_summaries is not None and total_users is not None:
        return {
            "total_summaries": total_summaries,
            "total_users": total_users
        }
    else:
        raise HTTPException(status_code=404, detail="Analytics data not found")
