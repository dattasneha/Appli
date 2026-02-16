import re

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.auth.util import create_access_token, verify_password, hash_password
from src.db.main import engine
from src.model import User

router = APIRouter()

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#$%^&+=]{8,}$')


@router.post("/login")
async def login(email: str, password: str):

	if not EMAIL_REGEX.match(email):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
	if not PASSWORD_REGEX.match(password):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password does not meet complexity requirements")

	async with AsyncSession(engine) as session:
		q = select(User).where(User.email == email)
		res = await session.execute(q)
		user = res.scalars().first()

	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

	if not verify_password(password, user.hashed_password):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

	token = create_access_token({"id": str(user.id), "email": user.email, "role": user.role})
	return {"message": "Login successful", "access_token": token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(name: str, email: str, password: str):
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

		new_user = User(name=name.strip(), email=email, hashed_password=hash_password(password))
		session.add(new_user)
		await session.commit()
		await session.refresh(new_user)
			

	return {"message": "User registered", "id": str(new_user.id), "email": new_user.email}


	
		