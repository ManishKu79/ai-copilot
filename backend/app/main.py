from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import analysis, review, error, search, health, refactor, dependencies
from app.api.routes import commit
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
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(refactor.router, prefix="/api/refactor", tags=["refactor"])
app.include_router(dependencies.router, prefix="/api/dependencies", tags=["dependencies"])
app.include_router(commit.router, prefix="/api/commit", tags=["commit"])

@app.get("/")
async def root():
    return {"message": "AI Code Copilot API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}