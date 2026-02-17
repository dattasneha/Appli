from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import Config

engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True
)

async def init_db():
    async with engine.begin() as conn:
        from src.model import User, Job, Application, ApplicationStatusHistory

        await conn.run_sync(SQLModel.metadata.create_all)