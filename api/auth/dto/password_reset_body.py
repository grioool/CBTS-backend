from sqlmodel import SQLModel


class PasswordResetBody(SQLModel):
    token: str
    new_password: str
