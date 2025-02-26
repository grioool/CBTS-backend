from sqlmodel import SQLModel, Field


class Analytic(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    total_summaries: int
    total_users: int
