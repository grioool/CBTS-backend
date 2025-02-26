from fastapi import APIRouter, HTTPException

from api.admin.admin_service import get_analytics_data
from db.config import SessionDep

router = APIRouter()


@router.get("/admin/analytics")
async def get_admin_analytics(session: SessionDep):
    analytics_data = await get_analytics_data(session)
    if analytics_data:
        return {
            "total_summaries": analytics_data.total_summaries,
            "total_users": analytics_data.total_users
        }
    else:
        raise HTTPException(status_code=404, detail="Analytics data not found")
