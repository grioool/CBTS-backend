from sqlmodel import SQLModel


class UserResponse(SQLModel):
    username: str
    email: str
