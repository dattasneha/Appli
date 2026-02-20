import re

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.auth.util import ACCESS_TOKEN_EXPIRY, create_access_token, verify_password, hash_password
from src.db.main import engine
from src.model import User,UserRole
from pydantic import BaseModel
from sqlalchemy.orm import selectinload 
from fastapi import Response

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str   
    password: str
    role: str

router = APIRouter()

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#$%^&+=]{2,}$')


@router.post("/login")
async def login(payload: LoginRequest,response: Response):

    email = payload.email
    password = payload.password

    async with AsyncSession(engine) as session:
        res = await session.execute(
            select(User)
            .options(selectinload(User.applications))
            .where(User.email == email)
        )
        user = res.scalars().first()

    if not user:
        raise HTTPException(401, "Email not found")

    try:
        if not verify_password(password, user.hashed_password):
            raise HTTPException(401, "Wrong password")
    except Exception as e:
        raise HTTPException(500, f"Password verification failed: {str(e)}")

    try:
        token = create_access_token({
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value
        })
        response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax",max_age=ACCESS_TOKEN_EXPIRY)
    except Exception as e:
        raise HTTPException(500, f"Token crash: {str(e)}")
    sanitized_user = {
        "id": str(user.id), 
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "Applications": user.applications
    }
    return {"access_token": token,"user":sanitized_user}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):

    name = payload.name
    email = payload.email
    password = payload.password
    role = payload.role

    if not name or not name.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required")
    if not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
    if not PASSWORD_REGEX.match(password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password does not meet complexity requirements")

    async with AsyncSession(engine) as session:
        q = select(User).where(User.email == email)
        res = await session.execute(q)
        existing = res.scalars().first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        new_user = User(
            name=name.strip(),
            email=email,
            hashed_password=hash_password(password),
            role=role.lower()
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

    return {
        "message": f"User registered with role {new_user.role}",
        "id": str(new_user.id),
        "email": new_user.email,
        "name": new_user.name,
        "role": new_user.role
    }
