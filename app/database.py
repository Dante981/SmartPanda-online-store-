from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Строка подключения для SQLite
DATABASE_URL = "sqlite:///ecommerce.db"


# Создаём Engine
engine = create_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
SessionLocal = sessionmaker(bind=engine)


# --------------- Асинхронное подключение к PostgreSQL -------------------------

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Строка подключения для PostgreSQl
DATABASE_URL = settings.DATABASE_URL_ASYNC
# Создаём Engine
async_engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)

# Настраиваем фабрику сеансов
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass