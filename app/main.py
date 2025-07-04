from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="FastAPI Auth System",
    description="A secure authentication system with OAuth2 and JWT tokens",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

# Set all CORS enabled origins
if settings.ENVIRONMENT == "development":
    origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080",
    ]
else:
    origins = []  # Add your production domains here

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "FastAPI Auth System API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}