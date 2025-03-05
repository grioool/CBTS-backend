from fastapi import APIRouter, HTTPException, Depends

from api.admin.admin_service import count_summaries, count_users
from api.auth.auth_service import oauth2_scheme, AuthServiceDep
from db.config import SessionDep

router = APIRouter()


@router.get("/admin/analytics")
async def get_admin_analytics(auth_service: AuthServiceDep, session: SessionDep, token: str = Depends(oauth2_scheme)):
    current_user = await auth_service.get_current_user(token)
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Not authorized")

    total_summaries = await count_summaries(session)
    total_users = await count_users(session)

    if total_summaries is not None and total_users is not None:
        return {
            "total_summaries": total_summaries,
            "total_users": total_users,
            "is_admin": True
        }
    else:
        raise HTTPException(status_code=404, detail="Analytics data not found")
