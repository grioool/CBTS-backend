from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from api.user.entity.user import User
from db.config import SessionDep


class UserService:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_username(self, username: str) -> User:
        return self.session.exec(select(User).where(User.username == username)).first()

    def get_by_email(self, email: str) -> User:
        return self.session.exec(select(User).where(User.email == email)).first()

    def get_by_id(self, id: int) -> User:
        return self.session.exec(select(User).where(User.id == id)).first()


UserServiceDep = Annotated[UserService, Depends(UserService)]
