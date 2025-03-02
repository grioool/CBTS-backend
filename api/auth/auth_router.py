from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from api.auth.auth_service import AuthServiceDep, oauth2_scheme
from api.user.dto.user_create import UserCreate
from api.user.dto.user_login import UserLogin
from api.user.dto.user_response import UserResponse
from config import auth_settings

router = APIRouter(prefix="/auth")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


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
    access_token_expires = timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/refresh")
def refresh_token(token: Annotated[str, Depends(oauth2_scheme)], auth_service: AuthServiceDep):
    payload = auth_service.decode_access_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    new_access_token = auth_service.create_access_token(data={"sub": username})
    return Token(access_token=new_access_token)
