import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Получение URL базы данных из переменных окружения
DATABASE_URL = "postgresql://shop_user_2024:8Dm!Kp2%40vF9zLq@localhost:5432/telegram_shop_db"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()