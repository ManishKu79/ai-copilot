from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.refactor_engine import RefactorEngine

router = APIRouter()
refactor_engine = RefactorEngine()

class RefactorRequest(BaseModel):
    code: str
    language: str = "python"
    file_path: Optional[str] = ""

class RepositoryRefactorRequest(BaseModel):
    files: List[Dict[str, Any]]

@router.post("/analyze")
async def analyze_refactors(request: RefactorRequest):
    """Analyze code for refactoring opportunities"""
    if not request.code or len(request.code.strip()) == 0:
        raise HTTPException(status_code=400, detail="No code provided")
    
    try:
        suggestions = refactor_engine.analyze_code(
            request.code,
            request.file_path,
            request.language
        )
        
        return {
            "success": True,
            "suggestions": suggestions,
            "total_found": len(suggestions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-repository")
async def analyze_repository_refactors(request: RepositoryRefactorRequest):
    """Analyze entire repository for refactoring opportunities"""
    if not request.files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    try:
        result = refactor_engine.analyze_repository_refactors(request.files)
        
        return {
            "success": True,
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository analysis failed: {str(e)}")