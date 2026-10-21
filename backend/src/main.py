"""
CTMS Main Application Entry Point
Initializes FastAPI, attaches routes, middleware, and exception handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.api.routes import router

app = FastAPI(
    title="Cylinder Tracking Management System (CTMS)",
    description="Enterprise-grade ERP and asset-tracking platform for high-pressure gas cylinders with native Zoho ecosystem sync.",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.src.main:app", host="0.0.0.0", port=8000, reload=True)
