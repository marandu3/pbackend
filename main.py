import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
import uvicorn

from core.config import get_settings
from core.limiter import limiter
from routes.profile import router as profile_router, migrate_legacy_profile
from routes.education import router as education_router
from routes.skill import router as skill_router
from routes.timeline import router as timeline_router
from routes.project import router as project_router, migrate_project_slugs
from routes.user import router as user_router
from database.config import client, user_collection, project_collection

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("portfolio")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Portfolio API (environment=%s)", settings.environment)
    logger.info("Allowed CORS origins: %s", settings.cors_origins)

    try:
        client.admin.command("ping")
        logger.info("Connected to MongoDB.")
    except Exception:
        logger.exception("Could not reach MongoDB at startup.")

    try:
        user_collection.create_index("username", unique=True)
        migrate_legacy_profile()
        migrate_project_slugs()
        project_collection.create_index("slug", unique=True)
    except Exception:
        logger.exception("Startup maintenance (indexes/migration) failed.")

    yield


app = FastAPI(
    title="Portfolio API",
    description="Backend for the personal portfolio site: profile, education, skills, projects and timeline content, behind JWT-authenticated admin CRUD endpoints.",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again shortly."})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router, tags=["profile"])
app.include_router(education_router, tags=["education"])
app.include_router(skill_router, tags=["skills"])
app.include_router(timeline_router, tags=["timeline"])
app.include_router(project_router, tags=["projects"])
app.include_router(user_router, tags=["auth"])


@app.get("/", tags=["health"], summary="Liveness check")
async def root():
    return {"status": "ok", "service": "portfolio-api"}


@app.get("/health/db", tags=["health"], summary="Database connectivity check")
async def health_db():
    try:
        client.admin.command("ping")
        return {"status": "ok", "database": "connected"}
    except Exception:
        logger.exception("Health check: database unreachable.")
        return JSONResponse(status_code=503, content={"status": "error", "database": "unreachable"})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
