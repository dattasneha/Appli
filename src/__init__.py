from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.auth.routes import router as auth_router
from src.jobs.admin_routes import router as admin_router
from src.jobs.user_routes import router as user_router
@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"Server is starting...")
    await init_db()
    yield
    print(f"Server has closed...")
version = "v1"

app = FastAPI(
    title="Appli",
    description="A job application portal for Appli",
    version= version,
    lifespan=life_span
)

app.include_router(auth_router,prefix=f"/appli/{version}")
app.include_router(admin_router,prefix=f"/appli/{version}")
app.include_router(user_router,prefix=f"/appli/{version}")


