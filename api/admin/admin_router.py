from fastapi import APIRouter, HTTPException

from api.admin.admin_service import get_analytics_data, count_users
from db.config import SessionDep

router = APIRouter()


@router.get("/admin/analytics")
async def get_admin_analytics(session: SessionDep):
    analytics_data = await get_analytics_data(session)
    total_users = await count_users(session)
    if analytics_data:
        return {
            "total_summaries": analytics_data.total_summaries,
            "total_users": total_users
        }
    else:
        raise HTTPException(status_code=404, detail="Analytics data not found")
