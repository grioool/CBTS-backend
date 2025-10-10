from sqlmodel import SQLModel


class PasswordResetRequest(SQLModel):
    email: str