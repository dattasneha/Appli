from fastapi import APIRouter, HTTPException, status,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select
from src.db.main import engine
from src.dependency import get_current_user
from src.model import Application, Job,ApplicationStatus
import uuid
from typing import Optional


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

@router.get("/jobs/{job_id}", response_model=JobRead)
async def get_job(job_id: uuid.UUID):
    async with AsyncSession(engine) as session:
        res = await session.execute(select(Job).where(Job.id == job_id, Job.is_active == True))
        job = res.scalars().first()

    if not job:
        raise HTTPException(404, "Job not found or not active")

    return job

@router.post("/jobs/apply/{job_id}", status_code=status.HTTP_200_OK)
async def apply_job(job_id: uuid.UUID, resume_url: str, cover_letter: Optional[str] = None, payload:dict=Depends(get_current_user)):
    user_id = uuid.UUID(str(payload["user"]["id"]))

    async with AsyncSession(engine) as session:
        res = await session.execute(select(Job).where(Job.id == job_id, Job.is_active == True))
        job = res.scalars().first()
        if not job:
            raise HTTPException(404, "Job not found or not active")

        application = Application(
            user_id=user_id,
            job_id=job_id,
            resume_url=resume_url,
            status=ApplicationStatus.SUBMITTED,
            cover_letter=cover_letter
        )
        session.add(application)
        await session.commit()
        await session.refresh(application)

    return {"message": "Application submitted successfully", "application_id": application.id, "status": application.status.value}

@router.get("/me/applications", status_code=status.HTTP_200_OK)
async def list_my_applications(payload:dict=Depends(get_current_user)):
    user_id = uuid.UUID(str(payload["user"]["id"]))

    async with AsyncSession(engine) as session:
        res = await session.execute(select(Application).where(Application.user_id == user_id))
        applications = res.scalars().all()

    return applications

@router.get("/me/applications/{application_id}", status_code=status.HTTP_200_OK)
async def get_my_application(application_id: uuid.UUID, payload:dict=Depends(get_current_user)):
    user_id = uuid.UUID(str(payload["user"]["id"]))

    async with AsyncSession(engine) as session:
        res = await session.execute(select(Application).where(Application.id == application_id, Application.user_id == user_id))
        application = res.scalars().first()

    if not application:
        raise HTTPException(404, "Application not found")

    return application
