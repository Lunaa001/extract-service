"""
FastAPI application entry point.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers.pdf_router import router as pdf_router
from app.utils.exceptions import InvalidPdfRequestException, ProblemDetailException


app = FastAPI(
    title="Extract Text Service",
    version="1.0.0",
    description="Service that decodes Base64 PDF content and extracts text from it.",
)

app.include_router(pdf_router)


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
    main()
