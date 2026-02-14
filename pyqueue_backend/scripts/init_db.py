import database.models
from database.base import Base
from database.engine import engine
from database.session import SessionLocal

Base.metadata.create_all(bind=engine)
