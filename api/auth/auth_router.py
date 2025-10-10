from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from api.auth.auth_service import AuthServiceDep, oauth2_scheme
from api.auth.dto.password_reset_body import PasswordResetBody
from api.auth.dto.password_reset_request import PasswordResetRequest
from api.auth.password_reset_token import PasswordResetToken
from api.user.dto.user_create import UserCreate
from api.user.dto.user_login import UserLogin
from api.user.dto.user_response import UserResponse
from config import auth_settings

router = APIRouter(prefix="/auth")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool


@router.post("/registration")
def register(user: UserCreate, auth_service: AuthServiceDep) -> UserResponse:
    if auth_service.user_exists(user):
        raise HTTPException(status_code=400, detail="Username or email already taken")
    auth_service.create_user(user)
    return user


@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], auth_service: AuthServiceDep) -> Token:
    user_login = UserLogin(username=form_data.username, password=form_data.password)
    user = auth_service.login(user_login)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    is_admin = user.role_id == 1

    access_token_expires = timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "is_admin": is_admin},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer", is_admin=is_admin)


@router.post("/refresh")
def refresh_token(token: Annotated[str, Depends(oauth2_scheme)], auth_service: AuthServiceDep):
    payload = auth_service.decode_access_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    new_access_token = auth_service.create_access_token(data={"sub": username})
    return Token(access_token=new_access_token)

@router.post("/password/forgot")
def forgot(body: PasswordResetRequest, auth_service: AuthServiceDep):
    auth_service.request_password_reset(body.email)
    a = PasswordResetToken()
    return {"message": "If that email exists, a reset link has been sent."}

@router.post("/password/reset")
def reset(body: PasswordResetBody, auth_service: AuthServiceDep):
    auth_service.reset_password(body.token, body.new_password)
    return {"message": "Password has been reset successfully."}
