"""
FastAPI application main entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.database import Base, engine
from app.api import battles_router, verses_router, ratings_router, youtube_router, upload_router, semantic_router, mc_context_router


# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(battles_router.router, prefix="/api/battles", tags=["battles"])
app.include_router(youtube_router.router, prefix="/api/battles/youtube", tags=["youtube"])
app.include_router(upload_router.router, prefix="/api/battles/upload", tags=["upload"])
app.include_router(verses_router.router, prefix="/api/verses", tags=["verses"])
app.include_router(ratings_router.router, prefix="/api/ratings", tags=["ratings"])
app.include_router(semantic_router.router, prefix="/api/semantic", tags=["semantic"])  # Fase 3
app.include_router(mc_context_router.router, prefix="/api/mc", tags=["mc_context"])  # Fase 4

# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "Freestyle Callificator API"}
    )

# Root endpoint
@app.get("/")
async def root():
    return JSONResponse(
        status_code=200,
        content={
            "message": "Freestyle Callificator API",
            "version": settings.API_VERSION,
            "docs": "/docs",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
