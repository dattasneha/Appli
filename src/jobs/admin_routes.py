from fastapi import APIRouter, HTTPException, status,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select
from src.db.main import engine
from src.model import Job, UserRole,Application,ApplicationStatus
import uuid
from typing import Optional
from src.dependency import get_current_user

router = APIRouter()

class JobCreate(SQLModel):
    title: str
    description: str
    is_active: Optional[bool] = True

@router.post("/admin/jobs", status_code=status.HTTP_201_CREATED)
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

@router.delete("/admin/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: uuid.UUID, payload:dict=Depends(get_current_user)):
    role_in_token = payload["user"]["role"].lower()
    if role_in_token != UserRole.ADMIN.value.lower():
        raise HTTPException(403, "Only admin can delete jobs")

    async with AsyncSession(engine) as session:
        res = await session.execute(select(Job).where(Job.id == job_id))
        job = res.scalars().first()
        if not job:
            raise HTTPException(404, "Job not found")

        await session.delete(job)
        await session.commit()

    return

@router.patch("/admin/jobs/{job_id}/status", status_code=status.HTTP_200_OK)
async def change_job_status(job_id: uuid.UUID, is_active: bool, payload:dict =Depends(get_current_user)):
    role_in_token = payload["user"]["role"].lower()
    if role_in_token != UserRole.ADMIN.value.lower():
        raise HTTPException(403, "Only admin can change job status")

    async with AsyncSession(engine) as session:
        res = await session.execute(select(Job).where(Job.id == job_id))
        job = res.scalars().first()
        if not job:
            raise HTTPException(404, "Job not found")

        job.is_active = is_active
        await session.commit()
        await session.refresh(job)

    return job


@router.get("/admin/application", status_code=status.HTTP_200_OK)
async def list_all_applications(payload: dict = Depends(get_current_user)):
    role_in_token = payload["user"]["role"].lower()
    if role_in_token != UserRole.ADMIN.value.lower():
        raise HTTPException(403, "Only admin can view all applications")

    async with AsyncSession(engine) as session:
        res = await session.execute(select(Application))
        applications = res.scalars().all()

    return applications

@router.get("/admin/application/{application_id}", response_model=Application)
async def get_application(application_id: uuid.UUID, payload:dict=Depends(get_current_user)):    
    role_in_token = payload["user"]["role"].lower()
    if role_in_token != UserRole.ADMIN.value.lower():
        raise HTTPException(403, "Only admin can view application details")

    async with AsyncSession(engine) as session:
        res = await session.execute(select(Application).where(Application.id == application_id))
        application = res.scalars().first()

    if not application:
        raise HTTPException(404, "Application not found")

    return application

@router.patch("/admin/application/{application_id}/status", status_code=status.HTTP_200_OK)
async def change_application_status(application_id: uuid.UUID, status: str, payload:dict=Depends(get_current_user)):
    role_in_token = payload["user"]["role"].lower()
    if role_in_token != UserRole.ADMIN.value.lower():
        raise HTTPException(403, "Only admin can change application status")

    async with AsyncSession(engine) as session:
        res = await session.execute(select(Application).where(Application.id == application_id))
        application = res.scalars().first()
        if not application:
            raise HTTPException(404, "Application not found")

        try:
            application.status = status
            await session.commit()
            await session.refresh(application)
        except Exception as e:
            raise HTTPException(400, f"Invalid status value: {str(e)}")

    return application

