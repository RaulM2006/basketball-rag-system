import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from api.routes import router as coaching_router

# Load environment variables on startup
load_dotenv()

app = FastAPI(
    title="Basketball Multimodal RAG Coaching API",
    description=(
        "FastAPI service that accepts user jump shot videos, analyzes them "
        "using Gemini multimodal vision, queries a local ChromaDB vector store "
        "for professional shooting coaching drills, and synthesizes timestamped "
        "drill guides."
    ),
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local testing
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include the coaching route module
app.include_router(coaching_router, prefix="/api")

# Mount the static directory to serve HTML/CSS/JS frontend assets
# Note: The directory must exist on disk when the application starts
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    """Serves the main static index.html dashboard at the root URL."""
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    """Basic health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "api_version": "1.0.0"
    }

