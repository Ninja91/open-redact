from src.models.database import Base
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at {DATABASE_URL}")

if __name__ == "__main__":
    init_db()
