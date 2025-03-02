from typing import Annotated

from fastapi import APIRouter, Depends

from api.auth.auth_service import oauth2_scheme, AuthServiceDep
from api.summary.summary_service import SummaryServiceDep

router = APIRouter()


@router.get("/user/history")
async def get_history(token: Annotated[str, Depends(oauth2_scheme)], auth_service: AuthServiceDep,
                      summary_service: SummaryServiceDep):
    user = await auth_service.get_current_user(token)
    summaries = summary_service.get_all_user_summaries(user.id)
    return summaries
