from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlmodel import select, SQLModel

from api.user.dto.user_create import UserCreate
from api.user.dto.user_login import UserLogin
from api.user.entity.user import User
from api.user.user_service import UserServiceDep
from config import auth_settings
from db.config import SessionDep

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class TokenData(SQLModel):
    username: str | None = None

class AuthService:
    def __init__(self, session: SessionDep, user_service: UserServiceDep):
        self.session = session
        self.user_service = user_service

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    def user_exists(self, user: UserCreate):
        statement = select(User).where(User.username == user.username or User.email == user.email)
        existing = self.session.exec(statement).first()
        return existing is not None

    def create_user(self, user: UserCreate):
        user.password = self.get_password_hash(user.password)
        db_user = User.model_validate(user)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return user

    def login(self, user: UserLogin) -> User | None:
        db_user = self.user_service.get_by_username(user.username)
        if not db_user:
            return None
        if not self.verify_password(user.password, self.get_password_hash(user.password)):
            return None
        return db_user


    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str):
        try:
            payload = jwt.decode(token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except InvalidTokenError:
            raise credentials_exception
        user = self.user_service.get_by_username(token_data.username)
        if user is None:
            raise credentials_exception
        return user

AuthServiceDep = Annotated[AuthService, Depends(AuthService)]
