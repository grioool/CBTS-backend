from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from config import db_settings

engine = (create_engine(
    f"postgresql://{db_settings.DB_USER}:{db_settings.DB_PASSWORD}@{db_settings.DB_IP}:5432/{db_settings.DB_NAME}"))


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("created")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
