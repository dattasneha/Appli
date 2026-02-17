from fastapi import APIRouter, HTTPException, status,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select,Field
from src.db.main import engine
from src.model import Job, UserRole
import uuid
from typing import Optional

class JobCreate(SQLModel):
    title: str
    description: str

from src.dependency import get_current_user
router = APIRouter()

class JobRead(SQLModel):
    id: uuid.UUID
    title: str
    description: str
    is_active: bool
    
@router.get("/jobs", response_model=list[JobRead])
async def list_jobs():
    async with AsyncSession(engine) as session:
        res = await session.execute(select(Job).where(Job.is_active == True))
        jobs = res.scalars().all()

    return jobs

@router.post("/jobs", status_code=status.HTTP_201_CREATED)
async def create_job(job: JobCreate, payload:dict=Depends(get_current_user)):
    role_in_token = payload["user"].get("role", "").strip().lower()
    if role_in_token != UserRole.ADMIN.value.lower():
        raise HTTPException(403, "Only admin can create jobs")
    job = Job(title=job.title, description=job.description, is_active=True)

    async with AsyncSession(engine) as session:
        session.add(job)
        await session.commit()
        await session.refresh(job)

    return job

