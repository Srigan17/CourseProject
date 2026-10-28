import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.api.routes_status import router as status_router
from backend.app.api.routes_datasets import router as datasets_router
from backend.app.api.routes_fl import router as fl_router
from backend.app.api.routes_privacy import router as privacy_router
from backend.app.api.routes_fhir import router as fhir_router
from backend.app.api.routes_experiments import router as experiments_router
from backend.app.api.routes_security import router as security_router
from backend.app.api.routes_auth import router as auth_router
from backend.app.security.audit import audit_logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Privacy-Preserving Federated Learning for Healthcare Data with FHIR Interoperability, Differential Privacy, and Cryptographic Secure Aggregation."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
app.include_router(status_router, prefix=settings.API_PREFIX)
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(datasets_router, prefix=settings.API_PREFIX)
app.include_router(fl_router, prefix=settings.API_PREFIX)
app.include_router(privacy_router, prefix=settings.API_PREFIX)
app.include_router(fhir_router, prefix=settings.API_PREFIX)
app.include_router(experiments_router, prefix=settings.API_PREFIX)
app.include_router(security_router, prefix=settings.API_PREFIX)

@app.on_event("startup")
def on_startup():
    audit_logger.log_event(
        event_type="SYSTEM_STARTUP",
        severity="INFO",
        actor="SYSTEM",
        details={
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "port": 8000
        }
    )

# Mount reports directory for direct PDF/manuscript access
reports_dir = Path(__file__).resolve().parent.parent.parent / "reports"
if reports_dir.exists():
    app.mount("/reports", StaticFiles(directory=str(reports_dir)), name="reports")

# Mount frontend built static distribution if available
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "title": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs_url": "/docs",
            "api_status": f"{settings.API_PREFIX}/status"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
