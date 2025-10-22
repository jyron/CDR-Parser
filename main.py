from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CDR Parser API",
    description="API for parsing and storing Call Detail Records",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root redirect to dashboard
@app.get("/")
def root():
    """Redirect root to dashboard"""
    return RedirectResponse(url="/dashboard")


# Include API routes with /api prefix
app.include_router(router, prefix="/api")

# Mount frontend static files at /dashboard
app.mount("/dashboard", StaticFiles(directory="frontend", html=True), name="frontend")

