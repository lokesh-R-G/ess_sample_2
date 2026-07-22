from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.attendance import router as attendance_router
from .api.routes.admin import router as admin_router
from .api.routes.dashboard import router as dashboard_router
from .api.routes.auth import router as auth_router
from .api.routes.health import router as health_router
from .api.routes.leave import router as leave_router
from .api.routes.payslip import router as payslip_router
from .api.routes.profile import router as profile_router
from .api.routes.sync import router as sync_router
from .api.routes.policy import router as policy_router
from .api.routes.organization import router as organization_router
from .api.routes.workflow import router as workflow_router
from .api.routes.miss_punch import router as miss_punch_router
from .core.config import get_settings
from .db.mongo import init_indexes
from .scheduler.scheduler import init_scheduler


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_indexes()
    # start APScheduler for background sync jobs
    init_scheduler()
    yield


app = FastAPI(title="IDS ESS & Payroll API", version="1.0.0", lifespan=lifespan)

# Configure CORS for local development. Do NOT use allow_origins=['*'] in production.
origins = settings.frontend_origins or [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(attendance_router, prefix="/api/v1")
app.include_router(leave_router, prefix="/api/v1")
app.include_router(payslip_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(sync_router, prefix="/api/v1")
app.include_router(policy_router, prefix="/api/v1")
app.include_router(organization_router, prefix="/api/v1")
app.include_router(workflow_router, prefix="/api/v1")
app.include_router(miss_punch_router, prefix="/api/v1")
