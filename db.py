import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_HOST = os.getenv("DB_HOST", "mysql")
DB_NAME = os.getenv("DB_NAME", "cruddb")
DB_USER = os.getenv("DB_USER", "cruduser")
DB_PASS = os.getenv("DB_PASS", "crudpass")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # kopan bağlantıları otomatik yenile
    future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
