from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Ole Miss Virtual Academic Advisor",
    description="AI-powered academic advisor for Ole Miss CS students",
    version="0.1.0"
)

# Configure CORS
origins = [
    "http://localhost:3000", # Next.js Frontend
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Ole Miss Virtual Academic Advisor API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
