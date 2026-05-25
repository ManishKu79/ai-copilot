from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import analysis, review, error

app = FastAPI(title="AI Code Copilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(review.router, prefix="/api/review", tags=["review"])
app.include_router(error.router, prefix="/api/error", tags=["error"])

@app.get("/")
async def root():
    return {"message": "AI Code Copilot API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}