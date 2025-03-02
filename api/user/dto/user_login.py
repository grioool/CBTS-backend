from sqlmodel import SQLModel


class UserLogin(SQLModel):
    username: str
    password: str
