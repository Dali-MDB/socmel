from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]





