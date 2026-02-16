from sqlmodel import create_engine,SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import Config

engine = AsyncEngine(
    create_engine(
        url = Config.DATABASE_URL,
        echo=True
    )
)

async def init_db():
    async with engine.begin() as conn:
        from src.model import User, Job, Application, ApplicationStatusHistory

        await conn.run_sync(SQLModel.metadata.create_all)