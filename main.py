"""
FastAPI application entry point.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers.pdf_router import router as pdf_router
from app.utils.exceptions import InvalidPdfRequestException, ProblemDetailException

logger = logging.getLogger(__name__)

SERVICE_NAME = "extract-service"
SERVICE_PORT = 5000


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle — startup and shutdown."""
    # Startup — register with Consul
    logger.info("Starting Extract Service...")
    from app.consul_registration import register_service, deregister_service, fetch_kv_config

    # Load config from Consul KV
    kv_config = fetch_kv_config(SERVICE_NAME)
    global SERVICE_PORT
    if "PORT" in kv_config:
        SERVICE_PORT = int(kv_config["PORT"])

    # Register — tags are read from Consul KV automatically (no hardcoded labels)
    register_service(
        service_name=SERVICE_NAME,
        service_port=SERVICE_PORT,
        health_check_path="/health",
    )
    logger.info("✓ Extract Service ready")

    yield

    # Shutdown — deregister from Consul
    deregister_service(SERVICE_NAME, SERVICE_PORT)
    logger.info("Shutting down Extract Service...")


app = FastAPI(
    title="Extract Text Service",
    version="1.0.0",
    description="Service that decodes Base64 PDF content and extracts text from it.",
    lifespan=lifespan,
)

# CORS - allow all origins for microservice communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_router)


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "extract-service",
        "version": "1.0.0",
    }


@app.get("/ready", tags=["health"])
async def readiness():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "service": "extract-service",
    }


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Extract Text Service API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.exception_handler(ProblemDetailException)
async def problem_detail_exception_handler(
    _request: Request,
    exc: ProblemDetailException,
) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content=exc.to_dict())


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    detail = "; ".join(error["msg"] for error in exc.errors())
    problem = InvalidPdfRequestException(detail=detail)
    return JSONResponse(status_code=problem.status, content=problem.to_dict())


def main() -> None:
    print("Extract Text Service is configured.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
