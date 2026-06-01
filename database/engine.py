from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import settings

# Створення двигуна
engine = create_async_engine(
    url=settings.database_url,
    echo=False
)

# Створення сесій
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Функція для отримання сесій
async def get_session():
    async with async_session() as session:
        yield session
